"""Exporta versiones CSV de la base para quien usa Excel o Power BI.

    python scripts/exportar.py        # lee data/*.parquet y escribe data/csv/

Qué genera:
- resumen_anual.csv      Una fila por empresa, ejercicio y tipo (solo anuales): nombre,
                         sector, moneda, conceptos estándar y ratios en columnas. Es la
                         tabla más cómoda para empezar.
- resumen_trimestral.csv Igual, para los trimestres (montos del trimestre aislado).
- empresas.csv, cuentas.csv
- cambios_en_comparativos.csv  Cifras que cambiaron al presentarse como comparativo al año siguiente.
- estandar.csv.gz, ratios.csv.gz (comprimidos)
- hechos/hechos_AAAA.csv.gz  Detalle por cuenta, un archivo comprimido por ejercicio.

Los CSV usan coma como separador y punto decimal, en UTF-8 con BOM para que Excel
muestre bien las tildes.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CLAVES = ["rpj", "ejercicio", "periodo", "tipo"]
CONCEPTOS_RESUMEN = [
    "activo_total", "activo_corriente", "efectivo", "pasivo_total", "pasivo_corriente",
    "deuda_financiera", "patrimonio_total", "ingresos", "utilidad_bruta", "utilidad_operativa",
    "utilidad_antes_impuestos", "impuesto_renta", "utilidad_neta",
    "creditos_brutos", "creditos_atrasados", "depositos", "primas_ganadas_netas",
]


def resumen(est: pd.DataFrame, rat: pd.DataFrame, emp: pd.DataFrame, pres: pd.DataFrame) -> pd.DataFrame:
    valores = est[est["concepto"].isin(CONCEPTOS_RESUMEN)].pivot_table(
        index=CLAVES, columns="concepto", values="valor", aggfunc="first")
    valores = valores[[c for c in CONCEPTOS_RESUMEN if c in valores]]
    ratios = rat.pivot_table(index=CLAVES, columns="ratio", values="valor", aggfunc="first")
    ratios.columns = [f"ratio_{c}" for c in ratios.columns]
    # Qué conceptos de la fila dependen de un criterio aún no validado (ver mapeo/).
    # Los ratios heredan esa condición de sus insumos, así que basta con los conceptos.
    propuestos = (est[est["confianza"] == "propuesto"]
                    .groupby(CLAVES)["concepto"].agg(lambda s: ",".join(sorted(s)))
                    .rename("conceptos_no_validados"))
    moneda = (pres[pres["estado"] == "BG"].drop_duplicates(CLAVES)
                .set_index(CLAVES)[["moneda", "plan"]])
    out = valores.join(ratios, how="outer").join(moneda).join(propuestos).reset_index()
    out = out.merge(emp[["rpj", "nombre", "ruc", "tipo_empresa", "sector", "ciiu"]], on="rpj", how="left")
    # El resumen es para análisis: solo filas con balance o resultados.
    out = out[out[[c for c in ["activo_total", "utilidad_neta", "ingresos"] if c in out]].notna().any(axis=1)]
    primeras = ["rpj", "nombre", "ruc", "tipo_empresa", "sector", "ciiu", "ejercicio", "periodo",
                "tipo", "plan", "moneda", "conceptos_no_validados"]
    return out[primeras + [c for c in out.columns if c not in primeras]].sort_values(
        ["nombre", "ejercicio", "periodo", "tipo"])


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default=str(RAIZ / "data"))
    a = p.parse_args()
    data = Path(a.data)
    csv = data / "csv"
    if csv.exists():
        shutil.rmtree(csv)
    (csv / "hechos").mkdir(parents=True)
    kw = {"index": False, "encoding": "utf-8-sig"}

    est = pd.read_parquet(data / "estandar.parquet")
    rat = pd.read_parquet(data / "ratios.parquet")
    emp = pd.read_parquet(data / "empresas.parquet")
    pres = pd.read_parquet(data / "presentaciones.parquet")
    pres["ejercicio"] = pres["ejercicio"].astype(int)
    for df in (est, rat):
        df["ejercicio"] = df["ejercicio"].astype(int)

    res = resumen(est, rat, emp, pres)
    res[res["periodo"] == "A"].to_csv(csv / "resumen_anual.csv", **kw)
    res[res["periodo"] != "A"].to_csv(csv / "resumen_trimestral.csv", **kw)
    emp.to_csv(csv / "empresas.csv", **kw)
    (pd.read_parquet(data / "cambios_en_comparativos.parquet")
       .merge(emp[["rpj", "nombre"]], on="rpj", how="left")
       .to_csv(csv / "cambios_en_comparativos.csv", **kw))
    pd.read_parquet(data / "cuentas.parquet").to_csv(csv / "cuentas.csv", **kw)
    # Las tablas largas van comprimidas (Excel no las necesita: para eso están los resúmenes).
    est.to_csv(csv / "estandar.csv.gz", index=False, compression="gzip")
    rat.to_csv(csv / "ratios.csv.gz", index=False, compression="gzip")

    for carpeta in sorted((data / "hechos").glob("ejercicio=*")):
        anio = carpeta.name.split("=")[1]
        pd.read_parquet(carpeta).to_csv(csv / "hechos" / f"hechos_{anio}.csv.gz",
                                        index=False, compression="gzip")
    print(f"CSV en {csv}: {sum(1 for _ in csv.rglob('*.csv*'))} archivos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
