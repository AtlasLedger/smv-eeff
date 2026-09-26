"""Compara la base construida contra cifras publicadas por las propias empresas.

    python scripts/validar.py            # usa data/ y validacion/referencias.csv

Cada referencia indica empresa, período, concepto estándar, campo (valor, comparativo o
acumulado), el monto publicado en miles y la fuente. El reporte queda en
validacion/reporte.md. Una diferencia mayor a 1 (miles) se marca como discrepancia.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default=str(RAIZ / "data"))
    p.add_argument("--referencias", default=str(RAIZ / "validacion" / "referencias.csv"))
    p.add_argument("--reporte", default=str(RAIZ / "validacion" / "reporte.md"))
    a = p.parse_args()

    ref = pd.read_csv(a.referencias, dtype={"periodo": str})
    est = pd.read_parquet(Path(a.data) / "estandar.parquet")
    emp = pd.read_parquet(Path(a.data) / "empresas.parquet")[["rpj", "nombre"]]
    est = est.merge(emp, on="rpj")

    filas = []
    for r in ref.itertuples():
        m = est[(est["nombre"] == r.empresa_busqueda) & (est["ejercicio"] == r.ejercicio)
                & (est["periodo"] == r.periodo) & (est["tipo"] == r.tipo) & (est["concepto"] == r.concepto)]
        base = m[r.campo].iloc[0] if len(m) else None
        dif = None if base is None or pd.isna(base) else base - r.valor_referencia
        estado = "sin dato" if dif is None else ("ok" if abs(dif) <= 1 else "DISCREPANCIA")
        filas.append({"empresa": r.empresa_busqueda, "periodo": f"{r.ejercicio}-{r.periodo}-{r.tipo}",
                      "concepto": r.concepto, "campo": r.campo, "publicado": r.valor_referencia,
                      "base": base, "diferencia": dif, "resultado": estado,
                      "confianza": m["confianza"].iloc[0] if len(m) else None, "fuente": r.fuente})
    out = pd.DataFrame(filas)

    resumen = out["resultado"].value_counts().to_dict()
    texto = ["# Validación contra cifras publicadas por las empresas", "",
             "Montos en miles de la moneda de reporte. Tolerancia: 1 (redondeo).", "",
             f"Resultado: {resumen}", ""]
    for empresa, g in out.groupby("empresa", sort=False):
        texto += [f"## {empresa}", "", f"Fuente: {g['fuente'].iloc[0]}", "",
                  "| período | concepto | campo | publicado | base | diferencia | resultado | confianza |",
                  "|---|---|---|---:|---:|---:|---|---|"]
        for f in g.itertuples():
            fmt = lambda v: "" if v is None or pd.isna(v) else f"{v:,.0f}"
            texto.append(f"| {f.periodo} | {f.concepto} | {f.campo} | {fmt(f.publicado)} | {fmt(f.base)} "
                         f"| {fmt(f.diferencia)} | {f.resultado} | {f.confianza or ''} |")
        texto.append("")
    Path(a.reporte).write_text("\n".join(texto), "utf-8")
    print("\n".join(texto[:6]))
    return 1 if resumen.get("DISCREPANCIA") else 0


if __name__ == "__main__":
    sys.exit(main())
