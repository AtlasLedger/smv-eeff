"""Pruebas del extractor contra el servidor simulado. Correr con: pytest -q"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import servidor_simulado as sim
from smv import CacheDisco, ClienteSMV, ErrorPermanente, ErrorSMV, cargar, descargar
from smv.cliente import construir_sobre, extraer_registros


@pytest.fixture
def entorno(tmp_path):
    srv, url = sim.iniciar()
    sim.Estado.llamadas = 0
    sim.Estado.fallos_pendientes = 0
    cliente = ClienteSMV(host=url, max_intentos=3, backoff_base=0.01)
    yield cliente, CacheDisco(tmp_path / "cache")
    srv.shutdown()


def test_sobre_tiene_parametros():
    s = construir_sobre("obtener_GanciaPerdida", 2024, "A", "I").decode()
    assert "<Ejercicio>2024</Ejercicio><Periodo>A</Periodo><Tipo>I</Tipo>" in s
    assert 'xmlns="http://tempuri.org/"' in s


def test_descarga_y_cache(entorno):
    cliente, cache = entorno
    assert descargar(cliente, cache, "resultados", 2024, "A", "I") == ("red", len(sim.FILAS))
    # Segunda vez: no toca la red
    assert descargar(cliente, cache, "resultados", 2024, "A", "I") == ("cache", len(sim.FILAS))
    assert sim.Estado.llamadas == 1
    # Refrescar sí vuelve a llamar
    descargar(cliente, cache, "resultados", 2024, "A", "I", refrescar=True)
    assert sim.Estado.llamadas == 2


def test_encoding_se_preserva_tal_cual(entorno):
    cliente, cache = entorno
    descargar(cliente, cache, "resultados", 2024, "A", "I")
    df = cargar(cache, "resultados", 2024, "A", "I")
    # Lo que llegó bien sigue bien y lo que llegó roto sigue roto (sin corrupción extra)
    assert "Ganancia (Pérdida) Bruta" in set(df["DescripcionCuenta"])
    assert "M todo Directo" in set(df["MetodoFlujoEfectivo"])


def test_reintenta_ante_500(entorno):
    cliente, cache = entorno
    sim.Estado.fallos_pendientes = 2
    assert descargar(cliente, cache, "resultados", 2024, "A", "I")[0] == "red"
    assert sim.Estado.llamadas == 3


def test_falla_tras_agotar_intentos_y_no_cachea(entorno):
    cliente, cache = entorno
    sim.Estado.fallos_pendientes = 10
    with pytest.raises(ErrorSMV):
        descargar(cliente, cache, "resultados", 2024, "A", "I")
    assert not cache.existe("resultados", 2024, "A", "I")


def test_respuesta_vacia_se_cachea_como_vacia(entorno):
    cliente, cache = entorno
    assert descargar(cliente, cache, "resultados", 2001, "1", "C") == ("red", 0)
    assert cache.leer_meta("resultados", 2001, "1", "C")["vacio"] is True


def test_parametros_invalidos():
    with pytest.raises(ErrorPermanente):
        ClienteSMV().consultar("resultados", 2024, "5", "I")
    with pytest.raises(ErrorPermanente):
        ClienteSMV().consultar("no_existe", 2024, "A", "I")


def test_xml_sin_nodo_result_no_parsea():
    with pytest.raises(ErrorSMV):
        extraer_registros(b"<html>error</html>", "obtener_GanciaPerdida")


def test_vacio_reciente_se_vuelve_a_pedir(entorno, monkeypatch):
    from datetime import datetime
    cliente, cache = entorno
    monkeypatch.setattr(sim, "FILAS", [])
    anio = datetime.now().year
    descargar(cliente, cache, "resultados", anio, "4", "I")
    descargar(cliente, cache, "resultados", anio, "4", "I")
    assert sim.Estado.llamadas == 2          # período reciente vacío: se reintenta
    descargar(cliente, cache, "resultados", 2001, "4", "I")
    descargar(cliente, cache, "resultados", 2001, "4", "I")
    assert sim.Estado.llamadas == 3          # vacío antiguo: queda en caché
