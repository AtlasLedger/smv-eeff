"""Servidor que imita al de la SMV, para probar el extractor sin tocar la red.

Imita lo observado en las pruebas reales: SOAP 1.1, JSON dentro del nodo Result,
varios planes de cuentas (incluido el '2I' no documentado), dos monedas y encoding
roto de forma inconsistente ('M todo Directo' junto a 'Ganancia (Pérdida) Bruta').
Los datos son inventados; solo sirven para probar la mecánica.
"""
from __future__ import annotations

import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from xml.sax.saxutils import escape


def _fila(rpj, nombre, ruc, tipo_emp, cuenta, desc, monto, moneda="Soles", metodo="Método Directo"):
    return {
        "RPJ": rpj, "TipoEmpresa": tipo_emp, "TipoSector": "X", "NombreEmpresa": nombre,
        "RUC": ruc, "CIIU": "0000", "Ejercicio": 2024, "TipoInformacion": "Individual",
        "Trimestre": "A", "Moneda": moneda, "MetodoFlujoEfectivo": metodo,
        "Cuenta": cuenta, "DescripcionCuenta": desc,
        "Monto1": monto, "Monto2": monto * 0.9, "Monto3": 0, "Monto4": 0,
    }


FILAS = [
    _fila("A001", "MINERA EJEMPLO S.A.", "20100000001", "Empresas Diversas", "2D01ST01", "Ingresos de Actividades Ordinarias", 1000),
    _fila("A001", "MINERA EJEMPLO S.A.", "20100000001", "Empresas Diversas", "2D01ST05", "Ganancia (Pérdida) Bruta", 400, metodo="M todo Directo"),
    _fila("A002", "INDUSTRIAL DEMO S.A.A.", "20100000002", "Empresas Diversas", "2D01ST01", "Ingresos de Actividades Ordinarias", 5000, moneda="Dólares"),
    _fila("A002", "INDUSTRIAL DEMO S.A.A.", "20100000002", "Empresas Diversas", "2D01ST05", "Ganancia (P rdida) Bruta", 2000, moneda="Dólares"),
    _fila("B001", "BANCO FICTICIO", "20100000003", "Bancos", "2F01ST01", "Ingresos por Intereses", 8000),
    _fila("B001", "BANCO FICTICIO", "20100000003", "Bancos", "2F01ST02", "Depreciaci n y Amortizaci n", -300),
    _fila("C001", "ENTIDAD X", "20100000004", "Otras", "2I01ST01", "Ingresos Financieros", 700),
    _fila("E001", "SEGUROS DEMO", "20100000005", "Seguros", "2E01ST01", "Primas de Seguros Netas", 900),
]


def construir_respuesta(operacion: str, filas: list[dict]) -> bytes:
    texto = escape(json.dumps(filas, ensure_ascii=False))
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>'
        f'<{operacion}Response xmlns="http://tempuri.org/">'
        f"<{operacion}Result>{texto}</{operacion}Result>"
        f"</{operacion}Response></soap:Body></soap:Envelope>"
    )
    return xml.encode("utf-8")


class Estado:
    fallos_pendientes = 0  # cuántas respuestas 500 devolver antes de responder bien
    llamadas = 0


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silencio
        pass

    def do_POST(self):
        Estado.llamadas += 1
        cuerpo = self.rfile.read(int(self.headers["Content-Length"]))
        if Estado.fallos_pendientes > 0:
            Estado.fallos_pendientes -= 1
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"<faultstring>Server was unable to process request.</faultstring>")
            return
        accion = self.headers.get("SOAPAction", "").strip('"').rsplit("/", 1)[-1]
        anio = int(re.search(rb"<Ejercicio>(\d+)</Ejercicio>", cuerpo).group(1))
        filas = FILAS if anio == 2024 else []  # otros años: respuesta vacía
        datos = construir_respuesta(accion, filas)
        self.send_response(200)
        self.send_header("Content-Type", "text/xml; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)


def iniciar(puerto: int = 0) -> tuple[ThreadingHTTPServer, str]:
    srv = ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


if __name__ == "__main__":
    import time
    srv, url = iniciar(8765)
    print(f"Servidor simulado en {url} (Ctrl+C para salir)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        srv.shutdown()
