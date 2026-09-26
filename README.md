# smv-eeff

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22981480.svg)](https://doi.org/10.5281/zenodo.22981480)

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
  nivel de confianza (`directo` o `validado`). Las decisiones de criterio
  contable están en un CSV que cualquiera puede revisar.

Consulta en línea: https://atlasledger.github.io/smv-eeff/

## Qué contiene

- Estados financieros de **682 empresas** (balance, resultados, flujo de efectivo y otro
  resultado integral) de **2000 a 2026**, anuales y trimestrales, individuales y
  consolidados: unos 9.1 millones de montos por cuenta.
- Una capa de conceptos comparables y 12 ratios estándar.
- Una tabla de cambios en comparativos: cifras que una empresa modificó al volver a
  presentarlas al año siguiente (reexpresiones y reclasificaciones).
- El estado de cambios en el patrimonio (anual). Su saldo final coincide con el patrimonio
  del balance en 96 % a 100 % de los casos según el plan de cuentas.

## Estado

| paso | estado |
|---|---|
| Extracción con caché | listo |
| Limpieza y modelo dimensional | listo |
| Mapeo entre planes de cuentas | listo; decisiones de criterio documentadas |
| Validación contra estados publicados | 5 empresas, 177 cifras (2017 a 2024) |
| Publicación y actualización mensual | publicada; se actualiza sola cada mes |

## Qué tan confiable es

- Los totales de activo, pasivo, patrimonio y utilidad neta se cruzan contra el índice
  que publica la propia SMV en cada período (y los ingresos donde la definición es la
  misma): 208,788 comparaciones y 5 diferencias, todas
  anomalías de la fuente documentadas. Ese cruce detectó, por ejemplo, que las sociedades
  agentes de bolsa reportaban en soles y no en miles en los años antiguos; la base lo
  corrige y lo registra.
- En los años antiguos se verifica que utilidad antes de impuestos + impuesto = resultado
  antes de partidas extraordinarias: se cumple en 99.9 % de las presentaciones.
- En cada presentación se verifica que activo = pasivo + patrimonio (más las partidas que
  las plantillas antiguas ponían entre ambos, como el interés minoritario): cuadran todas
  salvo 3 de unas 48,000, también anomalías de la fuente.
- Contra estados financieros publicados por las propias empresas: Alicorp (consolidado
  2024, incluidos trimestres), BCP (banco, individual 2024), Credicorp (conglomerado,
  consolidado 2017 a 2024), Buenaventura (en dólares, 2017 a 2024) y Rimac (seguros,
  2024). 173 cifras coinciden y 4 difieren por razones documentadas (dos diferencias de
  presentación y un error de signo en el XBRL que Buenaventura presentó a la SEC).
  Para Credicorp y Buenaventura la fuente es la información XBRL que presentan a la SEC. Detalle en
  [validacion/reporte.md](validacion/reporte.md).
- Los conceptos marcados como `validado` dependen de una decisión de criterio contable
  (por ejemplo, qué cuenta como ingreso de un banco). Cada decisión, la evidencia que la
  respalda y su impacto están en [mapeo/DECISIONES.md](mapeo/DECISIONES.md).

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

El detalle de cada tabla y campo está en [docs/diccionario.md](docs/diccionario.md), hay
ejemplos en pandas y SQL (DuckDB) en [docs/ejemplos.md](docs/ejemplos.md) y las reglas de
mapeo están en [mapeo/](mapeo/).

## Cosas que conviene saber de la fuente

Estos son problemas de la data original que la base corrige o documenta. Cada uno está
explicado con más detalle en [BITACORA.md](BITACORA.md).

- **Montos en miles** de la moneda de reporte. Unas 30 empresas reportan en dólares; la
  base no convierte monedas.
- **Escala mixta en años antiguos.** Hasta 2011, las sociedades agentes de bolsa
  reportaban las líneas de total en soles y el detalle en miles, dentro del mismo estado.
  Se detecta contra el índice de la SMV y se corrige.
- **Mismos códigos, otro significado.** Las plantillas previas a NIIF (hasta 2009 en el
  plan general, más tarde en bancos, seguros y AFP) reutilizan códigos de cuenta con otro
  contenido; por ejemplo, la utilidad antes de impuestos se reportaba antes de la
  participación de los trabajadores. El mapeo tiene vigencia por años.
- **Planes de cuentas.** Seis actuales (empresas, bancos, seguros, AFP, sociedades agentes
  de bolsa y CAVALI) y tres letras antiguas (B, S y C en 2005). En bancos, el estado
  consolidado usa una plantilla distinta del individual.
- **Trimestres.** En resultados, la SMV entrega el trimestre aislado y el acumulado; en el
  flujo de efectivo, solo el acumulado. En los resultados trimestrales de las sociedades
  agentes de bolsa, la cifra "del trimestre" corresponde a otro subperíodo; la base
  conserva solo el acumulado.
- **Encoding roto en origen** (por ejemplo "D lares"): la letra ya viene perdida, así que se
  repara con un diccionario explícito.
- **Interés minoritario fuera del patrimonio** en las plantillas antiguas (hasta 2005 en
  el plan general y hasta 2010 en bancos y seguros): iba entre el pasivo y el patrimonio.
- **Brechas conocidas:** los bancos no desglosan la cartera por situación antes de 2006;
  en el estado de cambios en el patrimonio de las sociedades agentes de
  bolsa 2000-2005 la fila de saldo final viene vacía en la fuente.
- **Detalles menores:** identificadores con espacios de relleno, RUC = 0 en holdings
  extranjeros, una empresa que presentó el mismo estado en dos plantillas y el servicio
  `obtener_EFData`, que siempre devuelve 0 registros.
- Algunas partidas se clasifican distinto en el formato SBS que en el estado auditado NIIF
  (por ejemplo, la prima al fondo de seguro de depósitos o el efectivo restringido).

## Cómo citar

AtlasLedger (2026). *smv-eeff: estados financieros normalizados de empresas supervisadas
por la SMV (Perú), 2000-2026*. Zenodo. https://doi.org/10.5281/zenodo.22981480

Ese DOI siempre apunta a la versión más reciente. Para citar una versión exacta, la v1.0.0
es https://doi.org/10.5281/zenodo.22981481.

## Fuente y licencia

Fuente de los datos: Superintendencia del Mercado de Valores (SMV), portal de datos
abiertos, publicados bajo la Open Data Commons Open Database License (ODbL) 1.0.

La base derivada se publica bajo la misma licencia, ODbL 1.0
(https://opendatacommons.org/licenses/odbl/1-0/), con atribución a la SMV. El código se
publica bajo licencia MIT. Ver [LICENSE](LICENSE) y [LICENSE-DATA.md](LICENSE-DATA.md).

Este proyecto no está afiliado a la SMV.
