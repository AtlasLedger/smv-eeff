# Diccionario de datos

Todas las tablas están en formato Parquet dentro de `data/`. Los montos están en **miles**
de la moneda en que la empresa reportó (ver `presentaciones.moneda`). La base no convierte
monedas ni corrige montos: publica lo que la empresa presentó a la SMV.

Claves comunes:

| campo | significado |
|---|---|
| `rpj` | Código de la empresa en la SMV (Registro Público). Es la clave de empresa: el RUC no sirve porque los holdings extranjeros no tienen. |
| `ejercicio` | Año del estado financiero. |
| `periodo` | `A` anual (auditado), `1` a `4` trimestres (no auditados). |
| `tipo` | `I` individual (separado), `C` consolidado. |
| `estado` | `BG` situación financiera, `ER` resultados, `FE` flujo de efectivo, `ORI` otro resultado integral, `CP` cambios en el patrimonio. |

## hechos/ejercicio=AAAA/part-0.parquet

Una fila por empresa, período, tipo y cuenta. Es el dato original de la SMV, limpio.

| campo | significado |
|---|---|
| `cuenta` | Código de cuenta de la SMV. El segundo carácter es el plan de cuentas (ver `cuentas`). |
| `monto` | Monto del período aislado. En trimestres de resultados y ORI es **solo el trimestre**. En el balance es el saldo al cierre. En trimestres del flujo de efectivo es nulo: la SMV solo publica el acumulado (ver `monto_acumulado`). También es nulo en el estado de resultados trimestral de las sociedades agentes de bolsa: ahí la SMV entrega un subperíodo que no identifica (por magnitud, el último mes). |
| `monto_comparativo` | Mismo concepto en el período comparativo que publica la empresa: año anterior (resultados, flujo) o cierre del ejercicio anterior (balance). |
| `monto_acumulado` | Trimestres de resultados, ORI y flujo de efectivo: acumulado desde enero. Nulo cuando no aplica (anuales y balance). |
| `monto_acumulado_comparativo` | Acumulado del mismo período del año anterior. |

## presentaciones.parquet

Una fila por estado financiero presentado (empresa, período, tipo, estado).

| campo | significado |
|---|---|
| `plan` | Plan de cuentas usado: `D` empresas en general, `F` bancos y financieras, `E` seguros, `A` AFP, `I` sociedades agentes de bolsa, `V` CAVALI. |
| `moneda` | `PEN` o `USD`. |
| `metodo_flujo` | Método del flujo de efectivo declarado (directo o indirecto). |
| `cuentas` | Número de cuentas presentadas. |
| `smv_*` | Totales que la propia SMV publica en su índice (activo, pasivo, patrimonio, ingreso, utilidad neta). Sirven de control. |

## empresas.parquet

| campo | significado |
|---|---|
| `rpj` | Clave. |
| `ruc` | RUC. Nulo para holdings extranjeros (la SMV los reporta con RUC 0). |
| `nombre` | Razón social más reciente. El historial está en `empresas_nombres.parquet`. |
| `ciiu` | Actividad económica (CIIU). |
| `tipo_empresa` | Clasificación de la SMV (emisora, SAB, SAF, etc.). |
| `sector` | Sector según la SMV. |
| `planes` | Plan(es) de cuentas usados. |
| `primer_periodo`, `ultimo_periodo` | Rango con información en la base. |

## cuentas.parquet

| campo | significado |
|---|---|
| `cuenta` | Código. |
| `estado`, `plan` | Estado financiero y plan de cuentas. |
| `descripcion` | Descripción más reciente (limpia). El historial está en `cuentas_descripciones.parquet`. |
| `orden` | Posición de la cuenta en el formato de presentación de la SMV. |

## patrimonio/ejercicio=AAAA/part-0.parquet

Estado de cambios en el patrimonio. Es una matriz: filas (movimientos) por columnas
(componentes del patrimonio). Solo se guardan celdas distintas de cero.

| campo | significado |
|---|---|
| `cuenta` | Fila de la matriz (saldo inicial, utilidad, dividendos, saldo final...). |
| `columna` | Número de columna. Su nombre está en `patrimonio_columnas.parquet` según el plan. |
| `bloque` | Aparición de la fila en el reporte. Las SAB repiten los mismos códigos para el año anterior (`0`) y el actual (`1`). En los demás planes es siempre `0`. |
| `monto` | Monto. |

## estandar.parquet

Conceptos comparables entre planes de cuentas (activo total, ingresos, utilidad neta...).
Las definiciones están en `mapeo/conceptos.csv` y las reglas en `mapeo/mapeo_cuentas.csv`.

| campo | significado |
|---|---|
| `concepto` | Concepto estándar. |
| `valor`, `valor_comparativo`, `valor_acumulado` | Igual que en `hechos`. |
| `cuentas` | Cuentas de la SMV que se sumaron. |
| `confianza` | `directo`: equivalencia sin discusión. `validado`: decisión de criterio revisada. `propuesto`: decisión de criterio aún no validada; usar con cuidado. |

## ratios.parquet

| ratio | fórmula |
|---|---|
| `margen_bruto`, `margen_operativo`, `margen_neto` | utilidad correspondiente / ingresos |
| `roe` | utilidad neta / patrimonio promedio (solo anual) |
| `roa` | utilidad neta / activo promedio (solo anual) |
| `pasivo_patrimonio` | pasivo total / patrimonio |
| `deuda_patrimonio` | deuda financiera / patrimonio |
| `liquidez_corriente` | activo corriente / pasivo corriente |
| `tasa_impositiva_efectiva` | impuesto / utilidad antes de impuestos |
| `morosidad` | cartera atrasada / cartera bruta (bancos) |
| `cobertura_provisiones` | provisiones / cartera atrasada (bancos) |
| `siniestralidad` | siniestros netos / primas ganadas netas (seguros) |

Cada ratio hereda la `confianza` más baja de sus insumos. Los ratios trimestrales de margen
usan el trimestre aislado, no el acumulado.

## calidad.json

Conteo de problemas encontrados al construir la base y del control cruzado contra el
índice de la SMV.
