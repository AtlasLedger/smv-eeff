# Perfil histórico de la base

- Empresas: **494**
- Ejercicios: 2005 a 2026
- Presentaciones de balance: 12,258

## Presentaciones por año

Empresas con balance anual (A) y número de presentaciones trimestrales, por tipo.

| ejercicio | anual_C | anual_I | trimestres_C | trimestres_I |
|---|---|---|---|---|
| 2005 | 0 | 246 | 0 | 0 |
| 2006 | 0 | 242 | 0 | 0 |
| 2007 | 0 | 263 | 0 | 0 |
| 2008 | 0 | 275 | 0 | 0 |
| 2009 | 0 | 278 | 0 | 0 |
| 2010 | 0 | 279 | 0 | 0 |
| 2011 | 0 | 289 | 0 | 0 |
| 2012 | 0 | 294 | 0 | 0 |
| 2020 | 97 | 297 | 0 | 273 |
| 2021 | 91 | 290 | 358 | 1076 |
| 2022 | 87 | 284 | 342 | 1065 |
| 2023 | 87 | 280 | 331 | 1049 |
| 2024 | 86 | 276 | 329 | 1028 |
| 2025 | 77 | 274 | 330 | 1025 |
| 2026 | 0 | 0 | 156 | 504 |


## Planes de cuentas por año (empresas con balance anual individual)

| ejercicio | A | B | C | D | E | F | I | S | V |
|---|---|---|---|---|---|---|---|---|---|
| 2005 | 0 | 23 | 1 | 190 | 0 | 0 | 19 | 13 | 0 |
| 2006 | 0 | 0 | 1 | 187 | 13 | 22 | 19 | 0 | 0 |
| 2007 | 0 | 0 | 1 | 205 | 12 | 25 | 20 | 0 | 0 |
| 2008 | 0 | 0 | 1 | 212 | 12 | 27 | 23 | 0 | 0 |
| 2009 | 0 | 0 | 1 | 212 | 13 | 30 | 22 | 0 | 0 |
| 2010 | 4 | 0 | 1 | 204 | 13 | 34 | 23 | 0 | 0 |
| 2011 | 4 | 0 | 1 | 210 | 14 | 35 | 25 | 0 | 0 |
| 2012 | 4 | 0 | 1 | 212 | 14 | 39 | 24 | 0 | 0 |
| 2020 | 4 | 0 | 0 | 212 | 18 | 41 | 21 | 0 | 1 |
| 2021 | 4 | 0 | 0 | 205 | 18 | 41 | 21 | 0 | 1 |
| 2022 | 4 | 0 | 0 | 200 | 17 | 42 | 20 | 0 | 1 |
| 2023 | 4 | 0 | 0 | 197 | 17 | 42 | 19 | 0 | 1 |
| 2024 | 4 | 0 | 0 | 194 | 17 | 41 | 19 | 0 | 1 |
| 2025 | 4 | 0 | 0 | 192 | 17 | 40 | 20 | 0 | 1 |


## Moneda de reporte por año (balance anual individual)

| ejercicio | PEN | USD |
|---|---|---|
| 2005 | 219 | 27 |
| 2006 | 200 | 42 |
| 2007 | 230 | 33 |
| 2008 | 247 | 28 |
| 2009 | 248 | 30 |
| 2010 | 249 | 30 |
| 2011 | 257 | 32 |
| 2012 | 261 | 33 |
| 2020 | 265 | 32 |
| 2021 | 261 | 29 |
| 2022 | 255 | 29 |
| 2023 | 251 | 29 |
| 2024 | 246 | 30 |
| 2025 | 245 | 29 |


## Correcciones de escala

Presentaciones cuyos totales venían en unidades (o sin índice para verificarlo):

| ejercicio | unidades |
|---|---|
| 2005 | 19 |
| 2006 | 19 |
| 2007 | 20 |
| 2008 | 23 |
| 2009 | 22 |
| 2010 | 23 |
| 2011 | 25 |


## Encoding todavía sospechoso

Descripciones de cuentas que siguen pareciendo rotas después de la limpieza. Si aparece algo aquí, hay que agregarlo al diccionario de `smv/limpieza.py`.

_Ninguna._

## Calidad (de `data/calidad.json`)

```json
{
  "patrimonio_celdas_bloque_repetido": 4560,
  "archivos_vacios": 30,
  "archivos_procesados": 307,
  "presentaciones_en_dos_planes": [
    "SG0005 2020-1-I obtener_BalanceGeneral: se usa plan I",
    "SG0005 2021-1-I obtener_BalanceGeneral: se usa plan I",
    "SG0005 2021-2-I obtener_BalanceGeneral: se usa plan I",
    "SG0005 2021-3-I obtener_BalanceGeneral: se usa plan I",
    "SG0005 2020-1-I obtener_GanciaPerdida: se usa plan I",
    "SG0005 2021-1-I obtener_GanciaPerdida: se usa plan I",
    "SG0005 2021-2-I obtener_GanciaPerdida: se usa plan I",
    "SG0005 2021-3-I obtener_GanciaPerdida: se usa plan I",
    "SG0005 2021-1-I obtener_FlujoEfectivo: se usa plan I",
    "SG0005 2021-2-I obtener_FlujoEfectivo: se usa plan I",
    "SG0005 2021-3-I obtener_FlujoEfectivo: se usa plan I"
  ],
  "presentaciones_con_totales_en_unidades": 151,
  "patrimonio_escala_no_verificada": 0,
  "sab_antiguas_sin_indice_escala_no_verificada": 0,
  "planes_sin_mapeo": [],
  "mapeo_cuentas_con_descripcion_cambiante": 53,
  "balances_que_no_cuadran": 0,
  "control_cruzado_indice_smv_comparaciones": 47499,
  "control_cruzado_indice_smv_discrepancias": 2,
  "mapeo_conceptos_con_cobertura_menor_90pct": []
}
```
