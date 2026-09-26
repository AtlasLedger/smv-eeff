"""Cliente SOAP 1.1 para el servicio de datos abiertos de estados financieros de la SMV.

Decisiones de diseño:
- Se devuelve el XML CRUDO (bytes), sin decodificar a texto. La data de la SMV ya
  trae el encoding roto de forma inconsistente; si aquí se decodifica mal, se suma
  una segunda capa de corrupción imposible de separar de la original. El parseo
  se hace desde los bytes, respetando la declaración de encoding del propio XML.
- Reintentos con backoff exponencial y jitter solo ante errores transitorios
  (timeouts, conexión caída, HTTP 5xx). Un 4xx es un error nuestro: no se reintenta.
- Timeout de lectura generoso: una respuesta de 5 MB tarda ~8 s en condiciones
  normales, pero un servidor estatal puede tardar mucho más en horas pico.
"""
from __future__ import annotations

import json
import logging
import random
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from xml.sax.saxutils import escape

import requests

log = logging.getLogger(__name__)

HOST_POR_DEFECTO = "https://mvnet.smv.gob.pe"  # el host www.smv.gob.pe devuelve 500
RUTA = "/ws_od_eeff/WebServiceInfoFinanciera.asmx"
NS_TEMPURI = "http://tempuri.org/"
NS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"

# Alias cortos -> nombre real de la operación (con el typo "Gancia" original de la SMV)
OPERACIONES = {
    "balance": "obtener_BalanceGeneral",
    "resultados": "obtener_GanciaPerdida",
    "flujo": "obtener_FlujoEfectivo",
    "patrimonio": "obtener_CambiosPatrimonio",
    "integrales": "obtener_ResultadosIntegrales",
    "indice": "obtener_InfoFinanciera",
    "efdata": "obtener_EFData",
}
PERIODOS = ("A", "1", "2", "3", "4")
TIPOS = ("I", "C")


class ErrorSMV(Exception):
    """Error al consultar o interpretar el servicio."""


class ErrorPermanente(ErrorSMV):
    """Error que no tiene sentido reintentar (parámetros inválidos, 4xx)."""


@dataclass
class Respuesta:
    operacion: str
    ejercicio: int
    periodo: str
    tipo: str
    contenido: bytes  # XML crudo, tal cual llegó
    status: int
    segundos: float
    intentos: int


def resolver_operacion(nombre: str) -> str:
    """Acepta el alias ('resultados') o el nombre real ('obtener_GanciaPerdida')."""
    if nombre in OPERACIONES:
        return OPERACIONES[nombre]
    if nombre in OPERACIONES.values():
        return nombre
    raise ErrorPermanente(
        f"Operación desconocida: {nombre!r}. Opciones: {', '.join(OPERACIONES)}"
    )


def construir_sobre(operacion: str, ejercicio: int, periodo: str, tipo: str) -> bytes:
    parametros = {"Ejercicio": ejercicio, "Periodo": periodo, "Tipo": tipo}
    nodos = "".join(f"<{k}>{escape(str(v))}</{k}>" for k, v in parametros.items())
    sobre = (
        '<?xml version="1.0" encoding="utf-8"?>'
        f'<soap:Envelope xmlns:soap="{NS_SOAP}">'
        "<soap:Body>"
        f'<{operacion} xmlns="{NS_TEMPURI}">{nodos}</{operacion}>'
        "</soap:Body>"
        "</soap:Envelope>"
    )
    return sobre.encode("utf-8")


def extraer_fault(contenido: bytes) -> str:
    """Intenta leer el mensaje de un SOAP Fault; si no puede, devuelve el inicio del cuerpo."""
    try:
        raiz = ET.fromstring(contenido)
        for el in raiz.iter():
            if el.tag.endswith("faultstring"):
                return (el.text or "").strip()
    except ET.ParseError:
        pass
    return contenido[:300].decode("utf-8", errors="replace")


def extraer_registros(contenido: bytes, operacion: str) -> list[dict]:
    """Parsea el XML y convierte el JSON que viene como texto dentro de <operacionResult>.

    Lanza ErrorSMV si la respuesta no tiene la forma esperada. Esto se usa ANTES de
    guardar en caché: una respuesta que no parsea nunca se cachea.
    """
    try:
        raiz = ET.fromstring(contenido)
    except ET.ParseError as e:
        raise ErrorSMV(f"La respuesta no es XML válido: {e}") from e

    buscado = f"{operacion}Result"
    nodo = next(
        (el for el in raiz.iter() if el.tag == buscado or el.tag.endswith("}" + buscado)),
        None,
    )
    if nodo is None:
        raise ErrorSMV(f"No se encontró el nodo <{buscado}> en la respuesta")

    texto = (nodo.text or "").strip()
    if not texto:
        return []  # período sin datos: respuesta válida pero vacía

    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ErrorSMV(f"El contenido de <{buscado}> no es JSON válido: {e}") from e

    if datos is None:
        return []
    if isinstance(datos, dict):
        # Por si el servicio envuelve la lista en una clave (no visto aún, pero posible)
        listas = [v for v in datos.values() if isinstance(v, list)]
        datos = listas[0] if len(listas) == 1 else [datos]
    if not isinstance(datos, list):
        raise ErrorSMV(f"Se esperaba una lista de registros, llegó {type(datos).__name__}")
    return datos


class ClienteSMV:
    def __init__(
        self,
        host: str = HOST_POR_DEFECTO,
        timeout_conexion: float = 15,
        timeout_lectura: float = 180,
        max_intentos: int = 5,
        backoff_base: float = 4,
        backoff_max: float = 120,
    ):
        self.url = host.rstrip("/") + RUTA
        self.timeout = (timeout_conexion, timeout_lectura)
        self.max_intentos = max_intentos
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.sesion = requests.Session()  # reutiliza la conexión TLS entre llamadas
        self.sesion.headers["User-Agent"] = "smv-eeff (base de datos abierta; uso academico)"

    def _espera(self, intento: int) -> float:
        # Backoff exponencial con jitter: 4 s, 8 s, 16 s... +-50 %, tope en backoff_max.
        # El jitter evita que varias ejecuciones reintenten exactamente al mismo tiempo.
        base = min(self.backoff_base * 2 ** (intento - 1), self.backoff_max)
        return base * random.uniform(0.5, 1.5)

    def consultar(self, operacion: str, ejercicio: int, periodo: str, tipo: str) -> Respuesta:
        operacion = resolver_operacion(operacion)
        periodo, tipo = str(periodo).upper(), str(tipo).upper()
        if periodo not in PERIODOS:
            raise ErrorPermanente(f"Periodo inválido {periodo!r}; usar {PERIODOS}")
        if tipo not in TIPOS:
            raise ErrorPermanente(f"Tipo inválido {tipo!r}; usar {TIPOS}")

        cuerpo = construir_sobre(operacion, ejercicio, periodo, tipo)
        cabeceras = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f'"{NS_TEMPURI}{operacion}"',
        }
        ultimo_error: Exception | None = None

        for intento in range(1, self.max_intentos + 1):
            t0 = time.monotonic()
            try:
                r = self.sesion.post(self.url, data=cuerpo, headers=cabeceras, timeout=self.timeout)
            except (requests.ConnectionError, requests.Timeout) as e:
                ultimo_error = ErrorSMV(f"{type(e).__name__}: {e}")
            else:
                segundos = time.monotonic() - t0
                if r.status_code == 200:
                    return Respuesta(operacion, ejercicio, periodo, tipo,
                                     r.content, r.status_code, segundos, intento)
                detalle = extraer_fault(r.content)
                if 400 <= r.status_code < 500:
                    raise ErrorPermanente(f"HTTP {r.status_code}: {detalle}")
                ultimo_error = ErrorSMV(f"HTTP {r.status_code}: {detalle}")

            if intento < self.max_intentos:
                espera = self._espera(intento)
                log.warning("%s %s-%s-%s intento %d/%d falló (%s). Reintento en %.1f s",
                            operacion, ejercicio, periodo, tipo, intento,
                            self.max_intentos, ultimo_error, espera)
                time.sleep(espera)

        raise ErrorSMV(f"Falló tras {self.max_intentos} intentos: {ultimo_error}")
