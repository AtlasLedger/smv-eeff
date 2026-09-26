# Perfil: obtener_BalanceGeneral 2024 A I

## 1. Tamaño y origen

- Filas: **20,574**
- Columnas: 15 (más 4 de trazabilidad)
- Tamaño del XML crudo: 8.43 MB; tiempo de respuesta: 16.06 s
- Descargado (UTC): 2026-09-26T05:08:01+00:00; SHA-256: `bf3b7d4a15a59bd2...`

Columnas recibidas: `RPJ`, `TipoEmpresa`, `TipoSector`, `NombreEmpresa`, `RUC`, `CIIU`, `Ejercicio`, `TipoInformacion`, `Trimestre`, `Moneda`, `MetodoFlujoEfectivo`, `Cuenta`, `DescripcionCuenta`, `Monto1`, `Monto2`

## 2. ¿Lo recibido coincide con lo pedido?

**Ejercicio**

| Ejercicio | filas |
|---|---|
| 2024 | 20574 |

**Trimestre**

| Trimestre | filas |
|---|---|
| Anual | 20574 |

**TipoInformacion**

| TipoInformacion | filas |
|---|---|
| Anual Individual | 20574 |

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

Cuentas por empresa: mín 57, mediana 69, máx 102

## 4. Planes de cuentas (2º carácter de `Cuenta`)

| plan | filas | empresas | cuentas_distintas | documentado |
|---|---|---|---|---|
| D | 13386 | 194 | 69 | Empresas en general |
| F | 3854 | 41 | 94 | Bancos y financieras |
| I | 1938 | 19 | 102 | NO DOCUMENTADO |
| E | 1071 | 17 | 63 | Seguros |
| A | 228 | 4 | 57 | AFP |
| V | 97 | 1 | 97 | CAVALI |

- Empresas que reportan en más de un plan: 0

Cruce TipoEmpresa × plan (filas). Sirve para entender a quién pertenece cada plan:

| TipoEmpresa | A | D | E | F | I | V |
|---|---|---|---|---|---|---|
| BOLSAS DE VALORES Y OTRAS ENTIDADES RESPONSABLES DE LA CONDUCCIÓN DE MECANISMOS CENTRALIZADOS DE NEG | 0 | 69 | 0 | 0 | 0 | 0 |
| EMPRESAS ADMINISTRADORAS DE FONDOS COLECTIVOS | 0 | 621 | 0 | 0 | 0 | 0 |
| EMPRESAS CLASIFICADORAS DE RIESGO | 0 | 276 | 0 | 0 | 0 | 0 |
| EMPRESAS EMISORAS | 228 | 8004 | 1071 | 3666 | 0 | 0 |
| EMPRESAS MERCADO ALTERNATIVO DE VALORES | 0 | 276 | 0 | 94 | 0 | 0 |
| EMPRESAS MERCADO INVERSIONISTA INSTITUCIONAL | 0 | 621 | 0 | 94 | 0 | 0 |
| EMPRESAS PROVEEDORAS DE PRECIOS | 0 | 69 | 0 | 0 | 0 | 0 |
| EMPRESAS VALORIZADORAS | 0 | 138 | 0 | 0 | 0 | 0 |
| INSTITUCION DE COMPENSACION Y LIQUIDACION DE VALORES | 0 | 0 | 0 | 0 | 0 | 97 |
| SOCIEDADES ADMINISTRADORAS DE FONDOS DE INVERSION | 0 | 1104 | 0 | 0 | 0 | 0 |
| SOCIEDADES ADMINISTRADORAS DE FONDOS MUTUOS Y FONDOS DE INVERSION | 0 | 1173 | 0 | 0 | 0 | 0 |
| SOCIEDADES ADMINISTRADORAS DE PLATAFORMAS DE FINANCIAMIENTO PARTICIPATIVO FINANCIERO | 0 | 207 | 0 | 0 | 0 | 0 |
| SOCIEDADES AGENTES DE BOLSA | 0 | 0 | 0 | 0 | 1938 | 0 |
| SOCIEDADES ESTRUCTURADORAS - SES | 0 | 276 | 0 | 0 | 0 | 0 |
| SOCIEDADES TITULIZADORAS | 0 | 552 | 0 | 0 | 0 | 0 |

Empresas en planes no documentados (primeras 15):

| plan | RPJ | NombreEmpresa | filas |
|---|---|---|---|
| I | B80128     | SCOTIA SOCIEDAD AGENTE DE BOLSA S.A. | 102 |
| I | B80132     | SOCIEDAD AGENTE DE BOLSA CARTISA PERU S.A. | 102 |
| I | IV0002     | TRADEK S.A. SOCIEDAD AGENTE DE BOLSA | 102 |
| I | J40794     | SURA INVESTMENTS SOCIEDAD AGENTE DE BOLSA S.A. | 102 |
| I | OE3793     | KALLPA SECURITIES SOCIEDAD AGENTE DE BOLSA S.A. | 102 |
| I | OE3845     | BTG PACTUAL PERU SA SOCIEDAD AGENTE DE BOLSA ( ANTES CELFIN CAPITAL SAB) | 102 |
| I | OE4263     | DIVISO BOLSA SOCIEDAD AGENTE DE BOLSA S.A.(S) | 102 |
| I | OE4706     | LARRAIN VIAL SOCIEDAD AGENTE DE BOLSA S.A. | 102 |
| I | OE5661     | ACRES SOCIEDAD AGENTE DE BOLSA S.A. | 102 |
| I | OE5916     | RENTA 4 SOCIEDAD AGENTE DE BOLSA S.A. | 102 |
| I | S80061     | SEMINARIO Y CIA. SOCIEDAD AGENTE DE BOLSA S.A. | 102 |
| I | S80080     | CREDICORP CAPITAL SOCIEDAD AGENTE DE BOLSA S.A. | 102 |
| I | S80082     | INVERSION Y DESARROLLO SOCIEDAD AGENTE DE BOLSA S.A.C. | 102 |
| I | S80105     | MAGOT SOCIEDAD AGENTE DE BOLSA SAC | 102 |
| I | S80145     | PROMOTORES E INVERSIONES INVESTA S.A. SOCIEDAD AGENTE DE BOLSA | 102 |

Muestra de cuentas de esos planes:

| Cuenta | DescripcionCuenta |
|---|---|
| 1I0000 | ACTIVO |
| 1I0001 | ACTIVOS CORRIENTES |
| 1I1010 | Efectivo y Equivalentes de Efectivo |
| 1I1096 | Otros Activos Financieros |
| 1I1030 | Cuentas por Cobrar Comerciales, neto |
| 1I1050 | Cuentas por cobrar a Entidades Relacionadas |
| 1I1040 | Otras Cuentas por Cobrar, neto |
| 1I1070 | Gastos Pagados por Anticipado |
| 1I1133 | Otros Activos no Financieros |
| 1I1097 | Activos por Impuestos a las Ganancias |
| 1I1135 | Total de Activos Corrientes Distintos de los Activos o Grupos de Activos para su Disposición Clasificados como Mantenidos para la Venta o para Distribuir a los Propietarios |
| 1I1103 | Activos no corrientes o Grupos de Activos para su Disposición Clasificados como Mantenidos para la Venta |
| 1I1104 | Activos no Corrientes o Grupos de Activos para su Disposición Clasificados como Mantenidos para Distribuir a los Propietarios |
| 1I1136 | Activos no Corrientes o Grupos de Activos para su Disposición Clasificados como Mantenidos para la Venta o como Mantenidos para Distribuir a los Propietarios |
| 1I1071 | Total Activos Corrientes |

## 5. Moneda

| Moneda | filas | empresas |
|---|---|---|
| D lares | 2070 | 30 |
| Soles | 18504 | 246 |

- Empresas con más de una moneda en el mismo período: 0

## 6. Montos

| columna | tipo_original | nulos | no_numéricos | ceros | distintos_de_cero | negativos |
|---|---|---|---|---|---|---|
| Monto1 | float64 | 0 | 0 | 10405 | 10169 | 220 |
| Monto2 | float64 | 0 | 0 | 10417 | 10157 | 223 |

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

Cuentas con más de una descripción: **0**
- Solo difieren por encoding (colapsan al quitar no-ASCII): 0
- Difieren en redacción real: 0


Descripciones distintas: 351; con tildes/ñ bien formadas: 81

## 9. Nulos y vacíos por columna

| columna | nulos | vacíos | distintos |
|---|---|---|---|
| RPJ | 0 | 0 | 276 |
| TipoEmpresa | 0 | 0 | 15 |
| TipoSector | 0 | 6313 | 10 |
| NombreEmpresa | 0 | 0 | 276 |
| RUC | 0 | 0 | 274 |
| CIIU | 0 | 1530 | 83 |
| Ejercicio | 0 | 0 | 1 |
| TipoInformacion | 0 | 0 | 1 |
| Trimestre | 0 | 0 | 1 |
| Moneda | 0 | 0 | 2 |
| MetodoFlujoEfectivo | 0 | 0 | 2 |
| Cuenta | 0 | 0 | 482 |
| DescripcionCuenta | 0 | 0 | 351 |
| Monto1 | 0 | 0 | 7771 |
| Monto2 | 0 | 0 | 7760 |

