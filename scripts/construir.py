"""Construye el modelo dimensional (Parquet) a partir del caché crudo.

    python scripts/construir.py                 # escribe en data/
    python scripts/construir.py --salida /tmp/x

No llama a la SMV: solo procesa lo que ya está en cache/raw. Se puede volver a
correr cuantas veces se quiera; reescribe la salida completa.
"""
from __future__ import annotations

import argparse
import logging
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from smv import CacheDisco
from smv.estandar import (cobertura, conceptos, control_cruzado, cuadre_balance, deriva_descripciones,
                          identidad_resultados, leer_mapeo, ratios, cambios_en_comparativos)
from smv.modelo import construir

RAIZ = Path(__file__).resolve().parents[1]


def capa_estandar(salida: Path, ruta_mapeo: Path) -> dict[str, int]:
    """Aplica el mapeo de cuentas, calcula ratios y cruza contra el índice de la SMV."""
    import json

    import pandas as pd

    hechos = pd.read_parquet(salida / "hechos")
    pres = pd.read_parquet(salida / "presentaciones.parquet")
    est = conceptos(hechos, leer_mapeo(ruta_mapeo))
    est.to_parquet(salida / "estandar.parquet", index=False)
    rat = ratios(est)
    rat.to_parquet(salida / "ratios.parquet", index=False)

    deriva = deriva_descripciones(ruta_mapeo, pd.read_parquet(salida / "cuentas_descripciones.parquet"))
    deriva.to_csv(salida / "mapeo_revisar_descripciones.csv", index=False)

    cob = cobertura(est, pres, ruta_mapeo)
    cob.to_csv(salida / "cobertura_mapeo.csv", index=False)
    # Las partidas intermedias solo existen cuando hay interés minoritario u otras: su
    # cobertura baja es esperable y no es alerta.
    bajas = cob[(cob["cobertura"] < 0.9) & (cob["presentaciones"] > 0)
                & (cob["concepto"] != "partidas_entre_pasivo_y_patrimonio")]

    cambios_en_comparativos(est).to_parquet(salida / "cambios_en_comparativos.parquet", index=False)

    ident = identidad_resultados(est, hechos)
    ident.to_csv(salida / "identidad_resultados.csv", index=False)

    descuadre = cuadre_balance(est)
    if len(descuadre):
        descuadre.to_csv(salida / "balance_descuadrado.csv", index=False)

    dif, comparadas = control_cruzado(est, pres)
    calidad = json.loads((salida / "calidad.json").read_text("utf-8"))
    # Planes presentes en los datos que el mapeo no cubre (ej. letras antiguas B, S, C)
    mapeados = set(pd.read_csv(ruta_mapeo, dtype=str)["plan"].dropna())
    calidad["planes_sin_mapeo"] = sorted(set(pres["plan"].dropna()) - mapeados)
    calidad["mapeo_cuentas_con_descripcion_cambiante"] = int(deriva["cuenta"].nunique())
    calidad["balances_que_no_cuadran"] = len(descuadre)
    ant = ident[ident["contra"] == "antes_extraordinarias"]
    calidad["identidad_resultado_antes_extraordinarias_tasa"] = (
        round(float((ant["tasa"] * ant["n"]).sum() / ant["n"].sum()), 4) if len(ant) else None)
    calidad["identidad_resultado_antes_extraordinarias_anios_bajo_95pct"] = (
        ant.loc[ant["tasa"] < 0.95, "ejercicio"].astype(int).tolist())
    calidad["control_cruzado_indice_smv_comparaciones"] = comparadas
    calidad["control_cruzado_indice_smv_discrepancias"] = len(dif)
    calidad["mapeo_conceptos_con_cobertura_menor_90pct"] = bajas[["concepto", "plan", "tipo", "cobertura"]].to_dict("records")
    (salida / "calidad.json").write_text(json.dumps(calidad, indent=2, ensure_ascii=False), "utf-8")
    if len(dif):
        dif.to_csv(salida / "control_cruzado_discrepancias.csv", index=False)
    return {"conceptos": len(est), "ratios": len(rat), "comparaciones_indice": comparadas, "discrepancias_indice": len(dif)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cache", default="cache/raw")
    p.add_argument("--salida", default="data")
    p.add_argument("--mapeo", default=str(RAIZ / "mapeo" / "mapeo_cuentas.csv"))
    a = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    salida = Path(a.salida)
    tmp = salida.with_name(salida.name + ".tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    t0 = time.monotonic()
    resumen = construir(CacheDisco(a.cache), tmp)
    resumen |= capa_estandar(tmp, Path(a.mapeo))
    # Reemplazo al final: si la construcción falla, la salida anterior queda intacta.
    if salida.exists():
        shutil.rmtree(salida)
    tmp.rename(salida)
    logging.info("Listo en %.0f s: %s", time.monotonic() - t0, resumen)
    return 0


if __name__ == "__main__":
    sys.exit(main())
