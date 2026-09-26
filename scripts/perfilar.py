"""Perfil de calidad de una descarga ya cacheada. Genera un reporte en Markdown.

Ejemplo:
    python scripts/perfilar.py --op resultados --anio 2024 --periodo A --tipo I

No limpia nada: solo mide. El objetivo es decidir la limpieza con evidencia.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from smv import CacheDisco, cargar
from smv.cliente import resolver_operacion

# Diccionario oficial de la SMV (segundo carácter del código de cuenta).
# "I" NO está documentado: es uno de los hallazgos a investigar.
PLANES_DOCUMENTADOS = {
    "D": "Empresas en general",
    "F": "Bancos y financieras", "B": "Bancos y financieras",
    "E": "Seguros", "S": "Seguros",
    "A": "AFP",
    "V": "CAVALI", "C": "CAVALI",
}

# Heurísticas de encoding roto. Son señales para revisar a mano, no diagnósticos.
PATRONES_ENCODING = {
    "carácter de reemplazo U+FFFD": re.compile("\ufffd"),
    "mojibake UTF-8 leído como Latin-1 (Ã, Â)": re.compile(r"[ÃÂ][\u0080-\u00bf]|Ã[a-zA-Z]"),
    "signo ? dentro de palabra": re.compile(r"\w\?\w"),
    "'ci n' (probable 'ción' con tilde perdida)": re.compile(r"ci n\b"),
    "consonante mayúscula suelta + palabra (ej. 'M todo')": re.compile(r"(?<!\w)[B-DF-HJ-NP-TV-Z] [a-z]"),
}


# ---------- utilidades de formato ----------

def tabla(df: pd.DataFrame, max_filas: int = 30) -> str:
    """Tabla Markdown simple, sin depender de tabulate."""
    if df.empty:
        return "_(sin filas)_\n"
    df = df.head(max_filas)
    cols = [str(c) for c in df.columns]
    lineas = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for fila in df.itertuples(index=False):
        celdas = [str(v).replace("|", "\\|").replace("\n", " ") for v in fila]
        lineas.append("| " + " | ".join(celdas) + " |")
    return "\n".join(lineas) + "\n"


def solo_ascii(texto: str) -> str:
    """Deja solo letras ASCII en minúscula. 'Método' y 'M todo' colapsan a 'mtodo':
    si dos descripciones de una misma cuenta colapsan igual, la diferencia es de encoding."""
    return re.sub(r"[^a-z]", "", str(texto).lower())


def sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(texto)) if not unicodedata.combining(c))


# ---------- secciones del perfil ----------

def seccion_general(df: pd.DataFrame, meta: dict) -> str:
    s = "## 1. Tamaño y origen\n\n"
    s += f"- Filas: **{len(df):,}**\n- Columnas: {df.shape[1] - 4} (más 4 de trazabilidad)\n"
    s += f"- Tamaño del XML crudo: {meta['bytes'] / 1e6:.2f} MB; tiempo de respuesta: {meta['segundos']} s\n"
    s += f"- Descargado (UTC): {meta['descargado_utc']}; SHA-256: `{meta['sha256'][:16]}...`\n\n"
    cols = [c for c in df.columns if not c.startswith("_")]
    s += "Columnas recibidas: " + ", ".join(f"`{c}`" for c in cols) + "\n\n"
    return s


def seccion_consistencia_consulta(df: pd.DataFrame) -> str:
    s = "## 2. ¿Lo recibido coincide con lo pedido?\n\n"
    for col in ["Ejercicio", "Trimestre", "TipoInformacion"]:
        if col in df:
            vc = df[col].astype(str).value_counts().rename_axis(col).reset_index(name="filas")
            s += f"**{col}**\n\n" + tabla(vc) + "\n"
    return s


def seccion_empresas(df: pd.DataFrame) -> str:
    s = "## 3. Empresas (candidatas a dimensión)\n\n"
    if "RPJ" not in df:
        return s + "_Columna RPJ no encontrada._\n\n"
    s += f"- RPJ únicos: **{df['RPJ'].nunique():,}**\n"
    if "RUC" in df:
        s += f"- RUC únicos: {df['RUC'].nunique():,}\n"
    # Un RPJ debería tener un solo valor de cada atributo. Si no, la dimensión no es limpia.
    atributos = [c for c in ["NombreEmpresa", "RUC", "CIIU", "TipoEmpresa", "TipoSector"] if c in df]
    filas = []
    for c in atributos:
        n = int((df.groupby("RPJ")[c].nunique(dropna=False) > 1).sum())
        filas.append({"atributo": c, "RPJ con más de un valor": n})
    s += "\nAtributos que varían dentro de un mismo RPJ (ideal: 0 en todos):\n\n"
    s += tabla(pd.DataFrame(filas))
    if "RUC" in df:
        n = int((df.groupby("RUC")["RPJ"].nunique() > 1).sum())
        s += f"\n- RUC asociados a más de un RPJ: {n}\n"
    if "TipoEmpresa" in df:
        vc = (df.groupby("TipoEmpresa")["RPJ"].nunique().sort_values(ascending=False)
              .rename("empresas").reset_index())
        s += "\nEmpresas por TipoEmpresa:\n\n" + tabla(vc)
    filas_emp = df.groupby("RPJ").size()
    s += (f"\nCuentas por empresa: mín {filas_emp.min()}, mediana {int(filas_emp.median())}, "
          f"máx {filas_emp.max()}\n\n")
    return s


def seccion_planes(df: pd.DataFrame) -> str:
    s = "## 4. Planes de cuentas (2º carácter de `Cuenta`)\n\n"
    if "Cuenta" not in df:
        return s + "_Columna Cuenta no encontrada._\n\n"
    plan = df["Cuenta"].astype(str).str[1]
    resumen = (df.assign(_plan=plan).groupby("_plan")
               .agg(filas=("Cuenta", "size"), empresas=("RPJ", "nunique"), cuentas_distintas=("Cuenta", "nunique"))
               .sort_values("filas", ascending=False).reset_index().rename(columns={"_plan": "plan"}))
    resumen["documentado"] = resumen["plan"].map(lambda p: PLANES_DOCUMENTADOS.get(p, "NO DOCUMENTADO"))
    s += tabla(resumen) + "\n"

    multi = df.assign(_plan=plan).groupby("RPJ")["_plan"].nunique()
    s += f"- Empresas que reportan en más de un plan: {int((multi > 1).sum())}\n"

    if "TipoEmpresa" in df:
        cruce = pd.crosstab(df["TipoEmpresa"], plan).reset_index()
        s += "\nCruce TipoEmpresa × plan (filas). Sirve para entender a quién pertenece cada plan:\n\n"
        s += tabla(cruce)

    no_doc = df[~plan.isin(PLANES_DOCUMENTADOS)]
    if not no_doc.empty and "NombreEmpresa" in df:
        s += "\nEmpresas en planes no documentados (primeras 15):\n\n"
        ej = (no_doc.assign(plan=no_doc["Cuenta"].astype(str).str[1])
              .groupby(["plan", "RPJ", "NombreEmpresa"]).size().rename("filas").reset_index())
        s += tabla(ej, 15)
        muestra_cuentas = no_doc[["Cuenta", "DescripcionCuenta"]].drop_duplicates().head(15) \
            if "DescripcionCuenta" in df else pd.DataFrame()
        s += "\nMuestra de cuentas de esos planes:\n\n" + tabla(muestra_cuentas, 15)
    return s + "\n"


def seccion_moneda(df: pd.DataFrame) -> str:
    s = "## 5. Moneda\n\n"
    if "Moneda" not in df:
        return s + "_Columna Moneda no encontrada._\n\n"
    vc = (df.groupby("Moneda", dropna=False)
          .agg(filas=("Moneda", "size"), empresas=("RPJ", "nunique")).reset_index())
    s += tabla(vc)
    multi = df.groupby("RPJ")["Moneda"].nunique()
    s += f"\n- Empresas con más de una moneda en el mismo período: {int((multi > 1).sum())}\n\n"
    return s


def seccion_montos(df: pd.DataFrame) -> str:
    s = "## 6. Montos\n\n"
    filas = []
    for c in ["Monto1", "Monto2", "Monto3", "Monto4"]:
        if c not in df:
            continue
        num = pd.to_numeric(df[c], errors="coerce")
        no_numericos = int(num.isna().sum() - df[c].isna().sum())
        filas.append({
            "columna": c,
            "tipo_original": str(df[c].dtype),
            "nulos": int(df[c].isna().sum()),
            "no_numéricos": no_numericos,
            "ceros": int((num == 0).sum()),
            "distintos_de_cero": int((num.fillna(0) != 0).sum()),
            "negativos": int((num < 0).sum()),
        })
    s += tabla(pd.DataFrame(filas))
    s += ("\nSi Monto3/Monto4 salen todo en cero, se pueden descartar del modelo "
          "(pero se deja la evidencia aquí).\n\n")
    return s


def seccion_duplicados(df: pd.DataFrame) -> str:
    s = "## 7. Duplicados\n\n"
    exactos = int(df.duplicated().sum())
    s += f"- Filas exactamente duplicadas: {exactos}\n"
    claves = [c for c in ["RPJ", "Cuenta", "Moneda"] if c in df]
    if len(claves) >= 2:
        d = df[df.duplicated(subset=claves, keep=False)]
        s += f"- Filas con clave ({', '.join(claves)}) repetida: {len(d)}\n"
        if not d.empty:
            cols = claves + [c for c in ["DescripcionCuenta", "Monto1"] if c in df]
            s += "\nMuestra:\n\n" + tabla(d[cols].sort_values(claves), 15)
    return s + "\n"


def seccion_encoding(df: pd.DataFrame) -> str:
    s = "## 8. Encoding\n\n"
    # is_string_dtype cubre tanto "object" (pandas 2) como "str" (pandas 3)
    texto = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) and not c.startswith("_")]

    filas, ejemplos = [], []
    for c in texto:
        valores = df[c].dropna().astype(str).drop_duplicates()
        for nombre, patron in PATRONES_ENCODING.items():
            # re de Python y no .str.contains: con pandas 3 + pyarrow el regex va a RE2,
            # que no acepta escapes \u ni lookbehind.
            hits = valores[valores.map(lambda v: bool(patron.search(v)))]
            if len(hits):
                filas.append({"columna": c, "patrón": nombre, "valores_distintos": len(hits)})
                ejemplos.extend({"columna": c, "patrón": nombre, "valor": v} for v in hits.head(3))
    s += "Valores sospechosos (heurística, revisar a mano):\n\n" + tabla(pd.DataFrame(filas))
    if ejemplos:
        s += "\nEjemplos:\n\n" + tabla(pd.DataFrame(ejemplos), 25)

    # Prueba más fuerte: una misma cuenta con varias descripciones.
    if {"Cuenta", "DescripcionCuenta"} <= set(df.columns):
        var = df.groupby("Cuenta")["DescripcionCuenta"].agg(lambda x: sorted(set(x.dropna().astype(str))))
        var = var[var.map(len) > 1]
        encoding = var[var.map(lambda vs: len({solo_ascii(v) for v in vs}) == 1)]
        redaccion = var[var.map(lambda vs: len({solo_ascii(v) for v in vs}) > 1)]
        s += (f"\nCuentas con más de una descripción: **{len(var)}**\n"
              f"- Solo difieren por encoding (colapsan al quitar no-ASCII): {len(encoding)}\n"
              f"- Difieren en redacción real: {len(redaccion)}\n\n")
        if len(encoding):
            s += "Ejemplos por encoding:\n\n" + tabla(
                pd.DataFrame({"Cuenta": encoding.index, "variantes": encoding.map(" ‖ ".join).values}), 10)
        if len(redaccion):
            s += "\nEjemplos por redacción:\n\n" + tabla(
                pd.DataFrame({"Cuenta": redaccion.index, "variantes": redaccion.map(" ‖ ".join).values}), 10)

    # ¿Cuánto texto tiene tildes correctas? Da idea de si el problema es general o puntual.
    if "DescripcionCuenta" in df:
        d = df["DescripcionCuenta"].dropna().astype(str).drop_duplicates()
        con_tilde = d[d != d.map(sin_tildes)]
        s += f"\nDescripciones distintas: {len(d):,}; con tildes/ñ bien formadas: {len(con_tilde):,}\n\n"
    return s


def seccion_nulos(df: pd.DataFrame) -> str:
    s = "## 9. Nulos y vacíos por columna\n\n"
    filas = []
    for c in df.columns:
        if c.startswith("_"):
            continue
        vacios = int((df[c].astype(str).str.strip() == "").sum())
        filas.append({"columna": c, "nulos": int(df[c].isna().sum()), "vacíos": vacios,
                      "distintos": int(df[c].nunique())})
    return s + tabla(pd.DataFrame(filas), 50) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--op", default="resultados")
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--periodo", default="A")
    p.add_argument("--tipo", default="I")
    p.add_argument("--cache", default="cache/raw")
    p.add_argument("--salida", default="reportes")
    a = p.parse_args()

    op = resolver_operacion(a.op)
    cache = CacheDisco(a.cache)
    clave = (op, a.anio, a.periodo.upper(), a.tipo.upper())
    if not cache.existe(*clave):
        print(f"No está en caché: {clave}. Corre primero scripts/extraer.py", file=sys.stderr)
        return 1

    df = cargar(cache, *clave)
    meta = cache.leer_meta(*clave)

    reporte = f"# Perfil: {op} {a.anio} {a.periodo.upper()} {a.tipo.upper()}\n\n"
    if df.empty:
        reporte += "La respuesta vino vacía.\n"
    else:
        for seccion in (seccion_general,):
            reporte += seccion(df, meta)
        for seccion in (seccion_consistencia_consulta, seccion_empresas, seccion_planes,
                        seccion_moneda, seccion_montos, seccion_duplicados,
                        seccion_encoding, seccion_nulos):
            reporte += seccion(df)

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    archivo = salida / f"perfil_{op}_{a.anio}_{a.periodo.upper()}_{a.tipo.upper()}.md"
    archivo.write_text(reporte, "utf-8")
    print(reporte)
    print(f"\nReporte guardado en {archivo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
