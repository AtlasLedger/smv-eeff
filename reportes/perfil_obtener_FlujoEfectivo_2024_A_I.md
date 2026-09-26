# Perfil: obtener_FlujoEfectivo 2024 A I

## 1. Tamaño y origen

- Filas: **17,347**
- Columnas: 15 (más 4 de trazabilidad)
- Tamaño del XML crudo: 7.43 MB; tiempo de respuesta: 34.83 s
- Descargado (UTC): 2026-09-26T05:08:38+00:00; SHA-256: `6c36c8816fbfeea9...`

Columnas recibidas: `RPJ`, `TipoEmpresa`, `TipoSector`, `NombreEmpresa`, `RUC`, `CIIU`, `Ejercicio`, `TipoInformacion`, `Trimestre`, `Moneda`, `MetodoFlujoEfectivo`, `Cuenta`, `DescripcionCuenta`, `Monto1`, `Monto2`

## 2. ¿Lo recibido coincide con lo pedido?

**Ejercicio**

| Ejercicio | filas |
|---|---|
| 2024 | 17347 |

**Trimestre**

| Trimestre | filas |
|---|---|
| Anual | 17347 |

**TipoInformacion**

| TipoInformacion | filas |
|---|---|
| Anual Individual | 17347 |

## 3. Empresas (candidatas a dimensión)

- RPJ únicos: **276**
- RUC únicos: 274

Atributos que varían dentro de un mismo RPJ (ideal: 0 en todos):

| atributo | RPJ con más de un valor |
|---|---|
| NombreEmpresa | 0 |
| RUC | 0 |
| CIIU | 0 |
| TipoEmpresa | 0 |
| TipoSector | 0 |

- RUC asociados a más de un RPJ: 1

Empresas por TipoEmpresa:

| TipoEmpresa | empresas |
|---|---|
| EMPRESAS EMISORAS | 176 |
| SOCIEDADES AGENTES DE BOLSA | 19 |
| SOCIEDADES ADMINISTRADORAS DE FONDOS MUTUOS Y FONDOS DE INVERSION | 17 |
| SOCIEDADES ADMINISTRADORAS DE FONDOS DE INVERSION | 16 |
| EMPRESAS MERCADO INVERSIONISTA INSTITUCIONAL | 10 |
| EMPRESAS ADMINISTRADORAS DE FONDOS COLECTIVOS | 9 |
| SOCIEDADES TITULIZADORAS | 8 |
| EMPRESAS MERCADO ALTERNATIVO DE VALORES | 5 |
| EMPRESAS CLASIFICADORAS DE RIESGO | 4 |
| SOCIEDADES ESTRUCTURADORAS - SES | 4 |
| SOCIEDADES ADMINISTRADORAS DE PLATAFORMAS DE FINANCIAMIENTO PARTICIPATIVO FINANCIERO | 3 |
| EMPRESAS VALORIZADORAS | 2 |
| BOLSAS DE VALORES Y OTRAS ENTIDADES RESPONSABLES DE LA CONDUCCIÓN DE MECANISMOS CENTRALIZADOS DE NEG | 1 |
| EMPRESAS PROVEEDORAS DE PRECIOS | 1 |
| INSTITUCION DE COMPENSACION Y LIQUIDACION DE VALORES | 1 |

Cuentas por empresa: mín 29, mediana 66, máx 83

## 4. Planes de cuentas (2º carácter de `Cuenta`)

| plan | filas | empresas | cuentas_distintas | documentado |
|---|---|---|---|---|
| D | 13739 | 194 | 94 | Empresas en general |
| F | 1435 | 41 | 35 | Bancos y financieras |
| I | 1057 | 19 | 68 | NO DOCUMENTADO |
| E | 935 | 17 | 55 | Seguros |
| A | 116 | 4 | 29 | AFP |
| V | 65 | 1 | 65 | CAVALI |

- Empresas que reportan en más de un plan: 0

Cruce TipoEmpresa × plan (filas). Sirve para entender a quién pertenece cada plan:

| TipoEmpresa | A | D | E | F | I | V |
|---|---|---|---|---|---|---|
| BOLSAS DE VALORES Y OTRAS ENTIDADES RESPONSABLES DE LA CONDUCCIÓN DE MECANISMOS CENTRALIZADOS DE NEG | 0 | 66 | 0 | 0 | 0 | 0 |
| EMPRESAS ADMINISTRADORAS DE FONDOS COLECTIVOS | 0 | 628 | 0 | 0 | 0 | 0 |
| EMPRESAS CLASIFICADORAS DE RIESGO | 0 | 264 | 0 | 0 | 0 | 0 |
| EMPRESAS EMISORAS | 116 | 8183 | 935 | 1365 | 0 | 0 |
| EMPRESAS MERCADO ALTERNATIVO DE VALORES | 0 | 298 | 0 | 35 | 0 | 0 |
| EMPRESAS MERCADO INVERSIONISTA INSTITUCIONAL | 0 | 662 | 0 | 35 | 0 | 0 |
| EMPRESAS PROVEEDORAS DE PRECIOS | 0 | 66 | 0 | 0 | 0 | 0 |
| EMPRESAS VALORIZADORAS | 0 | 149 | 0 | 0 | 0 | 0 |
| INSTITUCION DE COMPENSACION Y LIQUIDACION DE VALORES | 0 | 0 | 0 | 0 | 0 | 65 |
| SOCIEDADES ADMINISTRADORAS DE FONDOS DE INVERSION | 0 | 1192 | 0 | 0 | 0 | 0 |
| SOCIEDADES ADMINISTRADORAS DE FONDOS MUTUOS Y FONDOS DE INVERSION | 0 | 1207 | 0 | 0 | 0 | 0 |
| SOCIEDADES ADMINISTRADORAS DE PLATAFORMAS DE FINANCIAMIENTO PARTICIPATIVO FINANCIERO | 0 | 198 | 0 | 0 | 0 | 0 |
| SOCIEDADES AGENTES DE BOLSA | 0 | 0 | 0 | 0 | 1057 | 0 |
| SOCIEDADES ESTRUCTURADORAS - SES | 0 | 264 | 0 | 0 | 0 | 0 |
| SOCIEDADES TITULIZADORAS | 0 | 562 | 0 | 0 | 0 | 0 |

Empresas en planes no documentados (primeras 15):

| plan | RPJ | NombreEmpresa | filas |
|---|---|---|---|
| I | B80128     | SCOTIA SOCIEDAD AGENTE DE BOLSA S.A. | 55 |
| I | B80132     | SOCIEDAD AGENTE DE BOLSA CARTISA PERU S.A. | 57 |
| I | IV0002     | TRADEK S.A. SOCIEDAD AGENTE DE BOLSA | 55 |
| I | J40794     | SURA INVESTMENTS SOCIEDAD AGENTE DE BOLSA S.A. | 55 |
| I | OE3793     | KALLPA SECURITIES SOCIEDAD AGENTE DE BOLSA S.A. | 55 |
| I | OE3845     | BTG PACTUAL PERU SA SOCIEDAD AGENTE DE BOLSA ( ANTES CELFIN CAPITAL SAB) | 55 |
| I | OE4263     | DIVISO BOLSA SOCIEDAD AGENTE DE BOLSA S.A.(S) | 55 |
| I | OE4706     | LARRAIN VIAL SOCIEDAD AGENTE DE BOLSA S.A. | 57 |
| I | OE5661     | ACRES SOCIEDAD AGENTE DE BOLSA S.A. | 57 |
| I | OE5916     | RENTA 4 SOCIEDAD AGENTE DE BOLSA S.A. | 55 |
| I | S80061     | SEMINARIO Y CIA. SOCIEDAD AGENTE DE BOLSA S.A. | 55 |
| I | S80080     | CREDICORP CAPITAL SOCIEDAD AGENTE DE BOLSA S.A. | 55 |
| I | S80082     | INVERSION Y DESARROLLO SOCIEDAD AGENTE DE BOLSA S.A.C. | 55 |
| I | S80105     | MAGOT SOCIEDAD AGENTE DE BOLSA SAC | 57 |
| I | S80145     | PROMOTORES E INVERSIONES INVESTA S.A. SOCIEDAD AGENTE DE BOLSA | 57 |

Muestra de cuentas de esos planes:

| Cuenta | DescripcionCuenta |
|---|---|
| 4I4500 | FLUJOS DE EFECTIVO DE ACTIVIDAD DE OPERACIÓN |
| 4I5516 | Ganancia (pérdida) Neta del Ejercicio |
| 4I5520 | Ajustes por disminuciones (incrementos) en cuentas por cobrar de origen comercial |
| 4I5521 | Ajustes por disminuciones (incrementos) en otras cuentas por cobrar derivadas de las actividades de operación |
| 4I5522 | Ajustes por incrementos (disminuciones) en cuentas por pagar de origen comercial |
| 4I5523 | Ajustes por incrementos (disminuciones) en otras cuentas por pagar derivadas de las actividades de operación |
| 4I5524 | Ajustes por gastos de depreciación y amortización |
| 4I5526 | Ajustes por provisiones |
| 4I5527 | Ajustes por pérdidas (ganancias) de moneda extranjera no realizadas |
| 4I5529 | Ajustes por ganancias (pérdidas) de valor razonable |
| 4I5530 | Otros ajustes por partidas distintas al efectivo |
| 4I5531 | Ajustes por pérdidas (ganancias) por la disposición de activos no corrientes |
| 4I5532 | Otros ajustes para los que los efectos sobre el efectivo son flujos de efectivo de inversión o financiación |
| 4I5534 | Ganancias (pérdidas) no distribuidas de asociadas(*) |
| 4I4519 | Impuestos a las ganancias reembolsados (pagados) |

## 5. Moneda

| Moneda | filas | empresas |
|---|---|---|
| D lares | 2133 | 30 |
| Soles | 15214 | 246 |

- Empresas con más de una moneda en el mismo período: 0

## 6. Montos

| columna | tipo_original | nulos | no_numéricos | ceros | distintos_de_cero | negativos |
|---|---|---|---|---|---|---|
| Monto1 | float64 | 0 | 0 | 11231 | 6116 | 3006 |
| Monto2 | float64 | 0 | 0 | 11261 | 6086 | 3062 |

Si Monto3/Monto4 salen todo en cero, se pueden descartar del modelo (pero se deja la evidencia aquí).

## 7. Duplicados

- Filas exactamente duplicadas: 0
- Filas con clave (RPJ, Cuenta, Moneda) repetida: 0

## 8. Encoding

Valores sospechosos (heurística, revisar a mano):

| columna | patrón | valores_distintos |
|---|---|---|
| Moneda | consonante mayúscula suelta + palabra (ej. 'M todo') | 1 |
| MetodoFlujoEfectivo | consonante mayúscula suelta + palabra (ej. 'M todo') | 2 |

Ejemplos:

| columna | patrón | valor |
|---|---|---|
| Moneda | consonante mayúscula suelta + palabra (ej. 'M todo') | D lares |
| MetodoFlujoEfectivo | consonante mayúscula suelta + palabra (ej. 'M todo') | M todo Directo |
| MetodoFlujoEfectivo | consonante mayúscula suelta + palabra (ej. 'M todo') | M todo Indirecto |

Cuentas con más de una descripción: **7**
- Solo difieren por encoding (colapsan al quitar no-ASCII): 4
- Difieren en redacción real: 3

Ejemplos por encoding:

| Cuenta | variantes |
|---|---|
| 3D0103 | Intereses Recibidos (no Incluidos en la Actividad de Inversión) ‖ Intereses Recibidos (no incluidos en la Actividad de Inversión) |
| 3D0107 | Intereses Pagados (no Incluidos en la Actividad de Financiación) ‖ Intereses Pagados (no incluidos en la Actividad de Financiación) |
| 3D0111 | Dividendos Recibidos (no Incluidos en la Actividad de Inversión) ‖ Dividendos Recibidos (no incluidos en la Actividad de Inversión) |
| 3D0116 | Dividendos Pagados (no Incluidos en la Actividad de Financiación) ‖ Dividendos Pagados (no incluidos en la Actividad de Financiación) |

Ejemplos por redacción:

| Cuenta | variantes |
|---|---|
| 3D05ST |  ‖ Ganancia (Pérdida) Neta del Ejercicio |
| 4I4519 | Impuestos a las ganancias reembolsados (pagados) ‖ Pagos de tributos |
| 4I4520 | Otras entradas (salidas) de efectivo ‖ Otros |

Descripciones distintas: 309; con tildes/ñ bien formadas: 154

## 9. Nulos y vacíos por columna

| columna | nulos | vacíos | distintos |
|---|---|---|---|
| RPJ | 0 | 0 | 276 |
| TipoEmpresa | 0 | 0 | 15 |
| TipoSector | 0 | 5520 | 10 |
| NombreEmpresa | 0 | 0 | 276 |
| RUC | 0 | 0 | 274 |
| CIIU | 0 | 831 | 83 |
| Ejercicio | 0 | 0 | 1 |
| TipoInformacion | 0 | 0 | 1 |
| Trimestre | 0 | 0 | 1 |
| Moneda | 0 | 0 | 2 |
| MetodoFlujoEfectivo | 0 | 0 | 2 |
| Cuenta | 0 | 0 | 346 |
| DescripcionCuenta | 0 | 139 | 309 |
| Monto1 | 0 | 0 | 5187 |
| Monto2 | 0 | 0 | 5157 |

