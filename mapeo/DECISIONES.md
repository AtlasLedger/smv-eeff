# Decisiones de criterio pendientes

Cada decisión cambia cómo se calcula un concepto estándar para un tipo de entidad. Mientras
no se validen, los valores afectados salen con `confianza = propuesto`. Los impactos están
medidos sobre los estados anuales individuales 2024.

Para aprobar una decisión: cambiar `propuesto` por `validado` en `mapeo_cuentas.csv` (y
ajustar `cuentas` si se elige otra opción). Luego `python scripts/construir.py`.

---

## 1. Ingresos de bancos y financieras (plan F)

| opción | cuentas | comentario |
|---|---|---|
| A. Criterio SMV | 2F0101 | Solo ingresos por intereses. Es lo que usa el índice de la SMV. |
| **B. Propuesta** | 2F0101 + 2F2402 | Intereses + ingresos por servicios financieros (comisiones). Así miden los ingresos de un banco la SBS y los analistas. |

**Impacto:** con la opción B los ingresos suben 14 % en la mediana (entre 2 % y 27 % en el
80 % central de las 41 entidades). El margen neto mediano pasa de 10.2 % a 9.6 %.

**Recomendación:** B. Las comisiones son una línea de negocio central (tarjetas,
transferencias, cartas fianza); dejarlas fuera subestima el tamaño del banco.

**Nota:** en el consolidado bancario la plantilla solo trae comisiones netas (2F2406), no
brutas; ahí la opción B usa ingresos ordinarios + comisiones netas. No es idéntico al
individual y así queda documentado.

## 2. Ingresos de seguros (plan E)

| opción | cuentas | comentario |
|---|---|---|
| A. Criterio SMV | 2E0201 | Total primas netas del ejercicio, antes de ceder riesgo a reaseguradoras. |
| **B. Propuesta** | 2E0602 | Primas ganadas netas: lo que la aseguradora retiene después de reaseguro y ajuste de reservas. |

**Impacto:** las primas ganadas netas son 64 % de las primas netas en la mediana (entre
46 % y 98 %). Con A, una aseguradora que cede mucho riesgo aparece más grande de lo que es.

**Recomendación:** B, porque es el ingreso sobre el que se calcula la siniestralidad y es
comparable entre aseguradoras con distinta política de reaseguro.

## 3. Ingresos de sociedades agentes de bolsa (plan I)

| opción | cuentas | comentario |
|---|---|---|
| A. Criterio SMV | 2I2031 | Total ingresos operacionales. Incluye el valor **bruto** de las inversiones vendidas. |
| **B. Propuesta** | 2I2011 + 2I2030 + 2I2033 + 2I2020 + 2I2050 | Comisiones + intereses + otros + ganancia **neta** en venta de inversiones (venta menos costo). |

**Impacto:** con A los ingresos son 4.5 veces los de B en la mediana, y hasta 1,147 veces
(Larrain Vial SAB 2024: S/ 19,172 millones con A contra S/ 16.7 millones con B). Cualquier
margen calculado con A es inútil.

**Recomendación:** B, sin mucha duda. Vender una inversión de 100 que costó 99 no es un
ingreso de 100.

## 4. Efectivo de bancos (plan F)

| opción | cuentas | comentario |
|---|---|---|
| **A. Propuesta** | 1F0101 | DISPONIBLE completo. |
| B. | 1F0101 menos 1F0106 | Excluir los fondos en el BCRP (principalmente encaje legal, no disponible libremente). |

**Impacto:** los fondos en el BCRP son 68 % del disponible en la mediana. Con B el efectivo
bancario cae a menos de la mitad.

**Hallazgo de la validación:** en Credicorp, el efectivo NIIF que reporta a la SEC excluye
además el efectivo restringido; la diferencia fue 85,093 (0.2 %).

**Recomendación:** A, con advertencia. Para un banco el efectivo no se usa en ratios de
liquidez como en una empresa; lo importante es mantener el dato consistente con lo que
publica la SBS.

## 5. Deuda financiera (todos los planes salvo bancos)

En el plan general, "Otros Pasivos Financieros" (1D0309 + 1D0401) mezcla préstamos, bonos,
arrendamientos (NIIF 16) y derivados pasivos. Con esta data no se pueden separar.

**Impacto:** estos pasivos son 11.6 % del pasivo total en la mediana del plan general.

**Recomendación:** aceptar con la advertencia en el diccionario. La alternativa (no
publicar deuda) quita el ratio deuda/patrimonio, que es de los más usados.

## 6. Utilidad operativa en AFP, bancos y seguros

| plan | propuesta | duda |
|---|---|---|
| AFP | 2A03ST | Excluye el resultado del encaje legal (2A0304), que va debajo. ¿Incluirlo? |
| Bancos | 2F2801 "Resultado de operación" | Después de provisiones; es la línea más cercana. |
| Seguros | sin propuesta en individual; 2E1501 en consolidado | El formato individual no tiene una línea equivalente limpia. |

**Recomendación:** aceptar AFP y bancos; en seguros individual dejarlo vacío.

## 7. Años con plantillas previas a NIIF

La SMV reutiliza los mismos códigos con otro significado en los años antiguos. Ejemplos
de 2005 en el plan general: `2D01ST` era "Total de Ingresos Brutos" (incluía otros
ingresos operacionales), `2D04ST` era el resultado "antes de gastos extraordinarios,
participaciones e impuesto", y la participación de los trabajadores iba en una línea propia
(`2D0501`). En bancos, seguros y AFP, hasta alrededor de 2012 la línea era "antes de
participaciones e impuesto a la renta".

Esto importa porque la participación de los trabajadores (5 % a 10 % de la utilidad en el
Perú) hoy está dentro de los gastos de personal, por encima de la utilidad antes de
impuestos. Comparar sin ajustar sobreestima la utilidad antes de impuestos de los años
antiguos.

| opción | qué hace |
|---|---|
| a. | Aceptar con advertencia (marcar esos años como `propuesto`). |
| b. | Reconstruir: restar la participación de trabajadores donde viene separada. |
| c. | Dejar vacíos esos conceptos en los años previos al cambio de plantilla. |

**Qué hay implementado (como `propuesto`):** la opción b. Años de cambio encontrados:

| plan | plantilla antigua hasta | reconstrucción propuesta de utilidad antes de impuestos |
|---|---|---|
| D empresas | 2009 | 2D04ST + participación de trabajadores (2D0501) |
| I SAB | 2011 | 2I2121 + participaciones (2I2130) |
| F bancos | 2012 o después (por confirmar con el histórico) | 2F1301 + distribución legal de la renta neta (2F1402) |
| E seguros | 2012 o después | 2E1503 + participaciones (2E1601) |
| A AFP | 2012 o después | 2A04ST + participación (2A0501) |

Además, hasta 2009 los **ingresos** del plan general (2D01ST) eran "Total de Ingresos
Brutos" = ventas netas + otros ingresos operacionales. La propuesta toma solo ventas netas
(2D0101) para acercarlo a "ingresos de actividades ordinarias".

**Verificación:** utilidad antes de impuestos + impuesto = utilidad neta se cumple en 97.6 %
de los estados anuales del plan general hasta 2009 (con la reconstrucción), igual que en los
años NIIF (94 a 95 %; el resto son operaciones discontinuadas). En seguros y SAB antiguos
no se cumple porque había **partidas extraordinarias** debajo del impuesto; eso es correcto
y la utilidad neta se toma tal como fue reportada.

**Recomendación:** validar la opción b.

## 8. Interés minoritario en años antiguos

En las plantillas antiguas (plan general hasta 2005, bancos y seguros hasta 2010, y las
letras B y S) el interés minoritario, y a veces "contingencias" o "ganancias diferidas" en
las SAB, se presentaba **fuera** del pasivo total y del patrimonio total. Con NIIF el
interés minoritario (participaciones no controladoras) es parte del patrimonio.

Hoy la base deja `patrimonio_total` tal como fue reportado (coincide con el índice de la
SMV) y guarda esas partidas en el concepto `partidas_entre_pasivo_y_patrimonio`, que se
usa para verificar que el balance cuadre. En 2010, año de transición, algunas empresas ya
lo incluían dentro del patrimonio: eso se detecta presentación por presentación.

| opción | qué hace |
|---|---|
| **A. Actual** | Patrimonio tal como fue reportado. El ROE de años antiguos excluye al minoritario. |
| B. | Sumar el interés minoritario al patrimonio en años antiguos, para que sea comparable con NIIF. |

**Recomendación:** A para `patrimonio_total` (es el dato reportado) y documentarlo. El
impacto es chico en estados individuales, donde casi nunca hay interés minoritario.
