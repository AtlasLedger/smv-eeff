# Bitácora de trabajo autónomo

Registro de lo que se avanzó sin intervención de el propietario del proyecto, de lo que quedó pendiente y de
las decisiones que necesitan su validación. La sección de arriba siempre está al día.

## Estado actual

- Paso 1 (extractor): listo. Descarga histórica 2000-2026 en curso para balance,
  resultados, flujo, integrales e índice (`logs/historico_1.out`). Si se cortó, volver a
  correr el mismo comando: continúa donde quedó.
- Paso 2 (mapeo): **propuesta** lista en `mapeo/`. Faltan las decisiones de criterio (abajo).
- Paso 3 (modelo): listo. `python scripts/construir.py` genera `data/`.
- Paso 4 (validación): 64 cifras OK + 2 diferencias explicadas, en 5 empresas y 5
  plantillas (Alicorp consolidado PEN, BCP individual banco, Credicorp consolidado
  conglomerado, Buenaventura consolidado USD, Rimac individual seguros).
  `validacion/reporte.md`. Faltan: una SAB (plan I; no encontré su estado auditado
  individual en línea) y una AFP (plan A); y validar años antiguos.
- Paso 5 (publicación): pendiente; requiere cuentas de el propietario del proyecto (GitHub, Zenodo).

## Decisiones que necesitan a el propietario del proyecto

**Documento para decidir, con opciones, recomendación e impacto medido: `mapeo/DECISIONES.md`.**
Todas están en `mapeo/mapeo_cuentas.csv` con `confianza = propuesto` o `pendiente`.
Mientras no se validen, cada valor y ratio que dependa de ellas sale marcado como
`propuesto` en `data/estandar.parquet` y `data/ratios.parquet`.

1. **Ingresos de bancos.** La SMV usa solo ingresos por intereses (2F0101). Propuesta:
   intereses + ingresos por servicios financieros (2F0101 + 2F2402).
2. **Ingresos de seguros.** La SMV usa primas netas antes de cesiones (2E0201). Propuesta:
   primas ganadas netas (2E0602).
3. **Ingresos de SAB.** La SMV usa Total Ingresos Operacionales (2I2031), que incluye el
   valor bruto de inversiones vendidas (Credicorp Capital SAB 2024: 1,577 millones de
   venta de inversiones contra 46 millones de comisiones). Propuesta: comisiones +
   intereses + otros + ganancia NETA por venta de inversiones.
4. **Efectivo de bancos.** DISPONIBLE incluye el encaje en el BCRP. ¿Se deja o se excluye?
5. **Deuda financiera.** En el plan general "Otros Pasivos Financieros" mezcla deuda,
   arrendamientos NIIF 16 y derivados. No se puede separar con esta data. ¿Se acepta con
   la advertencia?
7. **Plantillas previas a NIIF (años antiguos).** La SMV reutiliza los mismos códigos con
   otro significado. En 2005: `2D01ST` era "Total de Ingresos Brutos" (incluye otros
   ingresos operacionales), `2D04ST` era "antes de gastos extraordinarios,
   participaciones e impuesto" y la participación de trabajadores iba aparte (`2D0501`).
   Bancos, seguros y AFP hasta ~2012 reportan "antes de participaciones e impuesto".
   Hoy el mapeo aplica el significado moderno a todos los años; para esos conceptos en
   años antiguos hay que decidir si (a) se acepta con advertencia, (b) se reconstruye
   (ej. restar la participación) o (c) se deja vacío. El mapeo ya admite `desde`/`hasta`.
   Lista para revisar: `data/mapeo_revisar_descripciones.csv`.
6. **Utilidad operativa** de AFP (¿incluye el encaje legal?), bancos (2F2801) y seguros
   (no hay línea equivalente).

## Hallazgos (para el README y la documentación)

- El plan `2I` no documentado = sociedades agentes de bolsa (19 empresas).
- El encoding roto está en origen: la SMV manda un espacio o `¿` donde iba la letra.
  Afecta campos de catálogo (Moneda, MetodoFlujoEfectivo) y descripciones del plan V.
  Se repara con diccionario explícito (`smv/limpieza.py`).
- RPJ de las SAB con espacios de relleno. RUC = 0 para holdings extranjeros.
- Trimestres: en resultados y ORI, Monto1 = trimestre, Monto3 = acumulado del año,
  Monto2/Monto4 = mismos períodos del año anterior. En el FLUJO DE EFECTIVO, Monto1 ya es
  el acumulado del año (verificado con la variación del efectivo en el balance de
  Alicorp); la base lo guarda en monto_acumulado. Anual: solo Monto1/Monto2. Balance:
  Monto2 = cierre del ejercicio anterior.
- Montos en miles: confirmado en la validación (Alicorp, BCP, Credicorp, Buenaventura).
- `obtener_EFData` es una grilla paginada que siempre devuelve 0 registros: se descarta.
- CambiosPatrimonio: 79 MB y ~5.5 min por llamada; 93 % de celdas en cero. Las SAB
  repiten los códigos de fila en dos bloques (año anterior y actual).
- Las SAB usan el prefijo 4 en el flujo y el 3 en patrimonio (al revés que el resto).
- Control cruzado: los totales de activo, pasivo, patrimonio y utilidad neta coinciden
  al 100 % con el índice que publica la SMV (9,897 comparaciones, 0 discrepancias).
  OJO: una primera versión reportaba "0 discrepancias" sin comparar nada (el ejercicio
  llegaba como texto en una tabla y como número en otra). Corregido y con prueba.
- Bancos: el consolidado usa OTRA plantilla (formato de conglomerado financiero, con
  líneas de seguros y corriente/no corriente). El mapeo distingue individual y consolidado.
  En el consolidado no se puede calcular morosidad (solo desglosa la cartera corriente).
- ESCALA MIXTA: en las SAB de 2005 y 2010, dentro de una MISMA presentación, las líneas
  de total (en MAYÚSCULAS en la plantilla) venían en soles y las de detalle en miles con
  decimales (77.065 de comisiones = 77,065 de total de ingresos). Se detecta comparando el
  activo total con el índice SMV (razón ~1000) y se dividen entre 1000 solo las líneas de
  total. Verificado: las líneas en mayúsculas son ~1000x y las demás no. Un primer intento
  dividía todo y dejaba el detalle 1000 veces más chico: lo detectó la revisión de ratios.
- Nuevo control: activo = pasivo + patrimonio en cada presentación (0 descuadres).
- SAB, estado de resultados TRIMESTRAL: el Monto1 de la SMV no es el trimestre (0 % de
  coincidencia con acumulado T(n) - acumulado T(n-1) en 2021, 2024 y 2025; en el resto de
  planes el mismo método da 87-100 %). Parece el último mes. Se deja nulo y se conserva
  el acumulado. El flujo de las SAB sí es acumulado como el de todos.
- Presentación doble: BNB Valores SAB (SG0005) presentó 2021-T1/T2 en el plan de SAB y en
  el general a la vez. La guarda contra reglas superpuestas lo detectó (si no, el activo
  salía duplicado). Se usa el plan que corresponde al tipo de empresa. Quedan 2
  diferencias de 1 (miles) contra el índice por redondeo entre ambas versiones.
- Diferencias de presentación SBS vs estado auditado NIIF (no son errores de la base):
  prima al fondo de seguro de depósitos (BCP) y efectivo restringido (Credicorp).

## Registro

### 2026-09-26, madrugada
- Entorno, pruebas, primera descarga real, fix del perfilador (pandas 3 + RE2).
- Perfiles de balance, resultados y flujo 2024; catálogo de cuentas en `catalogos/`.
- Limpieza (`smv/limpieza.py`), modelo dimensional (`smv/modelo.py`), capa estandarizada
  (`smv/estandar.py`), propuesta de mapeo (`mapeo/`), 17 pruebas pasando.
- Descarga histórica lanzada (recientes primero).
- Validación (Alicorp, BCP, Credicorp y Buenaventura; estas dos contra la API XBRL de la SEC).
- README, diccionario, licencias (MIT código + ODbL datos), exportación CSV, workflows.

## Antes de publicar (necesita a el propietario del proyecto)

1. Crear el repo público en GitHub y hacer push. Quitar `data/` de `.gitignore` cuando
   el histórico esté completo (hoy está excluido para no llenar el historial de git).
2. Primera corrida manual del workflow `actualizar` (Actions > actualizar > Run). Riesgo
   a verificar: que el servidor de la SMV acepte conexiones desde GitHub (EE. UU.).
3. Zenodo: conectar la cuenta de GitHub y crear un release para obtener el DOI.
4. Revisar el nombre en `LICENSE` (puse "el propietario del proyecto ").
