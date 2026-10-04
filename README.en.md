# smv-eeff

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22981480.svg)](https://doi.org/10.5281/zenodo.22981480)

*Versión en español: [README.md](README.md)*

An open, clean and comparable database of the financial statements that companies supervised
by Peru's securities regulator (SMV, Superintendencia del Mercado de Valores) file every
quarter.

The SMV already publishes this information on its open data portal. What this project adds is
the work needed on top of it to make it usable:

- **Cleaning.** Fixes broken text encoding in the source, padded identifiers and sentinel
  values (for example, RUC = 0).
- **Dimensional model.** Splits companies, accounts and amounts into small Parquet tables.
- **Comparability.** The SMV uses six different charts of accounts (general companies, banks,
  insurers, pension fund managers, securities brokers and CAVALI) and, for banks, a separate
  template for consolidated statements. The project maps them to a common set of concepts
  (total assets, revenue, net income, etc.) and computes 12 standard ratios.
- **Traceability.** Every concept records which SMV accounts it sums and its confidence level
  (`directo` or `validado`). Accounting judgment calls are in a CSV anyone can review.

Online: https://atlasledger.github.io/smv-eeff/en/ (the interactive explorer and the company
pages are in Spanish).

## What it contains

- Financial statements of **682 companies** (balance sheet, income statement, cash flow and
  other comprehensive income) from **2000 to 2026**, annual and quarterly, individual and
  consolidated: about 9.1 million amounts by account.
- A layer of comparable concepts and 12 standard ratios.
- A table of changes in comparatives: figures a company changed when it re-filed them the
  following year (restatements and reclassifications).
- The annual statement of changes in equity.

All amounts are in **thousands** of the reporting currency (PEN or USD). The database does not
convert currencies. Column names are in Spanish; see the data dictionary
([docs/diccionario.md](docs/diccionario.md), Spanish) and the common keys below.

| field | meaning |
|---|---|
| `rpj` | Company code in the SMV registry (primary key; the RUC is not usable because foreign holdings have none) |
| `ejercicio` | Fiscal year |
| `periodo` | `A` annual (audited), `1` to `4` quarters (unaudited) |
| `tipo` | `I` individual, `C` consolidated |
| `plan` | Chart of accounts: `D` companies, `F` banks, `E` insurers, `A` pension funds, `I` brokers, `V` CAVALI |

## How reliable it is

- Totals of assets, liabilities, equity and net income are cross-checked against the index the
  SMV itself publishes for each period (and revenue where the definition matches): 208,788
  comparisons and 5 differences, all documented anomalies of the source.
- The balance identity (assets = liabilities + equity) holds in all filings except 3 out of
  about 48,000, also source anomalies.
- Against statements published by the companies themselves (Alicorp, BCP, Credicorp,
  Buenaventura and Rimac): 173 figures match and 4 differ for documented reasons. Details in
  [validacion/reporte.md](validacion/reporte.md) (Spanish).
- Concepts marked `validado` depend on an accounting judgment (for example, what counts as
  revenue for a bank). Each decision, its evidence and its impact are in
  [mapeo/DECISIONES.md](mapeo/DECISIONES.md) (Spanish). Another analyst could choose
  differently.

## Known limits

- Only companies that report to the SMV; not every company in Peru.
- The source quality rules: banks have no loan breakdown by status before 2006, and the final
  balance row of the equity statement is empty in the source for brokers in 2000-2005.
- Older templates reuse account codes with a different meaning; the mapping is year-aware.

## Quick use

```python
import pandas as pd

anual = pd.read_csv("data/csv/resumen_anual.csv", encoding="utf-8-sig")
banks = anual[(anual.plan == "F") & (anual.tipo == "I") & (anual.periodo == "A")]
roe = banks.pivot_table(index="ejercicio", columns="nombre", values="ratio_roe")
```

More examples with pandas and SQL (DuckDB): [docs/ejemplos.md](docs/ejemplos.md).

## Where to find it

- Site: https://atlasledger.github.io/smv-eeff/ (English summary at `/en/`)
- Kaggle: https://www.kaggle.com/datasets/atlasledger/peru-smv-financial-statements
- Hugging Face: https://huggingface.co/datasets/AtlasLedger/smv-eeff
- Listed in awesome-public-datasets (Finance).

The Kaggle and Hugging Face copies are refreshed by hand; the up-to-date version is the one in
this repository, which is updated automatically every month.

## How to cite

AtlasLedger (2026). *smv-eeff: normalized financial statements of companies supervised by the
SMV (Peru), 2000-2026*. Zenodo. https://doi.org/10.5281/zenodo.22981480

That DOI always points to the latest version.

## Source and license

Data source: Superintendencia del Mercado de Valores (SMV), open data portal, published under
the Open Data Commons Open Database License (ODbL) 1.0. The derived database is published
under the same license, ODbL 1.0 (https://opendatacommons.org/licenses/odbl/1-0/), with
attribution to the SMV. The code is MIT licensed. See [LICENSE](LICENSE) and
[LICENSE-DATA.md](LICENSE-DATA.md).

This project is independent and not affiliated with the SMV.
