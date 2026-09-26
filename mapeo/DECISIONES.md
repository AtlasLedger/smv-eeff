# Decisiones de criterio

Registro de las decisiones de criterio contable que definen los conceptos estándar. Se
tomaron el 2026-09-26 con criterio delegado por el propietario del proyecto , después de revisar cada una
contra los datos. Los valores que dependen de ellas llevan `confianza = validado` en
`estandar.parquet` y `ratios.parquet`; los que no requieren criterio llevan `directo`.

Para cambiar una decisión: editar `mapeo_cuentas.csv` y correr `python scripts/construir.py`.
Los controles de la construcción (cobertura, cruce con el índice SMV, identidades
contables) avisan si el cambio rompe algo.

Resumen:

| # | tema | decisión | ¿cambió respecto a la propuesta inicial? |
|---|---|---|---|
| 1 | Ingresos de bancos | Intereses + ingresos por servicios financieros | No |
| 2 | Ingresos de seguros | Primas emitidas netas (primas de seguros + reaseguro aceptado) | **Sí** (antes: primas ganadas netas) |
| 3 | Ingresos de SAB | Comisiones + intereses + otros + ganancia **neta** en venta de inversiones | No |
| 4 | Efectivo de bancos | Disponible completo | No |
| 5 | Deuda financiera | Todas las líneas de deuda de cada era | **Sí** (antes: solo las líneas NIIF) |
| 6 | Utilidad operativa | AFP sin encaje, bancos "resultado de operación", seguros "resultado de operación" | **Sí** en seguros (antes: vacío) |
| 7 | Plantillas previas a NIIF | Reconstruir utilidad antes de impuestos; ingresos tal como se reportaron | **Sí** en ingresos (antes: solo ventas netas) |
| 8 | Interés minoritario antiguo | Patrimonio tal como fue reportado | No |

---

## 1. Ingresos de bancos y financieras

**Decisión:** intereses + ingresos por servicios financieros (2F0101 + 2F2402). En la
plantilla consolidada, ingresos ordinarios + comisiones netas (2F01ST + 2F2406), porque no
trae comisiones brutas.

**Por qué:** la SMV usa solo intereses, lo que deja fuera las comisiones (tarjetas,
transferencias, cartas fianza), una línea de negocio central. Con la decisión los ingresos
suben 14 % en la mediana. Se descartó sumar también el resultado por operaciones
financieras (cambio de moneda, negociación) porque es un resultado neto y volátil.

## 2. Ingresos de seguros

**Decisión:** primas de seguros netas + reaseguro aceptado (+ aportes de afiliados EPS en el
consolidado): 2E0101 + 2E0102 + 2E0108.

**Por qué cambió:** la propuesta inicial eran las primas ganadas netas. Al revisarlo contra
los datos, esa línea incluye el ajuste de reservas técnicas, que en seguros de vida y rentas
vitalicias puede ser la mitad de las primas o más. Con primas ganadas, el ingreso sale
negativo o cero en 2 % de los estados y el margen neto llega a 118 % en el percentil 99;
con primas emitidas, 0.3 % y 42 %. Las primas ganadas netas se conservan como concepto
propio para la siniestralidad, donde sí son la medida correcta.

## 3. Ingresos de sociedades agentes de bolsa

**Decisión:** comisiones + intereses + otros ingresos + ganancia **neta** en venta de
inversiones (venta menos costo de enajenación).

**Por qué:** la SMV usa el valor bruto de las inversiones vendidas. Con eso, los ingresos
eran 4.5 veces los reales en la mediana y hasta 1,147 veces (Larrain Vial SAB 2024: S/ 19,172
millones contra S/ 16.7 millones). Vender en 100 algo que costó 99 no es un ingreso de 100.

## 4. Efectivo de bancos

**Decisión:** disponible completo (incluye los fondos en el BCRP).

**Por qué:** es como lo presenta la SBS y es consistente con NIIF: el efectivo que Credicorp
reporta a la SEC también incluye los depósitos en el BCRP (solo excluye el efectivo
restringido, 0.2 % de diferencia). Excluir el encaje reduciría el efectivo a menos de la
mitad sin ganar comparabilidad, porque en bancos el efectivo no se lee como en una empresa.

## 5. Deuda financiera

**Decisión:** en cada plan, la suma de todas las líneas de deuda financiera de todas las eras
de la plantilla (sobregiros, préstamos, parte corriente de deuda de largo plazo, deuda de
largo plazo y derivados pasivos). Desde NIIF eso es "Otros Pasivos Financieros", que también
incluye arrendamientos. En bancos no aplica: para un banco la deuda es su materia prima.

**Por qué cambió:** la regla inicial solo tomaba las líneas NIIF. Al revisar los años
antiguos, antes de 2006 la deuda de corto plazo estaba en otras líneas y la regla solo
capturaba la de largo plazo. Con la corrección, la mediana de deuda / patrimonio del plan
general es 0.27 (2000-2005), 0.18 (2006-2010) y 0.20 (desde 2011).

**Advertencia que queda:** desde NIIF 16 incluye arrendamientos y no se pueden separar con
esta data. Es la práctica habitual de los analistas después de NIIF 16.

## 6. Utilidad operativa

**Decisión:**

| plan | cuenta |
|---|---|
| AFP | 2A03ST: sin el resultado del encaje legal, que es el rendimiento de mercado de la inversión obligatoria de la AFP en sus fondos |
| Bancos | 2F2801 "Resultado de operación" (después de provisiones) |
| Seguros | 2E1501 "Resultado de operación"; en individual desde 2010, 2E1508 (en esa plantilla no hay partidas entre el resultado de operación y el impuesto); en individual 2010-2012 con la plantilla anterior, 2E1503 |

**Por qué cambió en seguros:** la propuesta inicial era dejarlo vacío. Al revisar las
plantillas se vio que sí hay una línea equivalente y que las tres nunca coinciden en una
misma presentación. Incluye el resultado de inversiones, que en seguros es parte del
negocio. Los gastos financieros de seguros mezclan gastos de inversiones y financieros; se
aceptan con esa advertencia.

## 7. Años con plantillas previas a NIIF

**Decisión:** la utilidad antes de impuestos de los años antiguos se reconstruye restando la
participación de los trabajadores, que antes iba debajo y con NIIF va dentro de los gastos
de personal. Los ingresos del plan general se toman tal como fueron reportados (2D01ST, total
de ingresos brutos).

**Evidencia:** en su primer estado con la plantilla nueva, las empresas reexpresaron el año
anterior. Esa cifra reexpresada permite probar qué definición antigua es la correcta:

| prueba | reconstruida | sin ajustar |
|---|---|---|
| Utilidad antes de impuestos, plan general (2009 reexpresado en 2010) | 49 % coincide | 26 % |
| Utilidad antes de impuestos, bancos (2010 reexpresado en 2011) | 64 % | 17 % |
| Utilidad operativa, plan general | 35 % | 34 % |

La reconstrucción gana en la utilidad antes de impuestos; en la utilidad operativa no hace
diferencia y por eso no se aplica ahí. El resto de casos no coincide por otros ajustes de
la adopción de NIIF.

**Por qué cambió en ingresos:** la propuesta inicial era usar solo ventas netas (2D0101). La
misma prueba mostró que al reexpresar 2009 las empresas mantuvieron el total de ingresos
brutos (87 % de coincidencia contra 76 %).

Además, utilidad antes de impuestos + impuesto = resultado antes de partidas extraordinarias
se cumple en 99.9 % de los estados antiguos (control permanente en `data/calidad.json`).

## 8. Interés minoritario en años antiguos

**Decisión:** `patrimonio_total` tal como fue reportado (coincide con el índice de la SMV).
El interés minoritario que las plantillas antiguas ponían fuera del pasivo y del patrimonio
queda en `partidas_entre_pasivo_y_patrimonio`.

**Por qué:** es consistente dentro de cada era. En las plantillas antiguas la utilidad neta
era la atribuible a los accionistas de la controladora y el patrimonio excluía al
minoritario; con NIIF ambos lo incluyen. Sumar el minoritario al patrimonio antiguo
mezclaría una utilidad sin minoritario con un patrimonio con minoritario y distorsionaría el
ROE. En estados individuales el efecto es casi nulo.

---

## Otra decisión tomada en la misma revisión

**Margen financiero bruto en el consolidado bancario:** ingresos por intereses + gastos por
intereses (2F0101 + 2F0301), y no la línea "MARGEN BRUTO", que en conglomerados como
Credicorp incluye primas y siniestros de seguros.
