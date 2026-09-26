# Validación contra cifras publicadas por las empresas

Montos en miles de la moneda de reporte. Tolerancia: 1 (redondeo).

Resultado: {'ok': 64, 'diferencia explicada': 2}

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

## COMPAÑIA DE MINAS BUENAVENTURA S.A.A.

Fuente: https://data.sec.gov/api/xbrl/companyfacts/CIK0001013131.json (Form 20-F 2024, XBRL)

| período | concepto | campo | publicado | base | diferencia | resultado | confianza |
|---|---|---|---:|---:|---:|---|---|
| 2024-A-C | ingresos | valor | 1,154,605 | 1,154,605 | 0 | ok | directo |
| 2024-A-C | utilidad_neta | valor | 416,263 | 416,263 | 0 | ok | directo |
| 2024-A-C | utilidad_antes_impuestos | valor | 573,449 | 573,449 | 0 | ok | directo |
| 2024-A-C | activo_total | valor | 5,047,903 | 5,047,903 | 0 | ok | directo |
| 2024-A-C | pasivo_total | valor | 1,488,202 | 1,488,202 | 0 | ok | directo |
| 2024-A-C | patrimonio_total | valor | 3,559,701 | 3,559,701 | 0 | ok | directo |
| 2024-A-C | activo_corriente | valor | 838,362 | 838,362 | 0 | ok | directo |
| 2024-A-C | pasivo_corriente | valor | 479,738 | 479,738 | 0 | ok | directo |
| 2024-A-C | efectivo | valor | 478,435 | 478,435 | 0 | ok | directo |
| 2024-A-C | utilidad_bruta | valor | 359,287 | 359,287 | 0 | ok | directo |
| 2024-A-C | impuesto_renta | valor | -156,164 | -156,164 | 0 | ok | directo |
| 2024-A-C | gastos_financieros | valor | -65,397 | -65,397 | 0 | ok | directo |
| 2024-A-C | ingresos_financieros | valor | 12,528 | 12,528 | 0 | ok | directo |

## CREDICORP LTD.

Fuente: https://data.sec.gov/api/xbrl/companyfacts/CIK0001001290.json (Form 20-F 2024, XBRL)

| período | concepto | campo | publicado | base | diferencia | resultado | confianza |
|---|---|---|---:|---:|---:|---|---|
| 2024-A-C | activo_total | valor | 256,088,940 | 256,088,940 | 0 | ok | directo |
| 2024-A-C | pasivo_total | valor | 221,111,706 | 221,111,706 | 0 | ok | directo |
| 2024-A-C | patrimonio_total | valor | 34,977,234 | 34,977,234 | 0 | ok | directo |
| 2024-A-C | utilidad_neta | valor | 5,623,252 | 5,623,252 | 0 | ok | directo |
| 2024-A-C | utilidad_antes_impuestos | valor | 7,824,527 | 7,824,527 | 0 | ok | directo |
| 2024-A-C | impuesto_renta | valor | -2,201,275 | -2,201,275 | 0 | ok | directo |
| 2024-A-C | ingresos_intereses | valor | 19,869,256 | 19,869,256 | 0 | ok | directo |
| 2024-A-C | gastos_intereses | valor | -5,754,125 | -5,754,125 | 0 | ok | directo |
| 2024-A-C | efectivo | valor | 47,570,103 | 47,655,196 | 85,093 | diferencia explicada | propuesto |

Diferencia explicada en `efectivo`: El efectivo NIIF excluye el efectivo restringido (85,093); el rubro Disponible del formato SBS lo incluye. Refuerza que efectivo de bancos quede como propuesto.

## RIMAC SEGUROS Y REASEGUROS

Fuente: https://imagescdn.rimac.com/bltcc080c5219b7e019/67e2e59ec0d1f261140a49e8/Informe_auditado_de_Rimac_Seguros_y_Reaseguros_31.12.24-23_V.Vinal.pdf

| período | concepto | campo | publicado | base | diferencia | resultado | confianza |
|---|---|---|---:|---:|---:|---|---|
| 2024-A-I | activo_total | valor | 21,513,476 | 21,513,476 | 0 | ok | directo |
| 2024-A-I | pasivo_total | valor | 18,454,554 | 18,454,554 | 0 | ok | directo |
| 2024-A-I | patrimonio_total | valor | 3,058,922 | 3,058,922 | 0 | ok | directo |
| 2024-A-I | efectivo | valor | 673,565 | 673,565 | 0 | ok | directo |
| 2024-A-I | primas_ganadas_netas | valor | 3,320,376 | 3,320,376 | 0 | ok | directo |
| 2024-A-I | siniestros_netos | valor | -1,853,374 | -1,853,374 | 0 | ok | directo |
| 2024-A-I | utilidad_antes_impuestos | valor | 447,798 | 447,798 | 0 | ok | directo |
| 2024-A-I | impuesto_renta | valor | 0 | 0 | 0 | ok | directo |
| 2024-A-I | utilidad_neta | valor | 447,798 | 447,798 | 0 | ok | directo |
| 2024-A-I | activo_total | valor_comparativo | 20,143,246 | 20,143,246 | 0 | ok | directo |
| 2024-A-I | utilidad_neta | valor_comparativo | 424,623 | 424,623 | 0 | ok | directo |
