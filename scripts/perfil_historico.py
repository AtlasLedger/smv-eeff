"""Perfil de toda la base construida: cobertura por año, planes, monedas y calidad.

    python scripts/perfil_historico.py      # lee data/ y escribe reportes/perfil_historico.md

A diferencia de perfilar.py (que mira un solo período crudo), este mira la base ya
construida completa. Sirve para revisar de un vistazo si algún año se comporta raro.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from smv.limpieza import textos_sospechosos  # noqa: E402


def tabla(df: pd.DataFrame) -> str:
    if df.empty:
        return "_(vacío)_\n"
    df = df.reset_index() if not isinstance(df.index, pd.RangeIndex) else df
    cab = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "---|" * len(df.columns)
    filas = ["| " + " | ".join("" if pd.isna(v) else str(v) for v in f) + " |" for f in df.itertuples(index=False)]
    return "\n".join([cab, sep, *filas]) + "\n"


def main() -> int:
    data = RAIZ / "data"
    pres = pd.read_parquet(data / "presentaciones.parquet")
    emp = pd.read_parquet(data / "empresas.parquet")
    cuentas = pd.read_parquet(data / "cuentas_descripciones.parquet")
    calidad = json.loads((data / "calidad.json").read_text("utf-8"))
    pres["ejercicio"] = pres["ejercicio"].astype(int)
    bg = pres[pres["estado"] == "BG"].drop_duplicates(["rpj", "ejercicio", "periodo", "tipo"])

    out = ["# Perfil histórico de la base", ""]
    out += [f"- Empresas: **{emp['rpj'].nunique():,}**",
            f"- Ejercicios: {bg['ejercicio'].min()} a {bg['ejercicio'].max()}",
            f"- Presentaciones de balance: {len(bg):,}", ""]

    out += ["## Presentaciones por año", "",
            "Empresas con balance anual (A) y número de presentaciones trimestrales, por tipo.", ""]
    anual = bg[bg["periodo"] == "A"].pivot_table(index="ejercicio", columns="tipo", values="rpj",
                                                   aggfunc="nunique").add_prefix("anual_")
    trim = bg[bg["periodo"] != "A"].pivot_table(index="ejercicio", columns="tipo", values="rpj",
                                                 aggfunc="count").add_prefix("trimestres_")
    out += [tabla(anual.join(trim, how="outer").fillna(0).astype(int)), ""]

    out += ["## Planes de cuentas por año (empresas con balance anual individual)", ""]
    planes = bg[(bg["periodo"] == "A") & (bg["tipo"] == "I")].pivot_table(
        index="ejercicio", columns="plan", values="rpj", aggfunc="nunique").fillna(0).astype(int)
    out += [tabla(planes), ""]

    out += ["## Moneda de reporte por año (balance anual individual)", ""]
    mon = bg[(bg["periodo"] == "A") & (bg["tipo"] == "I")].pivot_table(
        index="ejercicio", columns="moneda", values="rpj", aggfunc="nunique").fillna(0).astype(int)
    out += [tabla(mon), ""]

    out += ["## Correcciones de escala", ""]
    esc = bg.groupby(["ejercicio", "escala_original"]).size().unstack(fill_value=0)
    esc = esc.loc[:, [c for c in esc.columns if c != "miles"]] if len(esc.columns) > 1 else esc.iloc[:, :0]
    esc = esc[esc.sum(axis=1) > 0] if not esc.empty else esc
    out += ["Presentaciones cuyos totales venían en unidades (o sin índice para verificarlo):", "",
            tabla(esc), ""]

    out += ["## Encoding todavía sospechoso", "",
            "Descripciones de cuentas que siguen pareciendo rotas después de la limpieza. Si "
            "aparece algo aquí, hay que agregarlo al diccionario de `smv/limpieza.py`.", ""]
    sus = textos_sospechosos(cuentas["descripcion"]) + textos_sospechosos(emp["nombre"])
    out += ["\n".join(f"- `{s}`" for s in sus[:50]) if sus else "_Ninguna._", ""]

    out += ["## Calidad (de `data/calidad.json`)", "", "```json",
            json.dumps(calidad, indent=2, ensure_ascii=False), "```", ""]

    destino = RAIZ / "reportes" / "perfil_historico.md"
    destino.write_text("\n".join(out), "utf-8")
    print(f"Escrito {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
