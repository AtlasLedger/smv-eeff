# smv-eeff

Extractor de los estados financieros publicados por la SMV (Superintendencia del Mercado de Valores del Perú) a través de su servicio de datos abiertos. Paso 1 de un proyecto para construir una base normalizada y comparable de esa información.

Fuente: SMV, datos abiertos, licencia Open Data Commons Open Database License (ODbL).

## Estado

Paso 1 (extracción con caché y perfil de calidad). Aún no hay normalización ni mapeo entre planes de cuentas.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
# Descargar estado de resultados 2024, anual, individual
python scripts/extraer.py --op resultados --anios 2024 --periodos A --tipos I

# Generar el perfil de calidad (queda en reportes/)
python scripts/perfilar.py --op resultados --anio 2024 --periodo A --tipo I

# Pruebas (usan un servidor simulado, no tocan la SMV)
pytest -q
```

Operaciones disponibles (`--op`): `balance`, `resultados`, `flujo`, `patrimonio`, `integrales`, `indice`, `efdata`, o `todas`.

Solo `resultados` e `indice` se han verificado contra el servicio real. Los parámetros de `efdata` en particular no están confirmados.

## Cómo funciona el caché

Cada respuesta se guarda cruda y comprimida en `cache/raw/<operacion>/<año>/<periodo>_<tipo>.xml.gz`, con un `.json` al lado (fecha de descarga, tamaño, SHA-256, filas). Si una combinación ya está en caché no se vuelve a pedir; `--refrescar` fuerza la descarga. Si el proceso se corta, al volver a correrlo continúa donde se quedó.
