"""Encuentra, por plan de cuentas, qué cuenta coincide con cada total del índice de la SMV.

    python scripts/buscar_cuentas_indice.py --anio 2005 --periodo A --tipo I

El índice de la SMV (obtener_InfoFinanciera) publica por empresa: activo total, pasivo
total, patrimonio total, total ingreso y utilidad neta. Si en un plan de cuentas una
cuenta coincide con ese total en todas (o casi todas) las empresas, es la cuenta que la
propia SMV usa para ese total. Es el punto de partida para mapear una plantilla nueva.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from smv import CacheDisco  # noqa: E402
from smv.cache import cargar  # noqa: E402
from smv.limpieza import limpiar  # noqa: E402

TOTALES = ["ActivoTotal", "PasivoTotal", "PatrimonioTotal", "TotalIngreso", "UtilidadNeta"]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--anio", type=int, required=True)
    p.add_argument("--periodo", default="A")
    p.add_argument("--tipo", default="I")
    p.add_argument("--planes", default="", help="filtrar planes, ej. B,S,C")
    p.add_argument("--cache", default="cache/raw")
    a = p.parse_args()

    c = CacheDisco(a.cache)
    clave = (a.anio, a.periodo, a.tipo)
    idx = limpiar(cargar(c, "indice", *clave))
    hechos = pd.concat([limpiar(cargar(c, op, *clave)) for op in ["balance", "resultados"]
                        if c.existe(op, *clave)], ignore_index=True)
    if a.planes:
        hechos = hechos[hechos["plan"].isin(a.planes.split(","))]
    desc = hechos.drop_duplicates("Cuenta").set_index("Cuenta")["DescripcionCuenta"]

    for total in TOTALES:
        m = hechos.merge(idx[["RPJ", total]], on="RPJ")
        m = m[m[total] != 0]
        # El índice redondea a miles: se tolera 1. También se prueba la escala en unidades.
        m["ok"] = ((m["Monto1"] - m[total]).abs() <= 1) | ((m["Monto1"] / 1000 - m[total]).abs() <= 1)
        r = m.groupby(["plan", "Cuenta"]).agg(coinciden=("ok", "sum"), empresas=("ok", "size")).reset_index()
        r = r[r["coinciden"] > 0].sort_values(["plan", "coinciden"], ascending=[True, False])
        mejor = r.groupby("plan").head(1)
        print(f"\n== {total}")
        for f in mejor.itertuples():
            print(f"  plan {f.plan}: {f.Cuenta} ({f.coinciden}/{f.empresas})  {str(desc.get(f.Cuenta, ''))[:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
