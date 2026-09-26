"""Agrega a validacion/referencias.csv cifras de empresas peruanas que reportan a la SEC.

    python scripts/referencias_sec.py --anios 2015-2024

Credicorp y Buenaventura presentan el Form 20-F en NIIF con etiquetas XBRL. La SEC publica
esas cifras en una API pública (data.sec.gov). Es una fuente independiente de la SMV para
validar la base en muchos años sin leer PDFs.

Solo se usan etiquetas cuyo significado coincide con un concepto estándar de la base.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]

EMPRESAS = {
    # CIK: (nombre en la base, etiquetas a usar)
    "0001001290": ("CREDICORP LTD.", ["Assets", "Liabilities", "Equity", "ProfitLoss", "ProfitLossBeforeTax",
                                      "IncomeTaxExpenseContinuingOperations", "RevenueFromInterest",
                                      "InterestExpense"]),
    "0001013131": ("COMPAÑIA DE MINAS BUENAVENTURA S.A.A.", ["Revenue", "ProfitLoss", "ProfitLossBeforeTax",
                                                            "Assets", "Liabilities", "Equity", "CurrentAssets",
                                                            "CurrentLiabilities", "GrossProfit",
                                                            "IncomeTaxExpenseContinuingOperations"]),
}
CONCEPTO = {
    "Revenue": "ingresos", "ProfitLoss": "utilidad_neta", "ProfitLossBeforeTax": "utilidad_antes_impuestos",
    "Assets": "activo_total", "Liabilities": "pasivo_total", "Equity": "patrimonio_total",
    "CurrentAssets": "activo_corriente", "CurrentLiabilities": "pasivo_corriente",
    "GrossProfit": "utilidad_bruta", "IncomeTaxExpenseContinuingOperations": "impuesto_renta",
    "RevenueFromInterest": "ingresos_intereses", "InterestExpense": "gastos_intereses",
}
# La SEC publica gastos como positivos; la base conserva el signo de la SMV (negativo).
SIGNO = {"impuesto_renta": -1, "gastos_intereses": -1}


def descargar(cik: str, carpeta: Path) -> dict:
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / f"CIK{cik}.json"
    if not destino.exists():
        r = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", timeout=90,
                         headers={"User-Agent": "smv-eeff (proyecto academico de datos abiertos)"})
        r.raise_for_status()
        destino.write_bytes(r.content)
    return json.loads(destino.read_text("utf-8"))


def rango(texto: str) -> list[int]:
    a, _, b = texto.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--anios", default="2015-2024")
    p.add_argument("--cache", default=str(RAIZ / "cache" / "sec"))
    a = p.parse_args()

    ruta = RAIZ / "validacion" / "referencias.csv"
    ref = pd.read_csv(ruta, dtype=str)
    nuevas = []
    for cik, (nombre, etiquetas) in EMPRESAS.items():
        hechos = descargar(cik, Path(a.cache))["facts"]["ifrs-full"]
        fuente = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json (Form 20-F, XBRL)"
        for anio in rango(a.anios):
            for etiqueta in etiquetas:
                if etiqueta not in hechos:
                    continue
                for valores in hechos[etiqueta]["units"].values():
                    # Solo el 20-F de ese mismo año (no los comparativos de años siguientes,
                    # que pueden venir reexpresados).
                    v = [x for x in valores if x.get("form") == "20-F" and x.get("fy") == anio
                         and x["end"] == f"{anio}-12-31" and x.get("start", f"{anio}-01-01") == f"{anio}-01-01"]
                    if not v:
                        continue
                    concepto = CONCEPTO[etiqueta]
                    nuevas.append({
                        "empresa_busqueda": nombre, "ejercicio": str(anio), "periodo": "A", "tipo": "C",
                        "concepto": concepto, "campo": "valor",
                        "valor_referencia": str(round(v[0]["val"] / 1000) * SIGNO.get(concepto, 1)),
                        "fuente": fuente, "diferencia_esperada": "",
                        "nota": "La SEC publica en unidades; aquí en miles."})
    salida = (pd.concat([ref, pd.DataFrame(nuevas)], ignore_index=True)
                .drop_duplicates(["empresa_busqueda", "ejercicio", "periodo", "tipo", "concepto", "campo"]))
    salida.to_csv(ruta, index=False)
    print(f"Referencias: {len(ref)} -> {len(salida)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
