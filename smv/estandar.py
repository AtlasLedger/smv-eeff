"""Capa estandarizada: conceptos comparables entre planes de cuentas y ratios.

Lee el mapeo de mapeo/mapeo_cuentas.csv (concepto, plan, cuentas, confianza) y lo aplica
sobre la tabla de hechos.

Decisiones de diseño:
- El mapeo vive en un CSV y no en el código: es criterio contable, no programación.
  Cualquiera (incluido un contador sin saber Python) puede revisarlo y proponer cambios.
- Cada valor lleva su nivel de confianza:
    directo    la cuenta equivale sin discusión (y, cuando existe, coincide con el
               total que la propia SMV publica en su índice)
    propuesto  requiere una decisión de criterio que aún no se validó
    validado   decisión de criterio revisada y aprobada
  Un ratio hereda la confianza más baja de sus insumos. Así nadie usa sin saberlo un
  número que depende de una decisión discutible.
- Si un concepto suma varias cuentas y ninguna aparece en la presentación, el valor
  queda nulo (no cero): "no reportado" no es lo mismo que "cero".
- Los ratios de flujo sobre stock (ROE, ROA) se calculan solo con estados anuales y
  usan el promedio entre el cierre y el cierre anterior (monto_comparativo del balance).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RANGO_CONFIANZA = {"directo": 3, "validado": 2, "propuesto": 1}
CLAVES = ["rpj", "ejercicio", "periodo", "tipo"]


def leer_mapeo(ruta: str | Path) -> pd.DataFrame:
    m = pd.read_csv(ruta, dtype=str).fillna("")
    m = m[m["confianza"].isin(RANGO_CONFIANZA) & (m["cuentas"] != "")]
    filas = [
        {"concepto": r.concepto, "plan": r.plan, "cuenta": c.strip(), "confianza": r.confianza}
        for r in m.itertuples() for c in r.cuentas.split("+")
    ]
    return pd.DataFrame(filas)


def conceptos(hechos: pd.DataFrame, mapeo: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una fila por (empresa, período, tipo, concepto)."""
    h = hechos.copy()
    for c in ["rpj", "periodo", "tipo", "cuenta"]:
        h[c] = h[c].astype(str)
    h["plan"] = h["cuenta"].str[1]
    x = h.merge(mapeo, on=["plan", "cuenta"], how="inner")
    agg = (x.groupby(CLAVES + ["concepto", "confianza"], as_index=False, observed=True)
             .agg(valor=("monto", lambda s: s.sum(min_count=1)),
                  valor_comparativo=("monto_comparativo", lambda s: s.sum(min_count=1)),
                  valor_acumulado=("monto_acumulado", lambda s: s.sum(min_count=1)),
                  cuentas=("cuenta", lambda s: "+".join(sorted(s)))))
    return agg


def ratios(est: pd.DataFrame) -> pd.DataFrame:
    """Ratios estándar sobre la tabla de conceptos (solo presentaciones anuales para ROE/ROA)."""
    ancho = est.pivot_table(index=CLAVES, columns="concepto", values="valor", aggfunc="first")
    comp = est.pivot_table(index=CLAVES, columns="concepto", values="valor_comparativo", aggfunc="first")
    conf = est.assign(r=est["confianza"].map(RANGO_CONFIANZA)).pivot_table(
        index=CLAVES, columns="concepto", values="r", aggfunc="first")

    def col(df, nombre):
        return df[nombre] if nombre in df else pd.Series(np.nan, index=df.index)

    def div(a, b):
        b = b.where(b != 0)
        return a / b

    def promedio(nombre):
        return pd.concat([col(ancho, nombre), col(comp, nombre)], axis=1).mean(axis=1, skipna=False)

    anual = ancho.index.get_level_values("periodo") == "A"
    definiciones = {
        "margen_bruto": (div(col(ancho, "utilidad_bruta"), col(ancho, "ingresos")), ["utilidad_bruta", "ingresos"], False),
        "margen_operativo": (div(col(ancho, "utilidad_operativa"), col(ancho, "ingresos")), ["utilidad_operativa", "ingresos"], False),
        "margen_neto": (div(col(ancho, "utilidad_neta"), col(ancho, "ingresos")), ["utilidad_neta", "ingresos"], False),
        "roe": (div(col(ancho, "utilidad_neta"), promedio("patrimonio_total")), ["utilidad_neta", "patrimonio_total"], True),
        "roa": (div(col(ancho, "utilidad_neta"), promedio("activo_total")), ["utilidad_neta", "activo_total"], True),
        "pasivo_patrimonio": (div(col(ancho, "pasivo_total"), col(ancho, "patrimonio_total")), ["pasivo_total", "patrimonio_total"], False),
        "deuda_patrimonio": (div(col(ancho, "deuda_financiera"), col(ancho, "patrimonio_total")), ["deuda_financiera", "patrimonio_total"], False),
        "liquidez_corriente": (div(col(ancho, "activo_corriente"), col(ancho, "pasivo_corriente")), ["activo_corriente", "pasivo_corriente"], False),
        "tasa_impositiva_efectiva": (div(-col(ancho, "impuesto_renta"), col(ancho, "utilidad_antes_impuestos")), ["impuesto_renta", "utilidad_antes_impuestos"], False),
        "morosidad": (div(col(ancho, "creditos_atrasados"), col(ancho, "creditos_brutos")), ["creditos_atrasados", "creditos_brutos"], False),
        "cobertura_provisiones": (div(-col(ancho, "provisiones_creditos"), col(ancho, "creditos_atrasados")), ["provisiones_creditos", "creditos_atrasados"], False),
        "siniestralidad": (div(-col(ancho, "siniestros_netos"), col(ancho, "primas_ganadas_netas")), ["siniestros_netos", "primas_ganadas_netas"], False),
    }
    salida = []
    inverso = {v: k for k, v in RANGO_CONFIANZA.items()}
    for nombre, (serie, insumos, solo_anual) in definiciones.items():
        if solo_anual:
            serie = serie.where(anual)
        rango = pd.concat([col(conf, i) for i in insumos], axis=1).min(axis=1, skipna=False)
        df = pd.DataFrame({"ratio": nombre, "valor": serie, "confianza": rango.map(inverso)})
        salida.append(df.dropna(subset=["valor"]).reset_index())
    return pd.concat(salida, ignore_index=True)


def control_cruzado(est: pd.DataFrame, presentaciones: pd.DataFrame) -> pd.DataFrame:
    """Compara conceptos 'directo' con los totales del índice de la SMV. Devuelve discrepancias."""
    pares = {"activo_total": "smv_activo_total", "pasivo_total": "smv_pasivo_total",
             "patrimonio_total": "smv_patrimonio_total", "utilidad_neta": "smv_utilidad_neta"}
    p = presentaciones.drop_duplicates(CLAVES)
    salida = []
    for concepto, col_smv in pares.items():
        if col_smv not in p:
            continue
        e = est[est["concepto"] == concepto][CLAVES + ["valor"]]
        m = e.merge(p[CLAVES + [col_smv]], on=CLAVES).dropna(subset=[col_smv])
        m = m[(m["valor"] - m[col_smv]).abs() > 1]
        salida.append(m.rename(columns={col_smv: "valor_smv"}).assign(concepto=concepto))
    return pd.concat(salida, ignore_index=True) if salida else pd.DataFrame()
