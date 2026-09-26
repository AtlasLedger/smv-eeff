# smv-eeff

Base de datos abierta, limpia y comparable de los estados financieros que las empresas
supervisadas por la SMV (Superintendencia del Mercado de Valores del Perú) presentan cada
trimestre.

La SMV ya publica esta información en su portal de datos abiertos. Lo que agrega este
proyecto es la capa de trabajo que hay que hacer encima para poder usarla:

- **Limpieza.** Corrige el encoding roto que viene en origen, los identificadores con
  espacios de relleno y los valores centinela (por ejemplo, RUC = 0).
- **Modelo dimensional.** Separa empresas, cuentas y montos en tablas Parquet livianas.
- **Comparabilidad.** La SMV usa seis planes de cuentas distintos (empresas en general,
  bancos, seguros, AFP, sociedades agentes de bolsa y CAVALI) y, en bancos, una plantilla
  distinta para los estados consolidados. El proyecto los lleva a un conjunto común de
  conceptos (activo total, ingresos, utilidad neta, etc.) y calcula ratios estándar.
- **Trazabilidad.** Cada concepto indica qué cuentas de la SMV lo componen y con qué
  nivel de confianza (`directo`, `validado` o `propuesto`). Las decisiones de criterio
  contable están en un CSV que cualquiera puede revisar.

## Estado

| paso | estado |
|---|---|
| Extracción con caché | listo |
| Limpieza y modelo dimensional | listo |
| Mapeo entre planes de cuentas | propuesta lista; decisiones de criterio en revisión |
| Validación contra estados publicados | 5 empresas, 100 cifras (2022 a 2024) |
| Publicación y actualización trimestral | pendiente |

## Qué tan confiable es

- Los totales de activo, pasivo, patrimonio y utilidad neta se cruzan contra el índice
  que publica la propia SMV en cada período. Ese cruce detectó, por ejemplo, que las
  sociedades agentes de bolsa reportaban en soles y no en miles en los años antiguos;
  la base lo corrige y lo registra.
- Contra estados financieros publicados por las propias empresas: Alicorp (consolidado
  2024, incluidos trimestres), BCP (banco, individual 2024), Credicorp (conglomerado,
  consolidado 2022 a 2024), Buenaventura (en dólares, 2022 a 2024) y Rimac (seguros,
  2024). 100 cifras coinciden y 2 difieren por diferencias de presentación documentadas.
  Para Credicorp y Buenaventura la fuente es la información XBRL que presentan a la SEC. Detalle en
  [validacion/reporte.md](validacion/reporte.md).
- Los conceptos marcados como `propuesto` dependen de una decisión de criterio que aún no
  se validó. Úsalos sabiendo eso.

## Uso

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1. Descargar (se guarda en cache/; lo ya descargado no se vuelve a pedir)
python scripts/extraer.py --op todas --anios 2024 --periodos A --tipos I,C

# 2. Construir las tablas (data/)
python scripts/construir.py

# 3. Validar contra cifras publicadas por las empresas
python scripts/validar.py

# Pruebas (usan un servidor simulado, no tocan la SMV)
pytest -q
```

Ejemplo con pandas:

```python
import pandas as pd

ratios = pd.read_parquet("data/ratios.parquet")
empresas = pd.read_parquet("data/empresas.parquet")
roe = (ratios.query("ratio == 'roe' and periodo == 'A' and tipo == 'C'")
             .merge(empresas[["rpj", "nombre"]], on="rpj"))
```

El detalle de cada tabla y campo está en [docs/diccionario.md](docs/diccionario.md) y
las reglas de mapeo en [mapeo/](mapeo/).

## Cosas que conviene saber de la fuente

- Montos en **miles** de la moneda de reporte. Hay empresas que reportan en dólares; la
  base no convierte monedas.
- En los trimestres, el estado de resultados trae el trimestre aislado y el acumulado
  del año. Los trimestres no son auditados; el anual sí.
- Los bancos presentan el individual en formato SBS y el consolidado en un formato de
  conglomerado financiero. Algunas partidas (por ejemplo la prima al fondo de seguro de
  depósitos) se clasifican distinto que en el estado auditado.
- El servicio `obtener_EFData` del portal devuelve siempre 0 registros y no se usa.

## Fuente y licencia

Fuente de los datos: Superintendencia del Mercado de Valores (SMV), portal de datos
abiertos, publicados bajo la Open Data Commons Open Database License (ODbL) 1.0.

La base derivada se publica bajo la misma licencia, ODbL 1.0
(https://opendatacommons.org/licenses/odbl/1-0/), con atribución a la SMV. El código se
publica bajo licencia MIT. Ver [LICENSE](LICENSE) y [LICENSE-DATA.md](LICENSE-DATA.md).

Este proyecto no está afiliado a la SMV.
