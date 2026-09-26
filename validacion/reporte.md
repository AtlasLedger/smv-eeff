# Validación contra cifras publicadas por las empresas

Montos en miles de la moneda de reporte. Tolerancia: 1 (redondeo).

Resultado: {'ok': 173, 'diferencia explicada': 4}

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
| 2022-A-C | ingresos | valor | 824,802 | 824,802 | 0 | ok | directo |
| 2022-A-C | utilidad_neta | valor | 602,935 | 602,935 | 0 | ok | directo |
| 2022-A-C | utilidad_antes_impuestos | valor | 124,429 | 124,429 | 0 | ok | directo |
| 2022-A-C | activo_total | valor | 4,503,227 | 4,503,227 | 0 | ok | directo |
| 2022-A-C | pasivo_total | valor | 1,340,286 | 1,340,286 | 0 | ok | directo |
| 2022-A-C | patrimonio_total | valor | 3,162,941 | 3,162,941 | 0 | ok | directo |
| 2022-A-C | activo_corriente | valor | 620,380 | 620,380 | 0 | ok | directo |
| 2022-A-C | pasivo_corriente | valor | 379,597 | 379,597 | 0 | ok | directo |
| 2022-A-C | utilidad_bruta | valor | 61,329 | 61,329 | 0 | ok | directo |
| 2022-A-C | impuesto_renta | valor | -41 | -41 | 0 | ok | directo |
| 2023-A-C | ingresos | valor | 823,845 | 823,845 | 0 | ok | directo |
| 2023-A-C | utilidad_neta | valor | 32,682 | 32,682 | 0 | ok | directo |
| 2023-A-C | utilidad_antes_impuestos | valor | 82,524 | 82,524 | 0 | ok | directo |
| 2023-A-C | activo_total | valor | 4,533,799 | 4,533,799 | 0 | ok | directo |
| 2023-A-C | pasivo_total | valor | 1,364,588 | 1,364,588 | 0 | ok | directo |
| 2023-A-C | patrimonio_total | valor | 3,169,211 | 3,169,211 | 0 | ok | directo |
| 2023-A-C | activo_corriente | valor | 577,762 | 577,762 | 0 | ok | directo |
| 2023-A-C | pasivo_corriente | valor | 441,605 | 441,605 | 0 | ok | directo |
| 2023-A-C | utilidad_bruta | valor | 91,248 | 91,248 | 0 | ok | directo |
| 2023-A-C | impuesto_renta | valor | -42,994 | -42,994 | 0 | ok | directo |
| 2017-A-C | ingresos | valor | 1,274,378 | 1,274,378 | 0 | ok | directo |
| 2017-A-C | utilidad_neta | valor | 64,435 | 64,435 | 0 | ok | directo |
| 2017-A-C | utilidad_antes_impuestos | valor | 92,545 | 92,545 | 0 | ok | directo |
| 2017-A-C | activo_total | valor | 4,332,813 | 4,332,813 | 0 | ok | directo |
| 2017-A-C | pasivo_total | valor | 1,269,186 | 1,269,186 | 0 | ok | directo |
| 2017-A-C | patrimonio_total | valor | 3,063,627 | 3,063,627 | 0 | ok | directo |
| 2017-A-C | activo_corriente | valor | 701,862 | 701,862 | 0 | ok | directo |
| 2017-A-C | pasivo_corriente | valor | 521,194 | 521,194 | 0 | ok | directo |
| 2017-A-C | utilidad_bruta | valor | 294,124 | 294,124 | 0 | ok | directo |
| 2017-A-C | impuesto_renta | valor | -18,012 | -18,012 | 0 | ok | directo |
| 2018-A-C | ingresos | valor | 1,167,381 | 1,167,381 | 0 | ok | directo |
| 2018-A-C | utilidad_neta | valor | -11,654 | -11,654 | 0 | ok | directo |
| 2018-A-C | utilidad_antes_impuestos | valor | 22,475 | 22,475 | 0 | ok | directo |
| 2018-A-C | activo_total | valor | 4,217,221 | 4,217,221 | 0 | ok | directo |
| 2018-A-C | pasivo_total | valor | 1,187,656 | 1,187,656 | 0 | ok | directo |
| 2018-A-C | patrimonio_total | valor | 3,029,565 | 3,029,565 | 0 | ok | directo |
| 2018-A-C | activo_corriente | valor | 761,134 | 761,134 | 0 | ok | directo |
| 2018-A-C | pasivo_corriente | valor | 399,182 | 399,182 | 0 | ok | directo |
| 2018-A-C | utilidad_bruta | valor | 184,424 | 184,424 | 0 | ok | directo |
| 2018-A-C | impuesto_renta | valor | 26,926 | -26,926 | -53,852 | diferencia explicada | directo |
| 2019-A-C | ingresos | valor | 867,888 | 867,888 | 0 | ok | directo |
| 2019-A-C | utilidad_neta | valor | -28,459 | -28,459 | 0 | ok | directo |
| 2019-A-C | utilidad_antes_impuestos | valor | -43,535 | -43,535 | 0 | ok | directo |
| 2019-A-C | activo_total | valor | 4,107,274 | 4,107,274 | 0 | ok | directo |
| 2019-A-C | pasivo_total | valor | 1,139,074 | 1,139,074 | 0 | ok | directo |
| 2019-A-C | patrimonio_total | valor | 2,968,200 | 2,968,200 | 0 | ok | directo |
| 2019-A-C | activo_corriente | valor | 648,619 | 648,619 | 0 | ok | directo |
| 2019-A-C | pasivo_corriente | valor | 565,357 | 565,357 | 0 | ok | directo |
| 2019-A-C | utilidad_bruta | valor | 68,306 | 68,306 | 0 | ok | directo |
| 2019-A-C | impuesto_renta | valor | -25,590 | 25,590 | 51,180 | diferencia explicada | directo |
| 2021-A-C | ingresos | valor | 900,450 | 900,450 | 0 | ok | directo |
| 2021-A-C | utilidad_neta | valor | -262,804 | -262,804 | 0 | ok | directo |
| 2021-A-C | utilidad_antes_impuestos | valor | 101,129 | 101,129 | 0 | ok | directo |
| 2021-A-C | activo_total | valor | 4,561,811 | 4,561,811 | 0 | ok | directo |
| 2021-A-C | pasivo_total | valor | 2,023,280 | 2,023,280 | 0 | ok | directo |
| 2021-A-C | patrimonio_total | valor | 2,538,531 | 2,538,531 | 0 | ok | directo |
| 2021-A-C | activo_corriente | valor | 739,545 | 739,545 | 0 | ok | directo |
| 2021-A-C | pasivo_corriente | valor | 844,937 | 844,937 | 0 | ok | directo |
| 2021-A-C | utilidad_bruta | valor | 87,344 | 87,344 | 0 | ok | directo |
| 2021-A-C | impuesto_renta | valor | 23,671 | 23,671 | 0 | ok | directo |

Diferencia explicada en `impuesto_renta`: En el XBRL de la SEC de 2018 el gasto por impuesto tiene el signo invertido (error de etiquetado del emisor): con el signo de la SEC, utilidad antes de impuestos + impuesto no llega a la utilidad neta; con el de la SMV sí (la diferencia restante son operaciones discontinuadas). La base usa el de la SMV.

Diferencia explicada en `impuesto_renta`: En el XBRL de la SEC de 2019 el gasto por impuesto tiene el signo invertido (error de etiquetado del emisor): con el signo de la SEC, utilidad antes de impuestos + impuesto no llega a la utilidad neta; con el de la SMV sí (la diferencia restante son operaciones discontinuadas). La base usa el de la SMV.

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
| 2022-A-C | activo_total | valor | 236,753,609 | 236,753,609 | 0 | ok | directo |
| 2022-A-C | pasivo_total | valor | 207,173,900 | 207,173,900 | 0 | ok | directo |
| 2022-A-C | patrimonio_total | valor | 29,579,709 | 29,579,709 | 0 | ok | directo |
| 2022-A-C | utilidad_neta | valor | 4,745,388 | 4,745,388 | 0 | ok | directo |
| 2022-A-C | utilidad_antes_impuestos | valor | 6,855,889 | 6,855,889 | 0 | ok | directo |
| 2022-A-C | impuesto_renta | valor | -2,110,501 | -2,110,501 | 0 | ok | directo |
| 2022-A-C | ingresos_intereses | valor | 15,011,282 | 15,011,282 | 0 | ok | directo |
| 2022-A-C | gastos_intereses | valor | -3,493,187 | -3,493,187 | 0 | ok | directo |
| 2023-A-C | activo_total | valor | 238,840,188 | 238,840,188 | 0 | ok | directo |
| 2023-A-C | pasivo_total | valor | 205,733,123 | 205,733,123 | 0 | ok | directo |
| 2023-A-C | patrimonio_total | valor | 33,107,065 | 33,107,065 | 0 | ok | directo |
| 2023-A-C | utilidad_neta | valor | 4,959,878 | 4,959,878 | 0 | ok | directo |
| 2023-A-C | utilidad_antes_impuestos | valor | 6,848,329 | 6,848,329 | 0 | ok | directo |
| 2023-A-C | impuesto_renta | valor | -1,888,451 | -1,888,451 | 0 | ok | directo |
| 2023-A-C | ingresos_intereses | valor | 18,798,495 | 18,798,495 | 0 | ok | directo |
| 2023-A-C | gastos_intereses | valor | -5,860,523 | -5,860,523 | 0 | ok | directo |
| 2017-A-C | activo_total | valor | 170,472,283 | 170,472,283 | 0 | ok | directo |
| 2017-A-C | pasivo_total | valor | 148,218,580 | 148,218,580 | 0 | ok | directo |
| 2017-A-C | patrimonio_total | valor | 22,253,703 | 22,253,703 | 0 | ok | directo |
| 2017-A-C | utilidad_neta | valor | 4,181,648 | 4,181,648 | 0 | ok | directo |
| 2017-A-C | utilidad_antes_impuestos | valor | 5,574,934 | 5,574,934 | 0 | ok | directo |
| 2017-A-C | impuesto_renta | valor | -1,393,286 | -1,393,286 | 0 | ok | directo |
| 2017-A-C | ingresos_intereses | valor | 11,030,683 | 11,030,683 | 0 | ok | directo |
| 2017-A-C | gastos_intereses | valor | -2,959,196 | -2,959,196 | 0 | ok | directo |
| 2018-A-C | activo_total | valor | 177,263,201 | 177,263,201 | 0 | ok | directo |
| 2018-A-C | pasivo_total | valor | 152,997,125 | 152,997,125 | 0 | ok | directo |
| 2018-A-C | patrimonio_total | valor | 24,266,076 | 24,266,076 | 0 | ok | directo |
| 2019-A-C | activo_total | valor | 187,876,691 | 187,876,691 | 0 | ok | directo |
| 2019-A-C | pasivo_total | valor | 161,130,381 | 161,130,381 | 0 | ok | directo |
| 2019-A-C | patrimonio_total | valor | 26,746,310 | 26,746,310 | 0 | ok | directo |
| 2019-A-C | utilidad_neta | valor | 4,352,331 | 4,352,331 | 0 | ok | directo |
| 2019-A-C | utilidad_antes_impuestos | valor | 5,975,408 | 5,975,408 | 0 | ok | directo |
| 2019-A-C | impuesto_renta | valor | -1,623,077 | -1,623,077 | 0 | ok | directo |
| 2019-A-C | ingresos_intereses | valor | 12,381,664 | 12,381,664 | 0 | ok | directo |
| 2019-A-C | gastos_intereses | valor | -3,290,867 | -3,290,867 | 0 | ok | directo |
| 2020-A-C | activo_total | valor | 237,406,163 | 237,406,163 | 0 | ok | directo |
| 2020-A-C | pasivo_total | valor | 211,960,516 | 211,960,516 | 0 | ok | directo |
| 2020-A-C | patrimonio_total | valor | 25,445,647 | 25,445,647 | 0 | ok | directo |
| 2020-A-C | utilidad_neta | valor | 334,138 | 334,138 | 0 | ok | directo |
| 2020-A-C | utilidad_antes_impuestos | valor | 224,161 | 224,161 | 0 | ok | directo |
| 2020-A-C | impuesto_renta | valor | 109,977 | 109,977 | 0 | ok | directo |
| 2020-A-C | ingresos_intereses | valor | 11,547,648 | 11,547,648 | 0 | ok | directo |
| 2020-A-C | gastos_intereses | valor | -2,976,306 | -2,976,306 | 0 | ok | directo |
| 2021-A-C | activo_total | valor | 244,821,984 | 244,821,984 | 0 | ok | directo |
| 2021-A-C | pasivo_total | valor | 217,784,545 | 217,784,545 | 0 | ok | directo |
| 2021-A-C | patrimonio_total | valor | 27,037,439 | 27,037,439 | 0 | ok | directo |
| 2021-A-C | utilidad_neta | valor | 3,671,829 | 3,671,829 | 0 | ok | directo |
| 2021-A-C | utilidad_antes_impuestos | valor | 5,332,816 | 5,332,816 | 0 | ok | directo |
| 2021-A-C | impuesto_renta | valor | -1,660,987 | -1,660,987 | 0 | ok | directo |
| 2021-A-C | ingresos_intereses | valor | 11,850,406 | 11,850,406 | 0 | ok | directo |
| 2021-A-C | gastos_intereses | valor | -2,488,426 | -2,488,426 | 0 | ok | directo |

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
