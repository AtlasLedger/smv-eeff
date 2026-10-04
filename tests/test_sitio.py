import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from generar_sitio import asignar_slugs, generar, slug  # noqa: E402


def _fila(rpj, nombre, ejercicio, tipo, **montos):
    base = {
        "rpj": rpj, "nombre": nombre, "ruc": "20100055237", "tipo_empresa": "EMPRESAS EMISORAS",
        "sector": "INDUSTRIALES", "ejercicio": ejercicio, "tipo": tipo, "moneda": "PEN",
        "activo_total": 1000.0, "patrimonio_total": 400.0, "ingresos": 900.0,
        "utilidad_neta": -12.0, "ratio_roe": 0.137, "ratio_margen_neto": None,
    }
    base.update(montos)
    return base


def test_slug_quita_tildes_y_signos():
    assert slug("COMPAÑIA DE MINAS BUENAVENTURA S.A.A.") == "compania-de-minas-buenaventura-s-a-a"


def test_slug_largo_se_corta_en_guion():
    s = slug("PALABRA " * 20)
    assert len(s) <= 80 and not s.endswith("-") and s.endswith("palabra")


def test_colision_agrega_rpj_a_todos():
    resumen = pd.DataFrame([_fila("B30002", "LAIVE S A", 2020, "I"), _fila("CI0011", "LAIVE S.A.", 2021, "I")])
    slugs = asignar_slugs(resumen)
    assert slugs == {"B30002": "laive-s-a-b30002", "CI0011": "laive-s-a-ci0011"}


def test_generar_sitio_minimo(tmp_path):
    resumen = pd.DataFrame([
        _fila("A1", "ALFA & BETA S.A.", 2020, "I"),
        _fila("A1", "ALFA & BETA S.A.", 2021, "I"),
        _fila("A1", "ALFA & BETA S.A.", 2021, "C", activo_total=12231540.4),
        _fila("B2", "OTRA S.A.C.", 2019, "I", ruc=None),
    ])
    n = generar(resumen, {"construido_utc": "2026-09-26T17:45:58+00:00"}, tmp_path)
    assert n == 2
    assert (tmp_path / "empresa" / "index.html").exists()
    pagina = (tmp_path / "empresa" / "alfa-beta-s-a" / "index.html").read_text(encoding="utf-8")
    assert (tmp_path / "empresa" / "otra-s-a-c" / "index.html").exists()
    sitemap = (tmp_path / "sitemap.xml").read_text(encoding="utf-8")
    assert sitemap.count("<url>") == 5 and "<lastmod>2026-09-26</lastmod>" in sitemap
    titulo = re.search(r"<title>(.*?)</title>", pagina).group(1)
    assert "—" not in titulo and "2020-2021" in titulo
    assert "ALFA &amp; BETA" in pagina and "ALFA & BETA" not in pagina
    assert "Estados consolidados" in pagina and "Estados individuales" in pagina
    assert pagina.index("Estados consolidados") < pagina.index("Estados individuales")
    assert "12,231,540" in pagina and "13.7 %" in pagina and 'class="neg">-12' in pagina
    otra = (tmp_path / "empresa" / "otra-s-a-c" / "index.html").read_text(encoding="utf-8")
    assert "RUC" not in otra
