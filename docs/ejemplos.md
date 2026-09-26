# Ejemplos de uso

Montos en miles de la moneda de reporte. Todos los ejemplos se probaron sobre la base.

## Excel o Power BI

Abrir `data/csv/resumen_anual.csv`: una fila por empresa, año y tipo de estado, con los
conceptos principales y los ratios en columnas. La columna `conceptos_con_criterio` indica
qué valores de la fila dependen de una decisión de criterio contable (documentadas en
`mapeo/DECISIONES.md`).

## Python (pandas)

```python
import pandas as pd

empresas = pd.read_parquet("data/empresas.parquet")
ratios = pd.read_parquet("data/ratios.parquet")

# ROE consolidado 2024, de mayor a menor
roe = (ratios.query("ratio == 'roe' and periodo == 'A' and tipo == 'C' and ejercicio == 2024")
             .merge(empresas[["rpj", "nombre"]], on="rpj")
             .sort_values("valor", ascending=False))

# Detalle por cuenta de un año (cada año es un archivo)
hechos_2024 = pd.read_parquet("data/hechos/ejercicio=2024")
```

## SQL con DuckDB

DuckDB lee los Parquet directamente, sin servidor (`pip install duckdb`).

```sql
-- Las 5 empresas con mayor ROE consolidado en 2024
SELECT e.nombre, r.ejercicio, round(r.valor * 100, 1) AS roe_pct, r.confianza
FROM 'data/ratios.parquet' r JOIN 'data/empresas.parquet' e USING (rpj)
WHERE r.ratio = 'roe' AND r.periodo = 'A' AND r.tipo = 'C' AND r.ejercicio = 2024
ORDER BY r.valor DESC
LIMIT 5;

-- Ingresos anuales consolidados de una empresa, leyendo todos los años a la vez
SELECT h.ejercicio, h.monto AS ingresos
FROM read_parquet('data/hechos/*/*.parquet', hive_partitioning = true) h
JOIN 'data/empresas.parquet' e USING (rpj)
WHERE e.nombre = 'ALICORP S.A.A.' AND h.cuenta = '2D01ST'
  AND h.periodo = 'A' AND h.tipo = 'C'
ORDER BY h.ejercicio;

-- Morosidad mediana de bancos y financieras por año
SELECT ejercicio, round(median(valor) * 100, 1) AS morosidad_mediana_pct, count(*) AS entidades
FROM 'data/ratios.parquet'
WHERE ratio = 'morosidad' AND periodo = 'A'
GROUP BY ejercicio
ORDER BY ejercicio;
```

## Cosas a tener en cuenta

- Para comparar empresas de distinto sector usa `estandar.parquet` o `ratios.parquet`, no
  los códigos de cuenta: cada plan de cuentas usa códigos distintos.
- Filtra por `confianza = 'directo'` si solo quieres cifras que no dependen de ninguna
  decisión de criterio (`validado` = depende de una decisión documentada).
- Revisa la moneda (`presentaciones.moneda`) antes de sumar empresas: unas 30 reportan en
  dólares.
- En trimestres, `monto` es el trimestre aislado y `monto_acumulado` el acumulado del año
  (en el flujo de efectivo solo hay acumulado).
