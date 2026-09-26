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
from smv.estandar import conceptos, leer_mapeo, ratios
from smv.modelo import _patrimonio, construir


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
    df = pd.DataFrame([{**sim.FILAS[0], "RPJ": "B80128     ", "Moneda": "D lares", "RUC": "0",
                        "_operacion": "obtener_GanciaPerdida"}])
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


def test_patrimonio_sab_conserva_los_dos_bloques():
    # Las SAB repiten los códigos para el año anterior y el actual: no son duplicados.
    base = {"RPJ": "S1", "_periodo_consultado": "A", "_tipo_consultado": "I", "plan": "I",
            "OrdenColumna": "1", "DescripcionColumna": "Capital"}
    df = pd.DataFrame([
        {**base, "Cuenta": "3I30I0", "Monto1": 100.0},  # saldo inicial año anterior
        {**base, "Cuenta": "3I30IA", "Monto1": 120.0},  # saldo final año anterior
        {**base, "Cuenta": "3I30I0", "Monto1": 120.0},  # saldo inicial año actual
        {**base, "Cuenta": "3I30IA", "Monto1": 120.0},  # saldo final año actual (igual)
    ])
    calidad = {"patrimonio_celdas_bloque_repetido": 0}
    p, _ = _patrimonio(df, calidad)
    assert len(p) == 4
    assert list(p["bloque"]) == [0, 0, 1, 1]
    assert calidad["patrimonio_celdas_bloque_repetido"] == 2


def test_mapeo_y_ratios():
    hechos = pd.DataFrame([
        # rpj, cuenta, monto, comparativo
        ("A", "1D07ST", 100.0, 80.0), ("A", "2D07ST", 18.0, 10.0), ("A", "2D01ST", 200.0, 150.0),
        ("A", "1D040T", 50.0, 40.0),
        ("B", "2F0101", 90.0, 0.0), ("B", "2F2402", 10.0, 0.0), ("B", "2F1901", 20.0, 0.0),
    ], columns=["rpj", "cuenta", "monto", "monto_comparativo"])
    hechos = hechos.assign(ejercicio=2024, periodo="A", tipo="I", monto_acumulado=float("nan"))
    mapeo = leer_mapeo(Path(__file__).resolve().parents[1] / "mapeo" / "mapeo_cuentas.csv")
    est = conceptos(hechos, mapeo)
    v = est.set_index(["rpj", "concepto"])
    # Banco: ingresos = intereses + servicios (propuesto, no validado)
    assert v.loc[("B", "ingresos"), "valor"] == 100
    assert v.loc[("B", "ingresos"), "confianza"] == "propuesto"
    r = ratios(est).set_index(["rpj", "ratio"])
    assert r.loc[("A", "roe"), "valor"] == pytest.approx(18 / 90)  # sobre patrimonio promedio
    assert r.loc[("A", "margen_neto"), "confianza"] == "directo"
    # El margen del banco depende de 'ingresos' propuesto -> hereda la confianza más baja
    assert r.loc[("B", "margen_neto"), "confianza"] == "propuesto"


def test_control_cruzado_compara_de_verdad():
    from smv.estandar import control_cruzado
    est = pd.DataFrame([{"rpj": "A", "ejercicio": 2024, "periodo": "A", "tipo": "I",
                         "concepto": "activo_total", "valor": 100.0}])
    pres = pd.DataFrame([{"rpj": "A", "ejercicio": 2024, "periodo": "A", "tipo": "I",
                          "smv_activo_total": 105.0}])
    dif, n = control_cruzado(est, pres)
    assert n == 1 and len(dif) == 1
    # Claves con tipos distintos (texto vs número) no deben pasar como "0 discrepancias"
    with pytest.raises(ValueError):
        control_cruzado(est, pres.assign(ejercicio="2024"))


def test_ejercicio_se_normaliza_a_entero():
    df = pd.DataFrame([{**sim.FILAS[0], "Ejercicio": "2024", "_operacion": "obtener_GanciaPerdida"}])
    assert limpiar(df)["Ejercicio"].iloc[0] == 2024
