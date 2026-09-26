"""Caché en disco de las respuestas crudas del servicio.

Decisiones de diseño:
- Se guarda el XML CRUDO comprimido (gzip), no la data ya parseada. Si mañana se
  mejora el parser o la limpieza, se reprocesa todo sin volver a llamar a la SMV.
  Además, el crudo es la evidencia de qué entregó la fuente (útil para la validación
  y para defender la base si alguien pregunta de dónde sale un número).
- Escritura atómica (archivo temporal + os.replace): si el proceso se corta a mitad
  de una escritura, no queda un archivo corrupto que después se lea como válido.
- Solo se cachea lo que PARSEA. Una página de error con HTTP 200 no entra al caché.
- Las respuestas vacías también se cachean (un 2001 consolidado sin datos es un
  resultado real), pero marcadas como vacías en el metadato.
- Cada archivo tiene un .json al lado con fecha de descarga, tamaño, hash SHA-256,
  tiempo de respuesta y número de filas: la trazabilidad de la base.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .cliente import ClienteSMV, Respuesta, extraer_registros, resolver_operacion

log = logging.getLogger(__name__)


class CacheDisco:
    def __init__(self, raiz: str | Path = "cache/raw"):
        self.raiz = Path(raiz)

    def ruta(self, operacion: str, ejercicio: int, periodo: str, tipo: str) -> Path:
        operacion = resolver_operacion(operacion)
        return self.raiz / operacion / str(ejercicio) / f"{periodo}_{tipo}.xml.gz"

    def existe(self, *clave) -> bool:
        return self.ruta(*clave).exists()

    def leer(self, *clave) -> bytes:
        return gzip.decompress(self.ruta(*clave).read_bytes())

    def leer_meta(self, *clave) -> dict:
        return json.loads(self.ruta(*clave).with_suffix("").with_suffix(".json").read_text("utf-8"))

    def guardar(self, resp: Respuesta, filas: int) -> Path:
        destino = self.ruta(resp.operacion, resp.ejercicio, resp.periodo, resp.tipo)
        destino.parent.mkdir(parents=True, exist_ok=True)

        tmp = destino.with_name(destino.name + ".tmp")
        tmp.write_bytes(gzip.compress(resp.contenido))
        os.replace(tmp, destino)

        meta = {
            "operacion": resp.operacion,
            "ejercicio": resp.ejercicio,
            "periodo": resp.periodo,
            "tipo": resp.tipo,
            "descargado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "bytes": len(resp.contenido),
            "sha256": hashlib.sha256(resp.contenido).hexdigest(),
            "segundos": round(resp.segundos, 2),
            "intentos": resp.intentos,
            "filas": filas,
            "vacio": filas == 0,
        }
        ruta_meta = destino.with_suffix("").with_suffix(".json")
        tmp_meta = ruta_meta.with_name(ruta_meta.name + ".tmp")
        tmp_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), "utf-8")
        os.replace(tmp_meta, ruta_meta)
        return destino


def descargar(cliente: ClienteSMV, cache: CacheDisco, operacion: str, ejercicio: int,
              periodo: str, tipo: str, refrescar: bool = False) -> tuple[str, int]:
    """Descarga una combinación si no está en caché. Devuelve (origen, filas).

    origen es 'cache' o 'red'. refrescar=True fuerza la descarga (útil para los
    períodos recientes, que la SMV puede corregir si una empresa re-presenta).
    """
    operacion = resolver_operacion(operacion)
    clave = (operacion, ejercicio, periodo, tipo)

    if not refrescar and cache.existe(*clave):
        meta = cache.leer_meta(*clave)
        # Un período reciente vacío suele ser un período que aún no se presentó (o que
        # se presentó tarde): se vuelve a pedir. Los vacíos antiguos sí son definitivos.
        if not (meta["vacio"] and ejercicio >= datetime.now().year - 1):
            return "cache", meta["filas"]

    resp = cliente.consultar(*clave)
    registros = extraer_registros(resp.contenido, operacion)  # si falla, no se cachea
    cache.guardar(resp, len(registros))
    log.info("%s %s-%s-%s: %d filas, %.1f MB, %.1f s",
             operacion, ejercicio, periodo, tipo, len(registros),
             len(resp.contenido) / 1e6, resp.segundos)
    return "red", len(registros)


def cargar(cache: CacheDisco, operacion: str, ejercicio: int, periodo: str, tipo: str) -> pd.DataFrame:
    """Lee una combinación desde el caché y la devuelve como DataFrame, sin limpiar."""
    operacion = resolver_operacion(operacion)
    registros = extraer_registros(cache.leer(operacion, ejercicio, periodo, tipo), operacion)
    df = pd.DataFrame(registros)
    # Columnas de trazabilidad: qué se pidió (puede no coincidir con lo que dice la fila)
    df["_operacion"] = operacion
    df["_ejercicio_consultado"] = ejercicio
    df["_periodo_consultado"] = periodo
    df["_tipo_consultado"] = tipo
    return df
