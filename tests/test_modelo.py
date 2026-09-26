"""Pruebas de limpieza y del modelo dimensional (sin red). Correr con: pytest -q"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import servidor_simulado as sim
from smv import CacheDisco, ClienteSMV, descargar
from smv.limpieza import limpiar, limpiar_ruc, limpiar_texto, textos_sospechosos
from smv.modelo import construir


def test_repara_valores_conocidos():
    assert limpiar_texto("D lares") == "Dólares"
    assert limpiar_texto("M todo Indirecto") == "Método Indirecto"
    assert limpiar_texto("Utilidad (p¿rdida) b¿sica por acción") == "Utilidad (pérdida) básica por acción"


def test_no_toca_textos_sanos():
    for t in ["Ganancia (Pérdida) Bruta", "Gastos de Ventas y Distribución", "Y otros"]:
        assert limpiar_texto(t) == t


def test_colapsa_espacios_y_saltos():
    assert limpiar_texto("  Otros ingresos\n (gastos)   netos ") == "Otros ingresos (gastos) netos"
    assert limpiar_texto("   ") is None


def test_ruc_cero_es_nulo():
    assert limpiar_ruc("0") is None
    assert limpiar_ruc("") is None
    assert limpiar_ruc("20100055237") == "20100055237"


def test_detector_de_encoding():
    sus = textos_sospechosos(pd.Series(["D lares", "Soles", "p¿rdida", "¿Qué?", "Y otros"]))
    assert sus == ["D lares", "p¿rdida"]


def test_limpiar_deriva_plan_estado_y_moneda():
    df = pd.DataFrame([{**sim.FILAS[0], "RPJ": "B80128     ", "Moneda": "D lares", "RUC": "0"}])
    out = limpiar(df)
    assert out.loc[0, "RPJ"] == "B80128"
    assert out.loc[0, "RUC"] is None
    assert out.loc[0, "plan"] == "D" and out.loc[0, "estado"] == "ER"
    assert out.loc[0, "moneda_iso"] == "USD"


@pytest.fixture
def cache_lleno(tmp_path):
    srv, url = sim.iniciar()
    cache = CacheDisco(tmp_path / "cache")
    cliente = ClienteSMV(host=url, max_intentos=1)
    descargar(cliente, cache, "resultados", 2024, "A", "I")
    srv.shutdown()
    return cache


def test_construir_modelo(cache_lleno, tmp_path):
    resumen = construir(cache_lleno, tmp_path / "data")
    assert resumen["hechos"] == len(sim.FILAS)
    assert resumen["empresas"] == len({f["RPJ"] for f in sim.FILAS})

    h = pd.read_parquet(tmp_path / "data" / "hechos")
    assert set(h.columns) >= {"rpj", "periodo", "tipo", "estado", "cuenta", "monto", "monto_comparativo"}
    # Anual: Monto3/Monto4 llegan en 0 -> no aplican -> nulo
    assert h["monto_acumulado"].isna().all()
    assert h["monto"].sum() == pytest.approx(sum(f["Monto1"] for f in sim.FILAS))

    e = pd.read_parquet(tmp_path / "data" / "empresas.parquet")
    assert e["rpj"].is_unique
    p = pd.read_parquet(tmp_path / "data" / "presentaciones.parquet")
    assert set(p["moneda"]) == {"PEN", "USD"}
