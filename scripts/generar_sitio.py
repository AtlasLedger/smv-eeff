"""Genera páginas estáticas por empresa, el directorio y el sitemap del sitio.

El explorador de index.html carga los datos con JavaScript, así que los buscadores no ven
ninguna empresa. Estas páginas son HTML plano, una por empresa, para que cada búsqueda
del tipo "estados financieros <empresa>" pueda llegar al sitio.

Uso: python scripts/generar_sitio.py --data data --salida _sitio
"""
from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

URL_BASE = "https://atlasledger.github.io/smv-eeff/"
REPO = "https://github.com/AtlasLedger/smv-eeff"
DOI = "https://doi.org/10.5281/zenodo.22981480"
LARGO_MAXIMO_SLUG = 80
VACIO = "—"

TITULOS_TIPO = {"C": "Estados consolidados", "I": "Estados individuales"}
COLUMNAS_TABLA = [
    ("ejercicio", "Año", "texto"),
    ("moneda", "Moneda", "texto"),
    ("activo_total", "Activo total", "monto"),
    ("patrimonio_total", "Patrimonio", "monto"),
    ("ingresos", "Ingresos", "monto"),
    ("utilidad_neta", "Utilidad neta", "monto"),
    ("ratio_roe", "ROE", "ratio"),
    ("ratio_margen_neto", "Margen neto", "ratio"),
]
CIFRAS_CLAVE = [
    ("activo_total", "Activo total"),
    ("patrimonio_total", "Patrimonio"),
    ("ingresos", "Ingresos"),
    ("utilidad_neta", "Utilidad neta"),
]

CSS = """
:root{--ink:#1d1d1f;--muted:#6e6e73;--faint:#86868b;--bg:#fff;--soft:#f5f5f7;
--line:rgba(0,0,0,.08);--accent:#0071e3;--neg:#c9342b}
*{box-sizing:border-box}
body{margin:0;color:var(--ink);background:var(--bg);font-family:Inter,-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",sans-serif;
font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.shell{width:min(1080px,calc(100% - 32px));margin-inline:auto}
.topbar{position:sticky;top:0;z-index:5;border-bottom:1px solid var(--line);background:rgba(255,255,255,.9);backdrop-filter:blur(16px)}
.topbar-inner{min-height:60px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{display:inline-flex;align-items:center;gap:10px;color:var(--ink);font-weight:700}
.brand:hover{text-decoration:none}
.brand-mark{width:30px;height:30px;display:grid;place-items:center;border-radius:8px;color:#fff;background:#1d1d1f}
.brand-mark svg{width:17px;height:17px}
.brand small{display:block;color:var(--faint);font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;line-height:1.05}
.brand strong{display:block;font-size:.88rem}
nav{display:flex;gap:4px}
nav a{padding:8px 11px;border-radius:999px;color:var(--muted);font-size:.8rem;font-weight:500}
nav a:hover{color:var(--ink);background:var(--soft);text-decoration:none}
main{padding:28px 0 56px}
.migas{margin:0 0 20px;color:var(--faint);font-size:.8rem}
.migas a{color:var(--muted)}
h1{margin:0 0 8px;font-size:clamp(1.7rem,4vw,2.4rem);line-height:1.1;letter-spacing:-.03em;overflow-wrap:anywhere}
h2{margin:40px 0 14px;font-size:1.25rem;letter-spacing:-.02em}
.ficha{margin:0 0 28px;color:var(--muted)}
.cifras{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:0;padding:0;list-style:none}
.cifras li{padding:18px;border-radius:18px;background:var(--soft)}
.cifras span{display:block;color:var(--faint);font-size:.75rem}
.cifras strong{display:block;margin-top:4px;font-size:1.3rem;letter-spacing:-.02em;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.nota{color:var(--faint);font-size:.8rem}
.tabla{overflow-x:auto;border:1px solid var(--line);border-radius:16px}
table{width:100%;border-collapse:collapse;font-size:.85rem;font-variant-numeric:tabular-nums}
th,td{padding:9px 14px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){text-align:left}
th{position:sticky;top:0;color:var(--muted);background:var(--soft);font-weight:600;font-size:.75rem}
tr:last-child td{border-bottom:0}
td.neg{color:var(--neg)}
.bloque{margin-top:40px;padding:22px;border-radius:18px;background:var(--soft)}
.bloque h2{margin-top:0}
.bloque ul{margin:0;padding-left:18px}
.cita{margin:14px 0 0;font-size:.85rem;color:var(--muted)}
.letras{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 24px}
.letras a{min-width:32px;padding:4px 8px;border-radius:8px;background:var(--soft);text-align:center;font-weight:600}
.grupo{margin:0;padding:0;list-style:none;columns:2 320px;column-gap:32px}
.grupo li{break-inside:avoid;padding:6px 0;border-bottom:1px solid var(--line)}
.grupo small{display:block;color:var(--faint);font-size:.72rem}
footer{padding:28px 0 40px;border-top:1px solid var(--line);color:var(--faint);font-size:.8rem}
@media (max-width:760px){.cifras{grid-template-columns:repeat(2,minmax(0,1fr))}nav a{padding:8px}}
@media (max-width:420px){.brand>span:last-child{display:none}}
"""

MARCA_SVG = (
    '<svg viewBox="0 0 24 24" fill="none"><path d="M4 18.5 10.2 5l3.1 6.6L16.4 5 22 18.5" '
    'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M6.8 14.2h12.3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
)


def slug(nombre: str) -> str:
    texto = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode().lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    if len(texto) > LARGO_MAXIMO_SLUG:
        corte = texto.rfind("-", 0, LARGO_MAXIMO_SLUG)
        texto = texto[:corte] if corte > 0 else texto[:LARGO_MAXIMO_SLUG]
    return texto


def asignar_slugs(resumen: pd.DataFrame) -> dict[str, str]:
    """Slug por rpj, con el nombre más reciente; si dos rpj chocan, todos llevan su rpj."""
    nombres = nombres_recientes(resumen)
    base = {rpj: slug(nombre) for rpj, nombre in nombres.items()}
    repetidos = pd.Series(base).value_counts()
    repetidos = set(repetidos[repetidos > 1].index)
    return {rpj: f"{s}-{rpj.lower()}" if s in repetidos else s for rpj, s in base.items()}


def nombres_recientes(resumen: pd.DataFrame) -> dict[str, str]:
    ultimo = resumen.sort_values("ejercicio").groupby("rpj").tail(1)
    return dict(zip(ultimo["rpj"], ultimo["nombre"].str.strip()))


def _vacio(valor) -> bool:
    return valor is None or (isinstance(valor, float) and pd.isna(valor)) or valor == ""


def formato_monto(valor) -> str:
    return VACIO if _vacio(valor) else f"{round(float(valor)):,}"


def formato_ratio(valor) -> str:
    return VACIO if _vacio(valor) else f"{float(valor) * 100:.1f} %"


def oracion(texto) -> str:
    if _vacio(texto):
        return ""
    texto = str(texto).strip().lower()
    return texto[:1].upper() + texto[1:]


def _encabezado(raiz: str) -> str:
    return f"""<header class="topbar"><div class="shell topbar-inner">
<a class="brand" href="{raiz}" aria-label="AtlasLedger, inicio"><span class="brand-mark" aria-hidden="true">{MARCA_SVG}</span><span><small>AtlasLedger</small><strong>SMV · EEFF</strong></span></a>
<nav aria-label="Navegación principal"><a href="{raiz}empresa/">Empresas</a><a href="{raiz}#descargas">Descargas</a><a href="{REPO}">GitHub</a></nav>
</div></header>"""


PIE = """<footer><div class="shell">Fuente: Superintendencia del Mercado de Valores (SMV), datos abiertos, licencia ODbL 1.0. Base derivada bajo ODbL 1.0. Proyecto independiente, no afiliado a la SMV.</div></footer>"""


def _documento(titulo: str, descripcion: str, canonica: str, raiz: str, cuerpo: str) -> str:
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#ffffff">
<title>{html.escape(titulo)}</title>
<meta name="description" content="{html.escape(descripcion)}">
<link rel="canonical" href="{canonica}">
<style>{CSS}</style>
</head>
<body>
{_encabezado(raiz)}
<main class="shell">
{cuerpo}
</main>
{PIE}
</body>
</html>
"""


def _celda(valor, formato: str) -> str:
    if formato == "texto":
        return f"<td>{VACIO if _vacio(valor) else html.escape(str(valor))}</td>"
    texto = formato_monto(valor) if formato == "monto" else formato_ratio(valor)
    negativo = not _vacio(valor) and float(valor) < 0
    return f'<td class="neg">{texto}</td>' if negativo else f"<td>{texto}</td>"


def _tabla(filas: pd.DataFrame) -> str:
    cabecera = "".join(f'<th scope="col">{t}</th>' for _, t, _ in COLUMNAS_TABLA)
    cuerpo = "".join(
        "<tr>" + "".join(_celda(fila[c], f) for c, _, f in COLUMNAS_TABLA) + "</tr>"
        for _, fila in filas.sort_values("ejercicio", ascending=False).iterrows()
    )
    return f'<div class="tabla"><table><thead><tr>{cabecera}</tr></thead><tbody>{cuerpo}</tbody></table></div>'


def pagina_empresa(filas: pd.DataFrame, nombre: str, slug_empresa: str) -> str:
    filas = filas.sort_values("ejercicio")
    anio_min, anio_max = int(filas["ejercicio"].min()), int(filas["ejercicio"].max())
    reciente = filas.iloc[-1]
    ficha = [
        f"RUC {html.escape(str(reciente['ruc']))}" if not _vacio(reciente["ruc"]) else "",
        html.escape(oracion(reciente["tipo_empresa"])),
        html.escape(oracion(reciente["sector"])),
    ]
    ficha = " · ".join(p for p in ficha if p)

    # Tipo principal: el que llega al año más reciente; a igualdad, el consolidado.
    ultimos = filas.groupby("tipo")["ejercicio"].max()
    principal = "C" if ultimos.get("C", -1) >= ultimos.get("I", -1) else "I"
    ultima = filas[filas["tipo"] == principal].iloc[-1]
    moneda = html.escape(str(ultima["moneda"])) if not _vacio(ultima["moneda"]) else ""
    cifras = "".join(
        f"<li><span>{etiqueta}</span><strong>{formato_monto(ultima[col])}</strong></li>"
        for col, etiqueta in CIFRAS_CLAVE
    )
    nombre_seguro = html.escape(nombre)
    tablas = "".join(
        f"<h2>{TITULOS_TIPO[t]}</h2>{_tabla(filas[filas['tipo'] == t])}"
        for t in ("C", "I") if (filas["tipo"] == t).any()
    )
    cuerpo = f"""<p class="migas"><a href="../../">Inicio</a> › <a href="../">Empresas</a> › {nombre_seguro}</p>
<h1>{nombre_seguro}</h1>
<p class="ficha">{ficha}</p>
<h2>Último año disponible: {int(ultima['ejercicio'])} ({TITULOS_TIPO[principal].split()[1]})</h2>
<ul class="cifras">{cifras}</ul>
<p class="nota">Montos en miles de {moneda or 'la moneda de reporte'}. En las tablas, montos en miles de la moneda de reporte de cada año.</p>
{tablas}
<section class="bloque"><h2>Descargar y citar</h2>
<ul><li><a href="../../data/csv/resumen_anual.csv">Resumen anual de todas las empresas (CSV)</a></li>
<li><a href="{REPO}">Repositorio con los datos completos y la metodología</a></li></ul>
<p class="cita">Cita: AtlasLedger (2026). smv-eeff. Zenodo. <a href="{DOI}">{DOI}</a></p></section>"""
    return _documento(
        f"{nombre}: estados financieros {anio_min}-{anio_max} | AtlasLedger",
        f"Balance, resultados y ratios de {nombre} presentados a la SMV del Perú, "
        f"{anio_min} a {anio_max}. Datos normalizados, comparables y descargables.",
        f"{URL_BASE}empresa/{slug_empresa}/",
        "../../",
        cuerpo,
    )


def _clave_orden(nombre: str) -> str:
    return unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode().upper()


def pagina_directorio(empresas: list[tuple[str, str, str]]) -> str:
    """empresas: (nombre, slug, tipo_empresa)."""
    grupos: dict[str, list[tuple[str, str, str]]] = {}
    for empresa in sorted(empresas, key=lambda e: _clave_orden(e[0])):
        inicial = _clave_orden(empresa[0])[:1]
        grupos.setdefault(inicial if inicial.isalpha() else "#", []).append(empresa)
    letras = "".join(f'<a href="#letra-{l}">{l}</a>' for l in grupos)
    secciones = "".join(
        f'<h2 id="letra-{letra}">{letra}</h2><ul class="grupo">'
        + "".join(
            f'<li><a href="{s}/">{html.escape(n)}</a><small>{html.escape(oracion(t))}</small></li>'
            for n, s, t in lista
        )
        + "</ul>"
        for letra, lista in grupos.items()
    )
    cuerpo = f"""<p class="migas"><a href="../">Inicio</a> › Empresas</p>
<h1>Empresas supervisadas por la SMV</h1>
<p class="ficha">{len(empresas)} empresas con estados financieros anuales. Cada página muestra su historia de balance, resultados y ratios.</p>
<nav class="letras" aria-label="Índice por letra">{letras}</nav>
{secciones}"""
    return _documento(
        "Empresas supervisadas por la SMV: directorio | AtlasLedger",
        f"Directorio de {len(empresas)} empresas supervisadas por la SMV del Perú con sus "
        "estados financieros normalizados y descargables.",
        f"{URL_BASE}empresa/",
        "../",
        cuerpo,
    )


def sitemap(slugs: list[str], fecha: str) -> str:
    urls = [URL_BASE, f"{URL_BASE}empresa/"] + [f"{URL_BASE}empresa/{s}/" for s in sorted(slugs)]
    entradas = "".join(f"<url><loc>{u}</loc><lastmod>{fecha}</lastmod></url>\n" for u in urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entradas}</urlset>\n"
    )


def generar(resumen: pd.DataFrame, metadatos: dict, salida: Path) -> int:
    salida = Path(salida)
    slugs = asignar_slugs(resumen)
    nombres = nombres_recientes(resumen)
    directorio = []
    for rpj, filas in resumen.groupby("rpj"):
        s = slugs[rpj]
        carpeta = salida / "empresa" / s
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "index.html").write_text(pagina_empresa(filas, nombres[rpj], s), encoding="utf-8")
        tipo = filas.sort_values("ejercicio")["tipo_empresa"].iloc[-1]
        directorio.append((nombres[rpj], s, "" if _vacio(tipo) else tipo))
    (salida / "empresa" / "index.html").write_text(pagina_directorio(directorio), encoding="utf-8")
    fecha = str(metadatos.get("construido_utc", ""))[:10]
    (salida / "sitemap.xml").write_text(sitemap(list(slugs.values()), fecha), encoding="utf-8")
    return len(directorio)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--salida", type=Path, default=Path("_sitio"))
    args = parser.parse_args()
    resumen = pd.read_csv(
        args.data / "csv" / "resumen_anual.csv", encoding="utf-8-sig", dtype={"ruc": str, "rpj": str}
    )
    metadatos = json.loads((args.data / "metadatos.json").read_text(encoding="utf-8"))
    n = generar(resumen, metadatos, args.salida)
    print(f"{n} páginas de empresa + directorio + sitemap en {args.salida}")


if __name__ == "__main__":
    main()
