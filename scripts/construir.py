"""Construye el modelo dimensional (Parquet) a partir del caché crudo.

    python scripts/construir.py                 # escribe en data/
    python scripts/construir.py --salida /tmp/x

No llama a la SMV: solo procesa lo que ya está en cache/raw. Se puede volver a
correr cuantas veces se quiera; reescribe la salida completa.
"""
from __future__ import annotations

import argparse
import logging
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from smv import CacheDisco
from smv.modelo import construir


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cache", default="cache/raw")
    p.add_argument("--salida", default="data")
    a = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    salida = Path(a.salida)
    tmp = salida.with_name(salida.name + ".tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    t0 = time.monotonic()
    resumen = construir(CacheDisco(a.cache), tmp)
    # Reemplazo al final: si la construcción falla, la salida anterior queda intacta.
    if salida.exists():
        shutil.rmtree(salida)
    tmp.rename(salida)
    logging.info("Listo en %.0f s: %s", time.monotonic() - t0, resumen)
    return 0


if __name__ == "__main__":
    sys.exit(main())
