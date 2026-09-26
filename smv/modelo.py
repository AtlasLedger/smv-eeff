"""Construcción del modelo dimensional a partir del caché crudo.

Tablas que produce (todas en Parquet):

- hechos/ejercicio=AAAA/*.parquet   Un monto por (empresa, período, tipo, cuenta).
- presentaciones.parquet            Una fila por estado presentado por una empresa en un
                                    período: moneda, método de flujo, plan de cuentas y los
                                    totales que la propia SMV publica en su índice.
- empresas.parquet                  Dimensión de empresas (último valor conocido de cada atributo).
- empresas_nombres.parquet          Historial de razones sociales (las empresas cambian de nombre).
- cuentas.parquet                   Dimensión de cuentas: código, estado, plan, descripción vigente.
- cuentas_descripciones.parquet     Historial de descripciones por código.
- patrimonio/ejercicio=AAAA/*.parquet  Estado de cambios en el patrimonio (matriz fila x
                                    columna). Solo celdas distintas de cero: el 93 % de la
                                    matriz es cero y guardarlo no aporta información.
- patrimonio_columnas.parquet       Nombre de cada columna de patrimonio por plan.
- calidad.json                      Problemas encontrados y corregidos al construir.

Decisiones de diseño:
- Se separa lo que se repite en cada fila (nombre, RUC, CIIU, moneda...) en dimensiones.
  La tabla de hechos queda con claves cortas y montos: pesa una fracción del crudo.
- Se particiona por ejercicio para que la actualización trimestral solo reescriba el
  año en curso y para que ningún archivo supere el límite de 100 MB de GitHub.
- No se convierte moneda ni se "arregla" ningún monto. La base publica lo que la
  empresa reportó, con la moneda en que lo reportó. Las conversiones y los ratios van
  en una capa aparte, para que el usuario pueda ver siempre el dato original.
- Monto3/Monto4 solo tienen sentido en los trimestres del estado de resultados y del
  ORI (acumulado del año). Donde la SMV los manda siempre en 0 se guardan como nulo,
  para no confundir "no aplica" con "cero".
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import pandas as pd

from .cache import CacheDisco, cargar
from .cliente import OPERACIONES
from .limpieza import limpiar

log = logging.getLogger(__name__)

# Operaciones con formato "una fila por cuenta" que entran a la tabla de hechos.
OPS_HECHOS = ["balance", "resultados", "flujo", "integrales"]
ORDEN_PERIODO = {"1": 1, "2": 2, "3": 3, "4": 4, "A": 5}
CLAVE_PRESENTACION = ["rpj", "ejercicio", "periodo", "tipo"]

# Cuenta de activo total por plan (las mismas que mapeo/mapeo_cuentas.csv marca como
# 'directo'). Se usan para detectar presentaciones reportadas en otra escala.
CUENTAS_ACTIVO_TOTAL = {"1D020T", "1F2001", "1E02ST", "1A020T", "1I1131", "1V020T",
                        "1B020T", "1S0301", "1C020T"}  # letras antiguas (2005)

COLUMNAS_HECHOS = {
    "RPJ": "rpj",
    "Ejercicio": "ejercicio",
    "_periodo_consultado": "periodo",
    "_tipo_consultado": "tipo",
    "estado": "estado",
    "Cuenta": "cuenta",
    "Monto1": "monto",
    "Monto2": "monto_comparativo",
    "Monto3": "monto_acumulado",
    "Monto4": "monto_acumulado_comparativo",
}


def archivos_en_cache(cache: CacheDisco, op: str) -> list[tuple[int, str, str]]:
    """Lista (ejercicio, periodo, tipo) disponibles en caché para una operación."""
    base = cache.raiz / OPERACIONES[op]
    salida = []
    for f in sorted(base.glob("*/*.xml.gz")):
        periodo, tipo = f.name.removesuffix(".xml.gz").split("_")
        salida.append((int(f.parent.name), periodo, tipo))
    return salida


def _hechos(df: pd.DataFrame) -> pd.DataFrame:
    h = df[[c for c in COLUMNAS_HECHOS if c in df]].rename(columns=COLUMNAS_HECHOS)
    for col in ["monto_acumulado", "monto_acumulado_comparativo"]:
        if col not in h:
            h[col] = float("nan")
        elif (h[col] == 0).all():
            h[col] = float("nan")
    # Flujo de efectivo trimestral: la SMV entrega el ACUMULADO del año en Monto1/Monto2
    # (verificado contra la variación del efectivo en el balance), a diferencia de
    # resultados y ORI, donde Monto1 es el trimestre aislado. Para que las columnas
    # signifiquen lo mismo en todos los estados, se mueve a las columnas de acumulado y
    # el trimestre aislado queda nulo (no se reporta; no se deriva restando).
    # Estado de resultados trimestral de las SAB (plan I): Monto1 NO es el trimestre (en
    # 2021, 2024 y 2025 no coincide nunca con acumulado T(n) - acumulado T(n-1), y en el T1
    # difiere del acumulado). Por magnitud parece el último mes (las SAB reportan
    # mensualmente), pero la fuente no lo dice: se deja fuera y se conserva el acumulado.
    if "plan" in df:
        sab_trim = (df["plan"].to_numpy() == "I") & (h["estado"] == "ER") & (h["periodo"] != "A")
        h.loc[sab_trim, ["monto", "monto_comparativo"]] = float("nan")
    fe_trim = (h["estado"] == "FE") & (h["periodo"] != "A")
    if fe_trim.any():
        h.loc[fe_trim, "monto_acumulado"] = h.loc[fe_trim, "monto"]
        h.loc[fe_trim, "monto_acumulado_comparativo"] = h.loc[fe_trim, "monto_comparativo"]
        h.loc[fe_trim, ["monto", "monto_comparativo"]] = float("nan")
    h["ejercicio"] = h["ejercicio"].astype("int16")
    return h


# Plan de cuentas esperado según el tipo de empresa (para resolver presentaciones duplicadas).
PLAN_POR_TIPO_EMPRESA = {"SOCIEDADES AGENTES DE BOLSA": "I"}


def _un_plan_por_empresa(df: pd.DataFrame, calidad: dict) -> pd.DataFrame:
    """Si una empresa presentó el mismo estado en dos planes de cuentas, deja uno.

    Caso real: BNB Valores SAB, 2021-T1, vino en el plan de SAB (I) y en el general (D)
    con las mismas cifras. Sin esto, los conceptos se sumarían dos veces. Se prefiere el
    plan que corresponde al tipo de empresa y, si no está definido, el más detallado.
    """
    if "plan" not in df or df.empty:
        return df
    n = df.groupby("RPJ")["plan"].nunique()
    dobles = n[n > 1].index
    if not len(dobles):
        return df
    quitar = []
    for rpj in dobles:
        sub = df[df["RPJ"] == rpj]
        esperado = PLAN_POR_TIPO_EMPRESA.get(sub["TipoEmpresa"].iloc[0]) if "TipoEmpresa" in sub else None
        conteo = sub["plan"].value_counts()
        elegido = esperado if esperado in conteo.index else conteo.index[0]
        quitar.append((df["RPJ"] == rpj) & (df["plan"] != elegido))
        calidad.setdefault("presentaciones_en_dos_planes", []).append(
            f"{rpj} {sub['Ejercicio'].iloc[0]}-{sub['_periodo_consultado'].iloc[0]}-"
            f"{sub['_tipo_consultado'].iloc[0]} {sub['_operacion'].iloc[0]}: se usa plan {elegido}")
    return df[~pd.concat(quitar, axis=1).any(axis=1)]


def _patrimonio(df: pd.DataFrame, calidad: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Las SAB (plan I) repiten los MISMOS códigos de fila en dos bloques: primero el año
    # anterior y luego el año actual (el saldo final del primero es el saldo inicial del
    # segundo). Parecen duplicados, pero no lo son: deduplicar borraría el año actual.
    # Se numera cada aparición en el orden del payload (bloque 0, 1...). En los demás
    # planes los códigos ya distinguen el año (4D01xx anterior, 4D02xx actual) y el
    # bloque es siempre 0.
    df = df.copy()
    df["bloque"] = df.groupby(["RPJ", "Cuenta", "OrdenColumna"]).cumcount().astype("int8")
    calidad["patrimonio_celdas_bloque_repetido"] += int((df["bloque"] > 0).sum())
    columnas = df.drop_duplicates(["plan", "OrdenColumna"])[["plan", "OrdenColumna", "DescripcionColumna"]]
    df = df[df["Monto1"] != 0]
    p = df[["RPJ", "_periodo_consultado", "_tipo_consultado", "Cuenta", "OrdenColumna", "bloque", "Monto1"]]
    p = p.rename(columns={"RPJ": "rpj", "_periodo_consultado": "periodo", "_tipo_consultado": "tipo",
                          "Cuenta": "cuenta", "OrdenColumna": "columna", "Monto1": "monto"})
    p["columna"] = p["columna"].astype("int16")
    return p, columnas


def _detectar_escala(hechos_por_anio: dict, idx: pd.DataFrame) -> pd.DataFrame:
    """Presentaciones cuyo activo total es ~1000 veces el que publica la SMV en su índice.

    Caso real: en las SAB hasta ~2010 las líneas de TOTAL (escritas en mayúsculas en la
    plantilla: TOTAL ACTIVO, UTILIDAD BRUTA...) venían en soles, mientras que las líneas de
    detalle venían en miles con decimales. El índice de la SMV muestra los totales en
    miles. Se exige una razón entre 999 y 1001 para no confundir esto con otro error.
    """
    vacio = pd.DataFrame(columns=CLAVE_PRESENTACION + ["escala_original"])
    if idx.empty or "smv_activo_total" not in idx:
        return vacio
    partes = []
    for lista in hechos_por_anio.values():
        for h in lista:
            partes.append(h[h["cuenta"].isin(CUENTAS_ACTIVO_TOTAL)][CLAVE_PRESENTACION + ["monto"]])
    if not partes:
        return vacio
    act = pd.concat(partes, ignore_index=True)
    m = act.merge(idx[CLAVE_PRESENTACION + ["smv_activo_total"]], on=CLAVE_PRESENTACION)
    m = m[m["smv_activo_total"].abs() > 0]
    razon = m["monto"] / m["smv_activo_total"]
    esc = m.loc[razon.between(999, 1001), CLAVE_PRESENTACION].drop_duplicates()
    return esc.assign(escala_original="unidades")


def _es_total(descripcion) -> bool:
    """Las líneas calculadas de las plantillas antiguas de las SAB van en MAYÚSCULAS."""
    texto = str(descripcion or "")
    if "por acci" in texto.lower():
        return False  # los montos por acción nunca se reescalan
    letras = re.sub(r"[^A-Za-zÁÉÍÓÚÑáéíóúñ]", "", texto)
    return bool(letras) and letras.isupper()


def _reescalar(df: pd.DataFrame, escalas: pd.DataFrame, totales: set, ejercicio: int | None = None) -> pd.DataFrame:
    """Divide entre 1000 las líneas de total de las presentaciones marcadas.

    `totales` es el conjunto de (ejercicio, periodo, cuenta) cuya descripción es de total.
    Las líneas de detalle ya vienen en miles y no se tocan.
    """
    df = df.copy()
    anio = df["ejercicio"] if "ejercicio" in df else pd.Series(ejercicio, index=df.index)
    claves = df[["rpj", "periodo", "tipo"]].assign(ejercicio=anio)
    marca = claves.merge(escalas, on=CLAVE_PRESENTACION, how="left")["escala_original"].notna().to_numpy()
    es_total = [(int(a), p, c) in totales for a, p, c in zip(anio, df["periodo"], df["cuenta"])]
    marca = marca & pd.Series(es_total, index=df.index).to_numpy()
    for col in [c for c in df.columns if c.startswith("monto")]:
        df.loc[marca, col] = df.loc[marca, col] / 1000
    return df


def _presentaciones(df: pd.DataFrame) -> pd.DataFrame:
    claves = ["RPJ", "Ejercicio", "_periodo_consultado", "_tipo_consultado", "estado"]
    p = (df.groupby(claves, as_index=False)
           .agg(plan=("plan", "first"), moneda=("moneda_iso", "first"),
                metodo_flujo=("MetodoFlujoEfectivo", "first"), cuentas=("Cuenta", "size")))
    return p.rename(columns={"RPJ": "rpj", "Ejercicio": "ejercicio",
                             "_periodo_consultado": "periodo", "_tipo_consultado": "tipo"})


def _atributos_empresa(df: pd.DataFrame, ejercicio: int, periodo: str) -> pd.DataFrame:
    cols = ["RPJ", "RUC", "NombreEmpresa", "CIIU", "TipoEmpresa", "TipoSector"]
    e = df[cols].drop_duplicates("RPJ").copy()
    e["ejercicio"], e["periodo"] = ejercicio, periodo
    return e


def construir(cache: CacheDisco, salida: Path) -> dict[str, int]:
    salida = Path(salida)
    (salida / "hechos").mkdir(parents=True, exist_ok=True)

    presentaciones, atributos, cuentas, indices, columnas_cp = [], [], [], [], []
    hechos_por_anio: dict[int, list[pd.DataFrame]] = {}
    patrimonio_por_anio: dict[int, list[pd.DataFrame]] = {}
    calidad = {"patrimonio_celdas_bloque_repetido": 0, "archivos_vacios": 0, "archivos_procesados": 0}

    for op in OPS_HECHOS + ["patrimonio", "indice"]:
        for ejercicio, periodo, tipo in archivos_en_cache(cache, op):
            if cache.leer_meta(op, ejercicio, periodo, tipo)["vacio"]:
                calidad["archivos_vacios"] += 1
                continue
            df = limpiar(cargar(cache, op, ejercicio, periodo, tipo))
            if df.empty:
                calidad["archivos_vacios"] += 1
                continue
            calidad["archivos_procesados"] += 1
            df = _un_plan_por_empresa(df, calidad)
            if op == "patrimonio":
                p, cols = _patrimonio(df, calidad)
                patrimonio_por_anio.setdefault(ejercicio, []).append(p)
                columnas_cp.append(cols)
                continue
            atributos.append(_atributos_empresa(df, ejercicio, periodo))
            if op == "indice":
                i = df[["RPJ", "Ejercicio", "_periodo_consultado", "_tipo_consultado",
                        "moneda_iso", "ActivoTotal", "PasivoTotal", "PatrimonioTotal",
                        "TotalIngreso", "UtilidadNeta"]]
                indices.append(i.rename(columns={
                    "RPJ": "rpj", "Ejercicio": "ejercicio", "_periodo_consultado": "periodo",
                    "_tipo_consultado": "tipo", "moneda_iso": "moneda",
                    "ActivoTotal": "smv_activo_total", "PasivoTotal": "smv_pasivo_total",
                    "PatrimonioTotal": "smv_patrimonio_total", "TotalIngreso": "smv_total_ingreso",
                    "UtilidadNeta": "smv_utilidad_neta"}))
                continue
            hechos_por_anio.setdefault(ejercicio, []).append(_hechos(df))
            presentaciones.append(_presentaciones(df))
            c = df.drop_duplicates("Cuenta")[["Cuenta", "estado", "plan", "DescripcionCuenta"]].copy()
            c["orden"] = range(len(c))
            c["ejercicio"], c["periodo"] = ejercicio, periodo
            cuentas.append(c)

    # --- Escala: algunas presentaciones antiguas vienen en unidades y no en miles
    idx = (pd.concat(indices, ignore_index=True).drop_duplicates(CLAVE_PRESENTACION)
           if indices else pd.DataFrame(columns=CLAVE_PRESENTACION + ["smv_activo_total"]))
    totales: set = set()
    if cuentas:
        cu_all = pd.concat(cuentas, ignore_index=True)
        cu_all = cu_all[cu_all["DescripcionCuenta"].map(_es_total)]
        totales = set(zip(cu_all["ejercicio"].astype(int), cu_all["periodo"], cu_all["Cuenta"]))
    escalas = _detectar_escala(hechos_por_anio, idx)
    calidad["presentaciones_con_totales_en_unidades"] = len(escalas)
    if len(escalas):
        hechos_por_anio = {a: [_reescalar(h, escalas, totales) for h in partes]
                           for a, partes in hechos_por_anio.items()}
        # Patrimonio de esas presentaciones: escala no verificada; se deja como vino y se avisa.
        calidad["patrimonio_escala_no_verificada"] = int(sum(
            len(p.merge(escalas.drop(columns="ejercicio"), on=["rpj", "periodo", "tipo"]))
            for a, partes in patrimonio_por_anio.items() for p in partes
            if a in set(escalas["ejercicio"].astype(int))))

    # --- Hechos, un archivo por ejercicio
    filas = 0
    for ejercicio, partes in sorted(hechos_por_anio.items()):
        h = pd.concat(partes, ignore_index=True)
        dup = h.duplicated(["rpj", "ejercicio", "periodo", "tipo", "cuenta"])
        if dup.any():
            raise ValueError(f"{ejercicio}: {int(dup.sum())} hechos duplicados")
        h = h.sort_values(["periodo", "tipo", "rpj", "estado", "cuenta"], ignore_index=True)
        for col in ["rpj", "periodo", "tipo", "estado", "cuenta"]:
            h[col] = h[col].astype("category")
        destino = salida / "hechos" / f"ejercicio={ejercicio}"
        destino.mkdir(exist_ok=True)
        h.drop(columns="ejercicio").to_parquet(destino / "part-0.parquet", index=False)
        filas += len(h)

    # --- Patrimonio, un archivo por ejercicio
    for ejercicio, partes in sorted(patrimonio_por_anio.items()):
        p = pd.concat(partes, ignore_index=True)
        for col in ["rpj", "periodo", "tipo", "cuenta"]:
            p[col] = p[col].astype("category")
        destino = salida / "patrimonio" / f"ejercicio={ejercicio}"
        destino.mkdir(parents=True, exist_ok=True)
        p.to_parquet(destino / "part-0.parquet", index=False)
    if columnas_cp:
        (pd.concat(columnas_cp).drop_duplicates(["plan", "OrdenColumna"], keep="last")
           .rename(columns={"OrdenColumna": "columna", "DescripcionColumna": "descripcion"})
           .sort_values(["plan", "columna"])
           .to_parquet(salida / "patrimonio_columnas.parquet", index=False))

    # --- Presentaciones (+ totales del índice de la SMV como control cruzado)
    pres = pd.concat(presentaciones, ignore_index=True)
    pres["ejercicio"] = pres["ejercicio"].astype("int16")
    pres = pres.merge(escalas, on=CLAVE_PRESENTACION, how="left")
    pres["escala_original"] = pres["escala_original"].fillna("miles")
    if indices:
        pres = pres.merge(idx.drop(columns="moneda"), on=CLAVE_PRESENTACION, how="left")
    if "smv_activo_total" in pres:
        # Sin índice no se puede detectar la escala mixta de las SAB antiguas: se avisa.
        sin_idx = (pres["plan"] == "I") & (pres["ejercicio"] <= 2011) & pres["smv_activo_total"].isna()
        pres.loc[sin_idx, "escala_original"] = "no verificada"
        calidad["sab_antiguas_sin_indice_escala_no_verificada"] = int(
            pres.loc[sin_idx].drop_duplicates(CLAVE_PRESENTACION).shape[0])
    pres.to_parquet(salida / "presentaciones.parquet", index=False)

    # --- Empresas: último valor conocido + historial de nombres
    at = pd.concat(atributos, ignore_index=True)
    at["_orden"] = at["ejercicio"] * 10 + at["periodo"].map(ORDEN_PERIODO)
    at = at.sort_values("_orden")
    empresas = at.groupby("RPJ", as_index=False).last()
    primero = at.groupby("RPJ")["_orden"].min()
    empresas["primer_periodo"] = empresas["RPJ"].map(primero).map(_orden_a_texto)
    empresas["ultimo_periodo"] = empresas["_orden"].map(_orden_a_texto)
    empresas = empresas.drop(columns=["_orden", "ejercicio", "periodo"]).rename(columns={
        "RPJ": "rpj", "RUC": "ruc", "NombreEmpresa": "nombre", "CIIU": "ciiu",
        "TipoEmpresa": "tipo_empresa", "TipoSector": "sector"})
    planes = pres.groupby("rpj")["plan"].agg(lambda s: ",".join(sorted(set(s))))
    empresas["planes"] = empresas["rpj"].map(planes)
    empresas.to_parquet(salida / "empresas.parquet", index=False)

    nombres = (at.groupby(["RPJ", "NombreEmpresa"], as_index=False)
                 .agg(desde=("_orden", "min"), hasta=("_orden", "max")))
    nombres["desde"] = nombres["desde"].map(_orden_a_texto)
    nombres["hasta"] = nombres["hasta"].map(_orden_a_texto)
    nombres.rename(columns={"RPJ": "rpj", "NombreEmpresa": "nombre"}).to_parquet(
        salida / "empresas_nombres.parquet", index=False)

    # --- Cuentas: descripción y orden de presentación del período más reciente
    cu = pd.concat(cuentas, ignore_index=True)
    cu["_orden"] = cu["ejercicio"] * 10 + cu["periodo"].map(ORDEN_PERIODO)
    cu = cu.sort_values(["_orden", "orden"])
    dim_cuentas = cu.groupby("Cuenta", as_index=False).last()
    dim_cuentas["primer_periodo"] = dim_cuentas["Cuenta"].map(cu.groupby("Cuenta")["_orden"].min()).map(_orden_a_texto)
    dim_cuentas["ultimo_periodo"] = dim_cuentas["_orden"].map(_orden_a_texto)
    dim_cuentas = (dim_cuentas.drop(columns=["_orden", "ejercicio", "periodo"])
                   .rename(columns={"Cuenta": "cuenta", "DescripcionCuenta": "descripcion"})
                   .sort_values(["estado", "plan", "orden"]))
    dim_cuentas.to_parquet(salida / "cuentas.parquet", index=False)

    hist = (cu.groupby(["Cuenta", "DescripcionCuenta"], as_index=False, dropna=False)
              .agg(desde=("_orden", "min"), hasta=("_orden", "max")))
    hist["desde"] = hist["desde"].map(_orden_a_texto)
    hist["hasta"] = hist["hasta"].map(_orden_a_texto)
    hist.rename(columns={"Cuenta": "cuenta", "DescripcionCuenta": "descripcion"}).to_parquet(
        salida / "cuentas_descripciones.parquet", index=False)

    (salida / "calidad.json").write_text(json.dumps(calidad, indent=2, ensure_ascii=False), "utf-8")
    return {"hechos": filas, "presentaciones": len(pres), "empresas": len(empresas),
            "cuentas": len(dim_cuentas), "ejercicios": len(hechos_por_anio)}


def _orden_a_texto(orden: int) -> str:
    anio, p = divmod(int(orden), 10)
    return f"{anio}-{'A' if p == 5 else 'T' + str(p)}"
