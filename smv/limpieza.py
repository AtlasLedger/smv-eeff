"""Limpieza de los registros crudos de la SMV.

Decisiones de diseño:
- El encoding roto NO se puede decodificar: la SMV manda un espacio (0x20) o un '¿'
  donde iba la letra con tilde. La información se perdió en origen. Por eso se repara
  con un diccionario de valores conocidos y no con una regla general (una regla del
  tipo "consonante + espacio + minúscula" rompería textos legítimos como "Y otros").
- Cada reparación es explícita y auditable: si aparece un valor roto nuevo, el test
  de calidad lo detecta y se agrega aquí a mano.
- Los identificadores se limpian de espacios (el RPJ de las SAB viene con relleno)
  y los valores centinela (RUC = "0", CIIU vacío) pasan a nulo: un 0 no es un RUC.
"""
from __future__ import annotations

import re

import pandas as pd

# Valores de catálogo completos que llegan rotos -> valor correcto.
REPARACIONES_VALOR = {
    "D lares": "Dólares",
    "M todo Directo": "Método Directo",
    "M todo Indirecto": "Método Indirecto",
}

# Fragmentos rotos dentro de descripciones de cuentas -> fragmento correcto.
# Se aplican como reemplazo literal de palabra (no regex genérico).
REPARACIONES_FRAGMENTO = {
    "p¿rdida": "pérdida",
    "P¿rdida": "Pérdida",
    "b¿sica": "básica",
    "B¿sica": "Básica",
}

MONEDAS = {"Soles": "PEN", "Dólares": "USD"}

# Estado financiero según la operación consultada. No se usa el primer carácter del
# código de cuenta porque no es consistente: las SAB (plan I) usan el prefijo 4 en el
# flujo de efectivo y el 3 en cambios en el patrimonio, al revés que el resto.
ESTADO_POR_OPERACION = {
    "obtener_BalanceGeneral": "BG",       # estado de situación financiera
    "obtener_GanciaPerdida": "ER",        # estado de resultados
    "obtener_FlujoEfectivo": "FE",        # flujo de efectivo
    "obtener_ResultadosIntegrales": "ORI",  # otro resultado integral
    "obtener_CambiosPatrimonio": "CP",    # cambios en el patrimonio
}

PLANES = {
    "D": "Empresas en general",
    "F": "Bancos y financieras",
    "E": "Seguros",
    "A": "AFP",
    "I": "Sociedades agentes de bolsa",
    "V": "CAVALI (compensación y liquidación)",
}

_ESPACIOS = re.compile(r"\s+")


def limpiar_texto(valor):
    """Quita espacios sobrantes/saltos de línea y repara encoding conocido."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    texto = _ESPACIOS.sub(" ", str(valor)).strip()
    if texto in REPARACIONES_VALOR:
        return REPARACIONES_VALOR[texto]
    for roto, bueno in REPARACIONES_FRAGMENTO.items():
        if roto in texto:
            texto = texto.replace(roto, bueno)
    return texto or None


def limpiar_ruc(valor):
    texto = limpiar_texto(valor)
    if texto is None or texto.strip("0") == "":
        return None  # holdings extranjeros (Credicorp Ltd., IFS, InRetail) vienen con RUC 0
    return texto


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una copia con identificadores, textos y montos normalizados.

    No cambia la forma de la tabla (misma cantidad de filas); solo limpia valores y
    agrega columnas derivadas: plan, estado, moneda_iso.
    """
    out = df.copy()
    for col in [c for c in ["RPJ", "Cuenta"] if c in out]:
        out[col] = out[col].astype(str).str.strip()
    if "RUC" in out:
        out["RUC"] = out["RUC"].map(limpiar_ruc)
    for col in ["DescripcionColumna", "NombreEmpresa", "TipoEmpresa", "TipoSector", "CIIU", "Moneda",
                "MetodoFlujoEfectivo", "DescripcionCuenta", "TipoInformacion", "Trimestre"]:
        if col in out:
            out[col] = out[col].map(limpiar_texto)
    numericas = [c for c in out.columns if c.startswith("Monto")] + [
        c for c in ["ActivoTotal", "PatrimonioTotal", "TotalIngreso", "UtilidadNeta", "PasivoTotal"] if c in out]
    for col in numericas:
        out[col] = pd.to_numeric(out[col], errors="raise").astype("float64")

    if "Ejercicio" in out:
        # Llega como texto en unos endpoints y como número en otros: se unifica a entero
        # para que los cruces entre tablas no fallen en silencio.
        out["Ejercicio"] = pd.to_numeric(out["Ejercicio"], errors="raise").astype("int16")
    if "Cuenta" in out:
        out["plan"] = out["Cuenta"].str[1]
        out["estado"] = out["_operacion"].map(ESTADO_POR_OPERACION)
    if "Moneda" in out:
        out["moneda_iso"] = out["Moneda"].map(MONEDAS)
    return out


def textos_sospechosos(serie: pd.Series) -> list[str]:
    """Valores que todavía parecen tener encoding roto (para el test de calidad)."""
    patron = re.compile(r"�|¿(?=[a-záéíóúñ])|(?<=[a-z])¿|(?<![\w(])[B-DF-HJ-NP-TV-XZ] [a-z]{3,}")
    vistos = serie.dropna().astype(str).drop_duplicates()
    return [v for v in vistos if patron.search(v)]
