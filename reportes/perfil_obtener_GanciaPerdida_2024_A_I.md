# Perfil: obtener_GanciaPerdida 2024 A I

## 1. Tamaño y origen

- Filas: **11,766**
- Columnas: 17 (más 4 de trazabilidad)
- Tamaño del XML crudo: 5.22 MB; tiempo de respuesta: 12.06 s
- Descargado (UTC): 2026-09-26T05:01:43+00:00; SHA-256: `17037bee753751ce...`

Columnas recibidas: `RPJ`, `TipoEmpresa`, `TipoSector`, `NombreEmpresa`, `RUC`, `CIIU`, `Ejercicio`, `TipoInformacion`, `Trimestre`, `Moneda`, `MetodoFlujoEfectivo`, `Cuenta`, `DescripcionCuenta`, `Monto1`, `Monto2`, `Monto3`, `Monto4`

## 2. ¿Lo recibido coincide con lo pedido?

**Ejercicio**

| Ejercicio | filas |
|---|---|
| 2024 | 11766 |

**Trimestre**

| Trimestre | filas |
|---|---|
| Anual | 11766 |

**TipoInformacion**

| TipoInformacion | filas |
|---|---|
| Anual Individual | 11766 |

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

Cuentas por empresa: mín 31, mediana 37, máx 69

## 4. Planes de cuentas (2º carácter de `Cuenta`)

| plan | filas | empresas | cuentas_distintas | documentado |
|---|---|---|---|---|
| D | 7178 | 194 | 37 | Empresas en general |
| F | 2829 | 41 | 69 | Bancos y financieras |
| I | 1026 | 19 | 54 | NO DOCUMENTADO |
| E | 578 | 17 | 34 | Seguros |
| A | 124 | 4 | 31 | AFP |
| V | 31 | 1 | 31 | CAVALI |

- Empresas que reportan en más de un plan: 0

Cruce TipoEmpresa × plan (filas). Sirve para entender a quién pertenece cada plan:

| TipoEmpresa | A | D | E | F | I | V |
|---|---|---|---|---|---|---|
| BOLSAS DE VALORES Y OTRAS ENTIDADES RESPONSABLES DE LA CONDUCCIÓN DE MECANISMOS CENTRALIZADOS DE NEG | 0 | 37 | 0 | 0 | 0 | 0 |
| EMPRESAS ADMINISTRADORAS DE FONDOS COLECTIVOS | 0 | 333 | 0 | 0 | 0 | 0 |
| EMPRESAS CLASIFICADORAS DE RIESGO | 0 | 148 | 0 | 0 | 0 | 0 |
| EMPRESAS EMISORAS | 124 | 4292 | 578 | 2691 | 0 | 0 |
| EMPRESAS MERCADO ALTERNATIVO DE VALORES | 0 | 148 | 0 | 69 | 0 | 0 |
| EMPRESAS MERCADO INVERSIONISTA INSTITUCIONAL | 0 | 333 | 0 | 69 | 0 | 0 |
| EMPRESAS PROVEEDORAS DE PRECIOS | 0 | 37 | 0 | 0 | 0 | 0 |
| EMPRESAS VALORIZADORAS | 0 | 74 | 0 | 0 | 0 | 0 |
| INSTITUCION DE COMPENSACION Y LIQUIDACION DE VALORES | 0 | 0 | 0 | 0 | 0 | 31 |
| SOCIEDADES ADMINISTRADORAS DE FONDOS DE INVERSION | 0 | 592 | 0 | 0 | 0 | 0 |
| SOCIEDADES ADMINISTRADORAS DE FONDOS MUTUOS Y FONDOS DE INVERSION | 0 | 629 | 0 | 0 | 0 | 0 |
| SOCIEDADES ADMINISTRADORAS DE PLATAFORMAS DE FINANCIAMIENTO PARTICIPATIVO FINANCIERO | 0 | 111 | 0 | 0 | 0 | 0 |
| SOCIEDADES AGENTES DE BOLSA | 0 | 0 | 0 | 0 | 1026 | 0 |
| SOCIEDADES ESTRUCTURADORAS - SES | 0 | 148 | 0 | 0 | 0 | 0 |
| SOCIEDADES TITULIZADORAS | 0 | 296 | 0 | 0 | 0 | 0 |

Empresas en planes no documentados (primeras 15):

| plan | RPJ | NombreEmpresa | filas |
|---|---|---|---|
| I | B80128     | SCOTIA SOCIEDAD AGENTE DE BOLSA S.A. | 54 |
| I | B80132     | SOCIEDAD AGENTE DE BOLSA CARTISA PERU S.A. | 54 |
| I | IV0002     | TRADEK S.A. SOCIEDAD AGENTE DE BOLSA | 54 |
| I | J40794     | SURA INVESTMENTS SOCIEDAD AGENTE DE BOLSA S.A. | 54 |
| I | OE3793     | KALLPA SECURITIES SOCIEDAD AGENTE DE BOLSA S.A. | 54 |
| I | OE3845     | BTG PACTUAL PERU SA SOCIEDAD AGENTE DE BOLSA ( ANTES CELFIN CAPITAL SAB) | 54 |
| I | OE4263     | DIVISO BOLSA SOCIEDAD AGENTE DE BOLSA S.A.(S) | 54 |
| I | OE4706     | LARRAIN VIAL SOCIEDAD AGENTE DE BOLSA S.A. | 54 |
| I | OE5661     | ACRES SOCIEDAD AGENTE DE BOLSA S.A. | 54 |
| I | OE5916     | RENTA 4 SOCIEDAD AGENTE DE BOLSA S.A. | 54 |
| I | S80061     | SEMINARIO Y CIA. SOCIEDAD AGENTE DE BOLSA S.A. | 54 |
| I | S80080     | CREDICORP CAPITAL SOCIEDAD AGENTE DE BOLSA S.A. | 54 |
| I | S80082     | INVERSION Y DESARROLLO SOCIEDAD AGENTE DE BOLSA S.A.C. | 54 |
| I | S80105     | MAGOT SOCIEDAD AGENTE DE BOLSA SAC | 54 |
| I | S80145     | PROMOTORES E INVERSIONES INVESTA S.A. SOCIEDAD AGENTE DE BOLSA | 54 |

Muestra de cuentas de esos planes:

| Cuenta | DescripcionCuenta |
|---|---|
| 2I2000 | INGRESOS OPERACIONALES |
| 2I2011 | Ingresos Brutos por Comisiones y servicios en el mercado de valores |
| 2I2020 | Venta de Inversiones Financieras |
| 2I2033 | Otros ingresos operacionales |
| 2I2030 | Intereses y dividendos |
| 2I2031 | Total Ingresos Operacionales |
| 2I2032 | COSTOS OPERACIONALES |
| 2I2055 | Otros costos operacionales |
| 2I2041 | Costo de venta y servicios en el Mercado de Valores |
| 2I2050 | Costo de enajenación de inversiones financieros |
| 2I2034 | Total Costos Operacionales |
| 2I2051 | Utilidad Bruta |
| 2I2052 | GASTOS OPERACIONALES |
| 2I2070 | Gastos de ventas |
| 2I2060 | Gastos de administración |

## 5. Moneda

| Moneda | filas | empresas |
|---|---|---|
| D lares | 1110 | 30 |
| Soles | 10656 | 246 |

- Empresas con más de una moneda en el mismo período: 0

## 6. Montos

| columna | tipo_original | nulos | no_numéricos | ceros | distintos_de_cero | negativos |
|---|---|---|---|---|---|---|
| Monto1 | float64 | 0 | 0 | 5898 | 5868 | 2638 |
| Monto2 | float64 | 0 | 0 | 5900 | 5866 | 2701 |
| Monto3 | int64 | 0 | 0 | 11766 | 0 | 0 |
| Monto4 | int64 | 0 | 0 | 11766 | 0 | 0 |

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


Descripciones distintas: 223; con tildes/ñ bien formadas: 87

## 9. Nulos y vacíos por columna

| columna | nulos | vacíos | distintos |
|---|---|---|---|
| RPJ | 0 | 0 | 276 |
| TipoEmpresa | 0 | 0 | 15 |
| TipoSector | 0 | 3351 | 10 |
| NombreEmpresa | 0 | 0 | 276 |
| RUC | 0 | 0 | 274 |
| CIIU | 0 | 810 | 83 |
| Ejercicio | 0 | 0 | 1 |
| TipoInformacion | 0 | 0 | 1 |
| Trimestre | 0 | 0 | 1 |
| Moneda | 0 | 0 | 2 |
| MetodoFlujoEfectivo | 0 | 0 | 2 |
| Cuenta | 0 | 0 | 256 |
| DescripcionCuenta | 0 | 0 | 223 |
| Monto1 | 0 | 0 | 4693 |
| Monto2 | 0 | 0 | 4676 |
| Monto3 | 0 | 0 | 1 |
| Monto4 | 0 | 0 | 1 |

