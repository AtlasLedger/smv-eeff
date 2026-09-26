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

import logging
from pathlib import Path

import pandas as pd

from .cache import CacheDisco, cargar
from .cliente import OPERACIONES
from .limpieza import limpiar

log = logging.getLogger(__name__)

# Operaciones con formato "una fila por cuenta" que entran a la tabla de hechos.
OPS_HECHOS = ["balance", "resultados", "flujo", "integrales"]
ORDEN_PERIODO = {"1": 1, "2": 2, "3": 3, "4": 4, "A": 5}

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
    h["ejercicio"] = h["ejercicio"].astype("int16")
    return h


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

    presentaciones, atributos, cuentas, indices = [], [], [], []
    hechos_por_anio: dict[int, list[pd.DataFrame]] = {}

    for op in OPS_HECHOS + ["indice"]:
        for ejercicio, periodo, tipo in archivos_en_cache(cache, op):
            if cache.leer_meta(op, ejercicio, periodo, tipo)["vacio"]:
                continue
            df = limpiar(cargar(cache, op, ejercicio, periodo, tipo))
            if df.empty:
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

    # --- Presentaciones (+ totales del índice de la SMV como control cruzado)
    pres = pd.concat(presentaciones, ignore_index=True)
    if indices:
        idx = pd.concat(indices, ignore_index=True).drop_duplicates(["rpj", "ejercicio", "periodo", "tipo"])
        pres = pres.merge(idx.drop(columns="moneda"), on=["rpj", "ejercicio", "periodo", "tipo"], how="left")
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

    return {"hechos": filas, "presentaciones": len(pres), "empresas": len(empresas),
            "cuentas": len(dim_cuentas), "ejercicios": len(hechos_por_anio)}


def _orden_a_texto(orden: int) -> str:
    anio, p = divmod(int(orden), 10)
    return f"{anio}-{'A' if p == 5 else 'T' + str(p)}"
