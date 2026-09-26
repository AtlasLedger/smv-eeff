# Validación contra cifras publicadas por las empresas

Montos en miles de la moneda de reporte. Tolerancia: 1 (redondeo).

Resultado: {'ok': 32, 'diferencia explicada': 1}

## ALICORP S.A.A.

Fuente: https://www.alicorp.com.pe/media/conference_calls/alicorp_earnings_report_4q24_es_vf.pdf

| período | concepto | campo | publicado | base | diferencia | resultado | confianza |
|---|---|---|---:|---:|---:|---|---|
| 2024-A-C | ingresos | valor | 10,598,328 | 10,598,328 | 0 | ok | directo |
| 2024-A-C | utilidad_bruta | valor | 2,864,867 | 2,864,867 | 0 | ok | directo |
| 2024-A-C | utilidad_operativa | valor | 1,076,315 | 1,076,315 | 0 | ok | directo |
| 2024-A-C | ingresos_financieros | valor | 76,433 | 76,433 | 0 | ok | directo |
| 2024-A-C | gastos_financieros | valor | -341,173 | -341,173 | 0 | ok | directo |
| 2024-A-C | utilidad_antes_impuestos | valor | 802,262 | 802,262 | 0 | ok | directo |
| 2024-A-C | impuesto_renta | valor | -256,252 | -256,252 | 0 | ok | directo |
| 2024-A-C | utilidad_neta | valor | 350,460 | 350,460 | 0 | ok | directo |
| 2024-A-C | ingresos | valor_comparativo | 11,039,113 | 11,039,113 | 0 | ok | directo |
| 2024-A-C | utilidad_neta | valor_comparativo | 195,935 | 195,935 | 0 | ok | directo |
| 2024-A-C | efectivo | valor | 1,983,599 | 1,983,599 | 0 | ok | directo |
| 2024-A-C | activo_corriente | valor | 5,183,004 | 5,183,004 | 0 | ok | directo |
| 2024-A-C | activo_total | valor | 12,231,540 | 12,231,540 | 0 | ok | directo |
| 2024-A-C | pasivo_corriente | valor | 5,216,350 | 5,216,350 | 0 | ok | directo |
| 2024-A-C | pasivo_total | valor | 9,979,152 | 9,979,152 | 0 | ok | directo |
| 2024-A-C | patrimonio_total | valor | 2,252,388 | 2,252,388 | 0 | ok | directo |
| 2024-A-C | deuda_financiera | valor | 5,137,268 | 5,137,268 | 0 | ok | propuesto |
| 2024-A-C | activo_total | valor_comparativo | 12,917,367 | 12,917,367 | 0 | ok | directo |
| 2024-4-C | ingresos | valor | 3,052,270 | 3,052,270 | 0 | ok | directo |
| 2024-4-C | ingresos | valor_acumulado | 10,598,328 | 10,598,328 | 0 | ok | directo |
| 2024-4-C | utilidad_neta | valor | -108,405 | -108,405 | 0 | ok | directo |
| 2024-4-C | utilidad_neta | valor_acumulado | 350,460 | 350,460 | 0 | ok | directo |

## BANCO DE CREDITO DEL PERU

Fuente: https://www.smv.gob.pe/ConsultasP8/documento.aspx?vidDoc=%7B70874495-0000-CC9A-8064-11EE21229F36%7D

| período | concepto | campo | publicado | base | diferencia | resultado | confianza |
|---|---|---|---:|---:|---:|---|---|
| 2024-A-I | activo_total | valor | 195,656,310 | 195,656,310 | 0 | ok | directo |
| 2024-A-I | activo_total | valor_comparativo | 179,230,213 | 179,230,213 | 0 | ok | directo |
| 2024-A-I | pasivo_total | valor | 170,689,252 | 170,689,252 | 0 | ok | directo |
| 2024-A-I | patrimonio_total | valor | 24,967,058 | 24,967,058 | 0 | ok | directo |
| 2024-A-I | efectivo | valor | 43,923,142 | 43,923,142 | 0 | ok | propuesto |
| 2024-A-I | ingresos_intereses | valor | 14,450,779 | 14,450,779 | 0 | ok | directo |
| 2024-A-I | utilidad_antes_impuestos | valor | 6,945,406 | 6,945,406 | 0 | ok | directo |
| 2024-A-I | impuesto_renta | valor | -1,728,714 | -1,728,714 | 0 | ok | directo |
| 2024-A-I | utilidad_neta | valor | 5,216,692 | 5,216,692 | 0 | ok | directo |
| 2024-A-I | utilidad_neta | valor_comparativo | 4,664,508 | 4,664,508 | 0 | ok | directo |
| 2024-A-I | gastos_intereses | valor | -3,518,074 | -3,289,017 | 229,057 | diferencia explicada | directo |

Diferencia explicada en `gastos_intereses`: El estado auditado incluye la prima al fondo de seguro de depósitos (229,057) en gastos financieros; el formato SBS que recibe la SMV la registra en gastos por servicios financieros (2F0407).
