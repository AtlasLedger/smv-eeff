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
from smv.modelo import _detectar_escala, _patrimonio, _reescalar, construir


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


def test_detecta_y_corrige_totales_en_unidades():
    # SAB antiguas: los TOTALES venían en soles y el detalle en miles con decimales.
    base = {"ejercicio": 2010, "periodo": "A", "tipo": "I"}
    hechos = pd.DataFrame([
        {**base, "rpj": "SAB", "cuenta": "1I1131", "monto": 38_179_940.0},  # TOTAL ACTIVO, en soles
        {**base, "rpj": "SAB", "cuenta": "1I1010", "monto": 165.964},       # Caja y bancos, en miles
        {**base, "rpj": "OK", "cuenta": "1D020T", "monto": 5_000.0},         # otra empresa, en miles
    ])
    idx = pd.DataFrame([{**base, "rpj": "SAB", "smv_activo_total": 38_180.0},
                        {**base, "rpj": "OK", "smv_activo_total": 5_000.0}])
    esc = _detectar_escala({2010: [hechos]}, idx)
    assert list(esc["rpj"]) == ["SAB"]
    totales = {(2010, "A", "1I1131"), (2010, "A", "1D020T")}
    out = _reescalar(hechos, esc, totales).set_index("cuenta")["monto"]
    assert out["1I1131"] == pytest.approx(38_179.94)
    assert out["1I1010"] == 165.964     # el detalle ya estaba en miles
    assert out["1D020T"] == 5_000.0     # otras empresas no se tocan


def test_es_total():
    from smv.modelo import _es_total
    assert _es_total("TOTAL INGRESOS OPERACIONALES")
    assert _es_total("RESULTADO ANTES DE PARTICIP. E IMPUESTO A LA RENTA")
    assert not _es_total("Caja y bancos")
    assert not _es_total("UTILIDAD (PERDIDA) BASICA POR ACCION COMUN")
    assert not _es_total("")


def test_cuadre_balance():
    from smv.estandar import cuadre_balance
    base = {"ejercicio": 2024, "periodo": "A", "tipo": "I"}
    est = pd.DataFrame([
        {**base, "rpj": "A", "concepto": "activo_total", "valor": 100.0},
        {**base, "rpj": "A", "concepto": "pasivo_total", "valor": 60.0},
        {**base, "rpj": "A", "concepto": "patrimonio_total", "valor": 40.0},
        {**base, "rpj": "B", "concepto": "activo_total", "valor": 100.0},
        {**base, "rpj": "B", "concepto": "pasivo_total", "valor": 60.0},
        {**base, "rpj": "B", "concepto": "patrimonio_total", "valor": 30.0},
    ])
    assert list(cuadre_balance(est)["rpj"]) == ["B"]


def test_flujo_trimestral_va_a_acumulado():
    from smv.modelo import _hechos
    df = pd.DataFrame([
        {"RPJ": "A", "Ejercicio": 2025, "_periodo_consultado": "2", "_tipo_consultado": "I",
         "estado": "FE", "Cuenta": "3D0405", "Monto1": -57966.0, "Monto2": -216643.0},
        {"RPJ": "A", "Ejercicio": 2025, "_periodo_consultado": "2", "_tipo_consultado": "I",
         "estado": "ER", "Cuenta": "2D07ST", "Monto1": 170200.0, "Monto2": 190267.0,
         "Monto3": 349210.0, "Monto4": 271706.0},
    ])
    h = _hechos(df).set_index("estado")
    assert pd.isna(h.loc["FE", "monto"]) and h.loc["FE", "monto_acumulado"] == -57966.0
    assert h.loc["ER", "monto"] == 170200.0 and h.loc["ER", "monto_acumulado"] == 349210.0


def test_reglas_superpuestas_fallan(tmp_path):
    ruta = tmp_path / "mapeo.csv"
    ruta.write_text(
        "concepto,plan,tipo,desde,hasta,cuentas,confianza,nota\n"
        "utilidad_neta,D,,,,2D07ST,directo,\n"
        "utilidad_neta,D,,2000,2030,2D0503,propuesto,\n", "utf-8")
    hechos = pd.DataFrame([
        {"rpj": "A", "ejercicio": 2024, "periodo": "A", "tipo": "I", "cuenta": c, "monto": 10.0,
         "monto_comparativo": 0.0, "monto_acumulado": float("nan")} for c in ["2D07ST", "2D0503"]])
    with pytest.raises(ValueError, match="más de una regla"):
        conceptos(hechos, leer_mapeo(ruta))


def test_empresa_en_dos_planes_se_queda_con_uno():
    from smv.modelo import _un_plan_por_empresa
    base = {"RPJ": "SG0005", "TipoEmpresa": "SOCIEDADES AGENTES DE BOLSA", "Ejercicio": 2021,
            "_periodo_consultado": "1", "_tipo_consultado": "I", "_operacion": "obtener_BalanceGeneral"}
    df = pd.DataFrame([{**base, "plan": "I", "Cuenta": "1I1131"}, {**base, "plan": "I", "Cuenta": "1I1491"},
                       {**base, "plan": "D", "Cuenta": "1D020T"},
                       {**base, "RPJ": "X", "TipoEmpresa": "EMPRESAS EMISORAS", "plan": "D", "Cuenta": "1D020T"}])
    calidad = {}
    out = _un_plan_por_empresa(df, calidad)
    assert set(out[out["RPJ"] == "SG0005"]["plan"]) == {"I"}
    assert len(out[out["RPJ"] == "X"]) == 1
    assert len(calidad["presentaciones_en_dos_planes"]) == 1


def test_resultados_trimestrales_sab_sin_monto_del_trimestre():
    from smv.modelo import _hechos
    base = {"RPJ": "S", "Ejercicio": 2024, "_periodo_consultado": "1", "_tipo_consultado": "I",
            "estado": "ER", "Monto2": 1.0, "Monto3": 432.5, "Monto4": 422.7}
    df = pd.DataFrame([{**base, "plan": "I", "Cuenta": "2I2161", "Monto1": 196.3},
                       {**base, "plan": "D", "Cuenta": "2D07ST", "Monto1": 432.5}])
    h = _hechos(df).set_index("cuenta")
    assert pd.isna(h.loc["2I2161", "monto"]) and h.loc["2I2161", "monto_acumulado"] == 432.5
    assert h.loc["2D07ST", "monto"] == 432.5


def test_escala_interna_sin_indice():
    from smv.modelo import _escala_interna
    base = {"RPJ": "B80127", "Ejercicio": 2003, "_periodo_consultado": "A", "_tipo_consultado": "I"}
    antiguo = pd.DataFrame([
        {**base, "Cuenta": "1I1010", "DescripcionCuenta": "Caja y bancos", "Monto1": 908.2},
        {**base, "Cuenta": "1I1020", "DescripcionCuenta": "Valores negociables", "Monto1": 5750.9},
        {**base, "Cuenta": "1I1071", "DescripcionCuenta": "TOTAL ACTIVO CORRIENTE", "Monto1": 6_659_100.0},
        {**base, "Cuenta": "1I1131", "DescripcionCuenta": "TOTAL ACTIVOS", "Monto1": 6_659_100.0},
    ])
    assert list(_escala_interna(antiguo)["rpj"]) == ["B80127"]
    actual = pd.DataFrame([
        {**base, "RPJ": "X", "Cuenta": "1D0109", "DescripcionCuenta": "Efectivo", "Monto1": 100.0},
        {**base, "RPJ": "X", "Cuenta": "1D01ST", "DescripcionCuenta": "Total Activos Corrientes", "Monto1": 100.0},
        {**base, "RPJ": "X", "Cuenta": "1D020T", "DescripcionCuenta": "TOTAL DE ACTIVOS", "Monto1": 100.0},
    ])
    assert _escala_interna(actual).empty


def test_partida_intermedia_se_quita_si_ya_estaba_en_el_patrimonio():
    from smv.estandar import _quitar_intermedias_ya_incluidas, cuadre_balance
    base = {"ejercicio": 2010, "periodo": "A", "tipo": "C"}
    filas = []
    for rpj, pat in [("FUERA", 80.0), ("DENTRO", 90.0)]:
        filas += [{**base, "rpj": rpj, "concepto": "activo_total", "valor": 200.0},
                  {**base, "rpj": rpj, "concepto": "pasivo_total", "valor": 110.0},
                  {**base, "rpj": rpj, "concepto": "patrimonio_total", "valor": pat},
                  {**base, "rpj": rpj, "concepto": "partidas_entre_pasivo_y_patrimonio", "valor": 10.0}]
    est = _quitar_intermedias_ya_incluidas(pd.DataFrame(filas))
    inter = est[est["concepto"] == "partidas_entre_pasivo_y_patrimonio"]
    assert list(inter["rpj"]) == ["FUERA"]   # en DENTRO ya cuadraba sin la partida
    assert cuadre_balance(est).empty


def test_patrimonio_codigo_de_fila_repetido():
    # Plantilla antigua SAB: la última columna repite el código de "Saldo inicial" en todas las filas.
    base = {"RPJ": "S", "_periodo_consultado": "A", "_tipo_consultado": "I", "plan": "I"}
    filas = []
    for cod, v in [("3I3010", 100.0), ("3I3016", 20.0), ("3I301A", 120.0)]:
        filas += [{**base, "Cuenta": cod, "OrdenColumna": "1", "DescripcionColumna": "CAPITAL", "Monto1": v},
                  {**base, "Cuenta": "3I30I0", "OrdenColumna": "8", "DescripcionColumna": "Total", "Monto1": v}]
    calidad = {"patrimonio_celdas_bloque_repetido": 0}
    p, _ = _patrimonio(pd.DataFrame(filas), calidad)
    total = p[p["columna"] == 8].set_index("fila")["monto"]
    assert total.to_dict() == {"3I3010": 100.0, "3I3016": 20.0, "3I301A": 120.0}
    assert set(p.loc[p["columna"] == 8, "cuenta"]) == {"3I30I0"}   # el código original se conserva
    assert calidad["patrimonio_celdas_con_codigo_distinto_a_su_fila"] == 3


def test_identidad_resultados():
    from smv.estandar import identidad_resultados
    base = {"periodo": "A", "tipo": "I"}
    est = pd.DataFrame([
        {**base, "rpj": "V", "ejercicio": 2003, "concepto": "utilidad_antes_impuestos", "valor": 100.0},
        {**base, "rpj": "V", "ejercicio": 2003, "concepto": "impuesto_renta", "valor": -30.0},
        {**base, "rpj": "N", "ejercicio": 2024, "concepto": "utilidad_antes_impuestos", "valor": 100.0},
        {**base, "rpj": "N", "ejercicio": 2024, "concepto": "impuesto_renta", "valor": -30.0},
        {**base, "rpj": "N", "ejercicio": 2024, "concepto": "utilidad_neta", "valor": 60.0},  # no cumple
    ])
    hechos = pd.DataFrame([{**base, "rpj": "V", "ejercicio": 2003, "cuenta": "2F1501", "monto": 70.0}])
    r = identidad_resultados(est, hechos).set_index("contra")
    assert r.loc["antes_extraordinarias", "tasa"] == 1.0
    assert r.loc["utilidad_neta", "tasa"] == 0.0


def test_cambios_en_comparativos():
    from smv.estandar import cambios_en_comparativos
    est = pd.DataFrame([
        {"rpj": "A", "ejercicio": 2023, "periodo": "A", "tipo": "I", "concepto": "utilidad_neta", "valor": 100.0, "valor_comparativo": 90.0},
        {"rpj": "A", "ejercicio": 2024, "periodo": "A", "tipo": "I", "concepto": "utilidad_neta", "valor": 120.0, "valor_comparativo": 95.0},
        {"rpj": "B", "ejercicio": 2023, "periodo": "A", "tipo": "I", "concepto": "utilidad_neta", "valor": 50.0, "valor_comparativo": 40.0},
        {"rpj": "B", "ejercicio": 2024, "periodo": "A", "tipo": "I", "concepto": "utilidad_neta", "valor": 60.0, "valor_comparativo": 50.0},
    ])
    c = cambios_en_comparativos(est)
    assert list(c["rpj"]) == ["A"] and c["diferencia"].iloc[0] == -5.0
