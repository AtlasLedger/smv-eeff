"""Descarga estados financieros de la SMV al caché local.

Ejemplos:
    # Primer entregable: estado de resultados 2024, anual, individual
    python scripts/extraer.py --op resultados --anios 2024 --periodos A --tipos I

    # Histórico completo de un endpoint (tarda horas; se puede cortar y retomar)
    python scripts/extraer.py --op resultados --anios 2000-2026

    # Todos los endpoints de un año, forzando re-descarga
    python scripts/extraer.py --op todas --anios 2026 --refrescar
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from smv import OPERACIONES, PERIODOS, TIPOS, CacheDisco, ClienteSMV, ErrorSMV, descargar
from smv.cliente import HOST_POR_DEFECTO


def rango_anios(texto: str) -> list[int]:
    """'2024' -> [2024]; '2000-2003' -> [2000..2003]; '2020,2024' -> [2020, 2024]."""
    anios: list[int] = []
    for parte in texto.split(","):
        if "-" in parte:
            a, b = (int(x) for x in parte.split("-"))
            anios.extend(range(a, b + 1))
        else:
            anios.append(int(parte))
    return anios


def configurar_logging(carpeta: Path) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    formato = "%(asctime)s %(levelname)s %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=formato,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(carpeta / "extraccion.log", encoding="utf-8"),
        ],
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--op", default="resultados",
                   help=f"alias ({', '.join(OPERACIONES)}) o 'todas'")
    p.add_argument("--anios", default="2024")
    p.add_argument("--periodos", default=",".join(PERIODOS), help="ej. A o A,1,2,3,4")
    p.add_argument("--tipos", default=",".join(TIPOS), help="I, C o I,C")
    p.add_argument("--refrescar", action="store_true", help="ignora el caché y vuelve a descargar")
    p.add_argument("--pausa", type=float, default=1.5,
                   help="segundos entre llamadas a la red (cortesía con el servidor)")
    p.add_argument("--timeout", type=float, default=180,
                   help="segundos máximos de lectura por respuesta (CambiosPatrimonio es lento)")
    p.add_argument("--intentos", type=int, default=5, help="intentos por combinación")
    p.add_argument("--cache", default="cache/raw")
    p.add_argument("--host", default=HOST_POR_DEFECTO, help="solo para pruebas con servidor simulado")
    a = p.parse_args()

    configurar_logging(Path("logs"))
    log = logging.getLogger("extraer")

    # efdata se excluye de "todas": es un endpoint de grilla paginada que siempre
    # devuelve 0 registros (probado con Ejercicio/Periodo/Tipo y con page/rows).
    ops = [o for o in OPERACIONES if o != "efdata"] if a.op == "todas" else [x.strip() for x in a.op.split(",")]
    # Años de más reciente a más antiguo: si la corrida se corta, lo ya bajado es lo más útil.
    combinaciones = [
        (op, anio, per.strip().upper(), tipo.strip().upper())
        for anio in sorted(rango_anios(a.anios), reverse=True)
        for per in a.periodos.split(",")
        for tipo in a.tipos.split(",")
        for op in ops
    ]

    cliente = ClienteSMV(host=a.host, timeout_lectura=a.timeout, max_intentos=a.intentos)
    cache = CacheDisco(a.cache)
    resumen = {"red": 0, "cache": 0, "vacios": 0, "filas": 0}
    fallidos: list[tuple] = []
    t0 = time.monotonic()

    log.info("Inicio: %d combinaciones", len(combinaciones))
    for i, combo in enumerate(combinaciones, 1):
        try:
            origen, filas = descargar(cliente, cache, *combo, refrescar=a.refrescar)
        except ErrorSMV as e:
            # Un fallo no detiene el recorrido: se registra y se sigue. Al volver a
            # correr el script, solo se reintentan los que faltan (el resto está en caché).
            log.error("[%d/%d] %s FALLÓ: %s", i, len(combinaciones), combo, e)
            fallidos.append((combo, str(e)))
            continue

        resumen[origen] += 1
        resumen["filas"] += filas
        resumen["vacios"] += filas == 0
        if origen == "red":
            time.sleep(a.pausa)
        if i % 25 == 0:
            log.info("Avance %d/%d", i, len(combinaciones))

    minutos = (time.monotonic() - t0) / 60
    log.info("Fin en %.1f min. Red: %d | Caché: %d | Vacíos: %d | Filas: %d | Fallidos: %d",
             minutos, resumen["red"], resumen["cache"], resumen["vacios"],
             resumen["filas"], len(fallidos))
    for combo, err in fallidos:
        log.info("  pendiente: %s (%s)", combo, err)
    return 1 if fallidos else 0


if __name__ == "__main__":
    sys.exit(main())
