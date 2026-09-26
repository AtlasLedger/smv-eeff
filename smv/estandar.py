"""Capa estandarizada: conceptos comparables entre planes de cuentas y ratios.

Lee el mapeo de mapeo/mapeo_cuentas.csv (concepto, plan, tipo, cuentas, confianza) y lo
aplica sobre la tabla de hechos. `tipo` vacío = aplica a individual y consolidado; `I` o
`C` cuando la plantilla cambia (el consolidado de bancos usa otra plantilla completa).
`desde`/`hasta` (ejercicios, vacío = sin límite) cuando un mismo código cambió de
significado en el tiempo (las plantillas previas a NIIF reutilizan códigos).

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
        {"regla": r.Index, "concepto": r.concepto, "plan": r.plan, "tipo_mapeo": r.tipo, "cuenta": c.strip(),
         "desde": int(r.desde) if r.desde else 0, "hasta": int(r.hasta) if r.hasta else 9999,
         "confianza": r.confianza}
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
    x = x[((x["tipo_mapeo"] == "") | (x["tipo_mapeo"] == x["tipo"]))
          & x["ejercicio"].astype(int).between(x["desde"], x["hasta"])]
    # Una presentación debe calzar con UNA sola regla por concepto. Si calza con dos (ej.
    # el código antiguo y el nuevo conviven en un año de transición), sumarlas duplicaría
    # el monto: mejor fallar y ajustar desde/hasta en el mapeo.
    reglas = x.groupby(CLAVES + ["concepto"], observed=True)["regla"].nunique()
    if (reglas > 1).any():
        casos = reglas[reglas > 1].reset_index().head(10).to_dict("records")
        raise ValueError(f"Presentaciones que calzan con más de una regla de mapeo: {casos}")
    agg = (x.groupby(CLAVES + ["concepto", "confianza"], as_index=False, observed=True)
             .agg(valor=("monto", lambda s: s.sum(min_count=1)),
                  valor_comparativo=("monto_comparativo", lambda s: s.sum(min_count=1)),
                  valor_acumulado=("monto_acumulado", lambda s: s.sum(min_count=1)),
                  cuentas=("cuenta", lambda s: "+".join(sorted(s)))))
    return _quitar_intermedias_ya_incluidas(agg)


def _quitar_intermedias_ya_incluidas(est: pd.DataFrame) -> pd.DataFrame:
    """En años de transición (ej. 2010) algunas empresas ya incluían el interés minoritario
    dentro del patrimonio. Si el balance cuadra SIN la partida intermedia, esa partida no
    estaba fuera de los totales y el concepto se elimina para esa presentación."""
    c = "partidas_entre_pasivo_y_patrimonio"
    if c not in set(est["concepto"]):
        return est
    w = est[est["concepto"].isin(["activo_total", "pasivo_total", "patrimonio_total"])].pivot_table(
        index=CLAVES, columns="concepto", values="valor", aggfunc="first").dropna()
    cuadra = w.index[(w["activo_total"] - w["pasivo_total"] - w["patrimonio_total"]).abs() <= 1]
    inter = est["concepto"] == c
    claves_inter = pd.MultiIndex.from_frame(est.loc[inter, CLAVES])
    quitar = inter.copy()
    quitar.loc[inter] = claves_inter.isin(cuadra)
    return est[~quitar].reset_index(drop=True)


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


def control_cruzado(est: pd.DataFrame, presentaciones: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Compara conceptos 'directo' con los totales del índice de la SMV.

    Devuelve (discrepancias, cantidad de comparaciones hechas). Si no se pudo comparar
    nada teniendo datos en ambos lados, lanza un error: un control que no compara nada
    no puede reportarse como "0 discrepancias".
    """
    pares = {"activo_total": "smv_activo_total", "pasivo_total": "smv_pasivo_total",
             "patrimonio_total": "smv_patrimonio_total", "utilidad_neta": "smv_utilidad_neta",
             "ingresos": "smv_total_ingreso"}
    p = presentaciones.drop_duplicates(CLAVES)
    salida, comparadas = [], 0
    for concepto, col_smv in pares.items():
        if col_smv not in p:
            continue
        e = est[est["concepto"] == concepto]
        if concepto == "ingresos":
            # Solo donde la definición es la misma que usa el índice de la SMV. En los demás
            # planes la diferencia es una decisión de criterio (ver mapeo/DECISIONES.md).
            anio = e["ejercicio"].astype(int)
            e = e[((e["cuentas"] == "2D01ST") & (anio >= 2010))
                  | e["cuentas"].isin(["2A01ST", "2V0101+2V01ST"])]
        e = e[CLAVES + ["valor"]]
        m = e.merge(p[CLAVES + [col_smv]], on=CLAVES).dropna(subset=[col_smv, "valor"])
        if concepto == "ingresos":
            # El índice pone 0 cuando la línea total de ingresos no vino en la presentación
            # (ej. CAVALI trimestral 2013-2016): es "sin dato", no un ingreso de cero.
            m = m[m[col_smv] != 0]
        comparadas += len(m)
        m = m[(m["valor"] - m[col_smv]).abs() > 1]
        salida.append(m.rename(columns={col_smv: "valor_smv"}).assign(concepto=concepto))
    if comparadas == 0 and len(est) and p.filter(like="smv_").notna().any().any():
        raise ValueError("control_cruzado no pudo comparar ninguna fila: revisar tipos de las claves")
    dif = pd.concat(salida, ignore_index=True) if salida else pd.DataFrame()
    return dif, comparadas


def cobertura(est: pd.DataFrame, presentaciones: pd.DataFrame, ruta_mapeo: str | Path) -> pd.DataFrame:
    """Por concepto x plan x tipo: en qué % de las presentaciones aparece el concepto.

    Una cobertura baja en un concepto 'directo' suele significar que la plantilla de la
    SMV cambió (otro código para la misma línea) y hay que ajustar el mapeo.
    """
    m = pd.read_csv(ruta_mapeo, dtype=str).fillna("")
    m = m[m["confianza"].isin(RANGO_CONFIANZA) & (m["cuentas"] != "")]
    estados = {"1": "BG", "2": "ER"}
    pres = presentaciones.drop_duplicates(CLAVES + ["estado"]).copy()
    pres["ejercicio"] = pres["ejercicio"].astype(int)
    e = est.assign(plan=est["cuentas"].str[1], ejercicio=est["ejercicio"].astype(int))
    filas = []
    for r in m.itertuples():
        estado = estados.get(r.cuentas[0])
        base = pres[(pres["plan"] == r.plan) & (pres["estado"] == estado)]
        if r.tipo:
            base = base[base["tipo"] == r.tipo]
        anios = base["ejercicio"].astype(int)
        base = base[anios.between(int(r.desde) if r.desde else 0, int(r.hasta) if r.hasta else 9999)]
        con = e[(e["concepto"] == r.concepto) & (e["plan"] == r.plan)]
        # Cuenta como presente si trae el período aislado o el acumulado (en trimestres de
        # SAB y del flujo solo existe el acumulado).
        con = con[con["valor"].notna() | con["valor_acumulado"].notna()]
        n = len(base)
        hay = len(base.merge(con[CLAVES], on=CLAVES)) if n else 0
        filas.append({"concepto": r.concepto, "plan": r.plan, "tipo": r.tipo or "I+C",
                      "desde": r.desde, "hasta": r.hasta,
                      "confianza": r.confianza, "presentaciones": n, "con_valor": hay,
                      "cobertura": hay / n if n else float("nan")})
    return pd.DataFrame(filas)


def deriva_descripciones(ruta_mapeo: str | Path, historial: pd.DataFrame) -> pd.DataFrame:
    """Cuentas usadas en el mapeo cuya descripción cambió en el tiempo.

    Un código que cambia de descripción puede haber cambiado de significado (pasa en las
    plantillas previas a NIIF). Se ignoran diferencias de mayúsculas, tildes y espacios.
    El resultado es una lista para revisar a mano, no un error.
    """
    import unicodedata

    def norm(t):
        t = unicodedata.normalize("NFD", str(t)).encode("ascii", "ignore").decode().lower()
        return " ".join(t.replace("(", " ").replace(")", " ").split())

    m = leer_mapeo(ruta_mapeo)
    usadas = m.groupby("cuenta")["concepto"].agg(lambda s: ",".join(sorted(set(s))))
    h = historial[historial["cuenta"].isin(usadas.index)].copy()
    h["norm"] = h["descripcion"].map(norm)
    variantes = h.groupby("cuenta")["norm"].nunique()
    cambian = variantes[variantes > 1].index
    out = h[h["cuenta"].isin(cambian)].sort_values(["cuenta", "desde"])
    out["conceptos"] = out["cuenta"].map(usadas)
    return out[["cuenta", "conceptos", "descripcion", "desde", "hasta"]]


def cuadre_balance(est: pd.DataFrame, tolerancia: float = 1.0) -> pd.DataFrame:
    """Presentaciones donde activo total != pasivo total + patrimonio total.

    Es una identidad contable: si no se cumple, hay un problema de escala, de mapeo o de
    la fuente. Tolerancia en miles (redondeo).
    """
    base = ["activo_total", "pasivo_total", "patrimonio_total"]
    w = est[est["concepto"].isin(base + ["partidas_entre_pasivo_y_patrimonio"])].pivot_table(
        index=CLAVES, columns="concepto", values="valor", aggfunc="first").dropna(subset=base)
    if w.empty:
        return pd.DataFrame(columns=CLAVES + base + ["diferencia"])
    # En plantillas antiguas el interés minoritario (y otras partidas) iba fuera de ambos totales.
    intermedio = w["partidas_entre_pasivo_y_patrimonio"].fillna(0) if "partidas_entre_pasivo_y_patrimonio" in w else 0
    w["diferencia"] = w["activo_total"] - w["pasivo_total"] - w["patrimonio_total"] - intermedio
    return w[w["diferencia"].abs() > tolerancia].reset_index()


# Línea "resultado antes de partidas extraordinarias" de las plantillas antiguas. Hasta
# ~2012, entre el impuesto y la utilidad neta había partidas extraordinarias e interés
# minoritario; la identidad correcta en esos años es contra esta línea.
LINEA_ANTES_EXTRAORDINARIAS = {"E": "2E1701", "S": "2S1401", "F": "2F1501", "B": "2B1101",
                               "I": "2I2141", "D": "2D05ST", "C": "2C05ST"}


def identidad_resultados(est: pd.DataFrame, hechos: pd.DataFrame) -> pd.DataFrame:
    """Verifica utilidad antes de impuestos + impuesto contra el resultado siguiente.

    Compara contra la línea "antes de partidas extraordinarias" cuando la plantilla la
    tiene, y si no, contra la utilidad neta. En plantillas actuales las diferencias
    suelen ser operaciones discontinuadas; en las antiguas, un error del mapeo por era.
    Devuelve la tasa de cumplimiento por plan y ejercicio.
    """
    w = est[est["concepto"].isin(["utilidad_antes_impuestos", "impuesto_renta", "utilidad_neta"])].pivot_table(
        index=CLAVES, columns="concepto", values="valor", aggfunc="first").dropna(
        subset=["utilidad_antes_impuestos", "impuesto_renta"]).reset_index()
    h = hechos[hechos["cuenta"].astype(str).isin(set(LINEA_ANTES_EXTRAORDINARIAS.values()))]
    h = h.assign(**{c: h[c].astype(str) for c in ["rpj", "periodo", "tipo", "cuenta"]})
    h = h.assign(ejercicio=h["ejercicio"].astype(int), plan=h["cuenta"].str[1])
    w["ejercicio"] = w["ejercicio"].astype(int)
    w = w.merge(h[CLAVES + ["plan", "monto"]], on=CLAVES, how="left")
    objetivo = w["monto"].fillna(w.get("utilidad_neta"))
    w["cumple"] = (w["utilidad_antes_impuestos"] + w["impuesto_renta"] - objetivo).abs() <= 1
    w["contra"] = w["monto"].notna().map({True: "antes_extraordinarias", False: "utilidad_neta"})
    return (w.dropna(subset=["cumple"]).groupby(["contra", "ejercicio"])["cumple"]
              .agg(tasa="mean", n="size").reset_index())


def cambios_en_comparativos(est: pd.DataFrame, tolerancia: float = 1.0) -> pd.DataFrame:
    """Cifras del año anterior que cambiaron en la presentación del año siguiente.

    Cada estado anual trae el año previo como comparativo. Si difiere de lo que se
    reportó originalmente, la empresa reexpresó o reclasificó. No todo cambio es una
    corrección de errores: hasta 2004 los comparativos se ajustaban por inflación, en 2010
    y 2011 hubo la adopción de NIIF, y hay reclasificaciones (ej. operaciones
    discontinuadas). Por eso el nombre neutro.
    """
    a = est[est["periodo"] == "A"].copy()
    a["ejercicio"] = a["ejercicio"].astype(int)
    original = a[["rpj", "ejercicio", "tipo", "concepto", "valor"]].rename(columns={"valor": "original"})
    posterior = (a[["rpj", "ejercicio", "tipo", "concepto", "valor_comparativo"]]
                 .rename(columns={"valor_comparativo": "segun_estado_siguiente"})
                 .assign(ejercicio=lambda d: d["ejercicio"] - 1))
    m = original.merge(posterior, on=["rpj", "ejercicio", "tipo", "concepto"]).dropna()
    m["diferencia"] = m["segun_estado_siguiente"] - m["original"]
    m = m[m["diferencia"].abs() > tolerancia].copy()
    m["diferencia_relativa"] = m["diferencia"] / m["original"].abs().where(m["original"] != 0)
    return m.sort_values(["ejercicio", "rpj", "tipo", "concepto"], ignore_index=True)
