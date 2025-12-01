# Dashboard de Ventas y Predicción – Tienda Aurelion (Power BI)

## 1. Objetivo del tablero

El objetivo del dashboard es ofrecer una **vista integral del desempeño comercial de Tienda Aurelion**, permitiendo:

- Analizar las ventas por **producto, categoría, cliente y período**.
- Identificar **productos y clientes clave**.
- Relacionar el comportamiento **histórico** con las **predicciones de demanda** generadas por el modelo de Machine Learning desarrollado en el sprint anterior.
- Facilitar la toma de decisiones sobre **stock, compras y acciones comerciales** en base a datos.

### Preguntas de negocio que responde

- ¿Cuántas unidades se venden en total en un período dado?
- ¿Cuántos productos diferentes se comercializan?
- ¿Cuántas ventas (transacciones) se realizan y cuántos clientes están activos?
- ¿Cuáles son los **productos más vendidos** y qué porcentaje representan del total?
- ¿Quiénes son los **clientes más activos**?
- ¿Qué categorías concentran la mayor parte de las ventas?
- ¿Cuáles son los productos con **mayor demanda predicha** para el próximo mes según el modelo de ML?

---

## 2. Fuentes de datos utilizadas

Se utilizaron los mismos archivos del proyecto Aurelion, exportados a formato .csv:

- `ventas csv`  
  Información de cada venta (id_venta, id_cliente, fecha, medio_pago, email, nombre_cliente).

- `detalle_ventas csv`  
  Detalle de cada ítem vendido (id_venta, id_producto, cantidad, importe, nombre_producto, precio_unitario).

- `productos csv`  
  Catálogo de productos (id_producto, nombre_producto, categoría, precio_unitario).

- `clientes csv`  
  Datos básicos de clientes (id_cliente, nombre_cliente, email, ciudad, fecha_alta).

- `top_predichos`  
  Salida del modelo de Machine Learning (id_producto, nombre_producto, predicted_quantity) con la demanda estimada para el próximo mes.

Opcionales (de apoyo al análisis):

- `ranking_historico`  
  Ranking de productos más vendidos en el último mes histórico.

---

## 3. Modelo de datos en Power BI

### 3.1 Conexión y modo de carga

- Todos los archivos se conectaron desde **Power BI Desktop → Obtener datos → Texto/CSV**.
- Se utilizó el modo de carga **Importar**, ya que se trata de archivos locales de tamaño reducido y no se requiere conexión en tiempo real.

### 3.2 Esquema estrella

Se diseñó un **modelo en estrella** donde:

- **Tabla de hechos:**
  - `detalle_ventas csv`: contiene una fila por producto vendido en cada venta (cantidad, importe, id_venta, id_producto).

- **Tablas dimensión:**
  - `ventas csv`: datos generales de cada venta (id_venta, id_cliente, fecha, medio_pago, email).
  - `productos csv`: catálogo de productos (id_producto, nombre_producto, categoría).
  - `clientes csv`: datos de clientes (id_cliente, nombre_cliente, email, ciudad, fecha_alta).

- **Tablas satélite:**
  - `top_predichos`: demanda predicha por producto.
  - `ranking_historico`: ranking histórico de productos (último mes).

### 3.3 Relaciones y cardinalidad

Se definieron las siguientes relaciones:

- `ventas csv[id_venta]` (1) ──► (*) `detalle_ventas csv[id_venta]`
- `productos csv[id_producto]` (1) ──► (*) `detalle_ventas csv[id_producto]`
- `clientes csv[id_cliente]` (1) ──► (*) `ventas csv[id_cliente]`
- `productos csv[id_producto]` (1) ──► (*) `top_predichos[id_producto]`
- `productos csv[id_producto]` (1) ──► (*) `ranking_historico[id_producto]`

Características:

- Todas las relaciones se configuraron con **cardinalidad Uno a varios (1:*)**.
- La **dirección del filtro cruzado** se dejó en modo **Simple**, desde las dimensiones hacia las tablas de hechos/satélite, para respetar el sentido del análisis: filtrar ventas y predicciones por producto, cliente y período.

### 3.4 Limpieza de columnas y relaciones

- Se **eliminó** una relación innecesaria basada en el campo `email` entre `ventas csv` y `clientes csv`, quedando solo la relación por `id_cliente` como clave principal.
- Se **ocultaron** en la vista de informe las columnas técnicas utilizadas solo para relaciones (por ejemplo `id_venta`, `id_cliente`, `id_producto` en algunas tablas) y columnas duplicadas.
- No se utilizaron relaciones muchos-a-muchos, evitando ambigüedades en el modelo.

---

## 4. Medidas DAX principales

Para alimentar los KPIs y visualizaciones se crearon las siguientes medidas DAX
(se almacenaron en una tabla de soporte llamada `Medidas`):

```DAX
Unidades vendidas =
SUM ( 'detalle_ventas csv'[cantidad] )

Importe total =
SUM ( 'detalle_ventas csv'[importe] )

Transacciones =
DISTINCTCOUNT ( 'ventas csv'[id_venta] )

Clientes activos =
DISTINCTCOUNT ( 'ventas csv'[id_cliente] )

Productos únicos =
DISTINCTCOUNT ( 'detalle_ventas csv'[id_producto] )

Ticket promedio =
DIVIDE ( [Importe total], [Transacciones] )

% participación producto =
DIVIDE (
    [Importe total],
    CALCULATE ( [Importe total], ALL ( 'productos csv' ) )
)

% participación categoría =
DIVIDE (
    [Importe total],
    CALCULATE ( [Importe total], ALL ( 'productos csv'[categoria] ) )
)
```
Estas medidas permiten:

- Construir indicadores de nivel general (KPIs).
- Analizar la contribución relativa de cada producto o categoría al total de ventas.
- Revisar el comportamiento por cliente, producto y período.

---

## 5. Páginas del dashboard

El reporte se organizó en cuatro páginas principales.

### 5.1 Página 1 – Resumen

**Objetivo:** ofrecer una vista ejecutiva del estado general de la tienda.

Elementos:

- **Tarjetas (Cards) con KPIs:**
  - `Unidades vendidas`
  - `Productos únicos`
  - `Transacciones`
  - `Clientes activos`
  - `Ticket promedio`

- **Gráfico de barras – Ventas por categoría:**
  - Eje: `productos csv[categoria]`
  - Valor: `[Unidades vendidas]` (o `[Importe total]`)
  - Ordenado de mayor a menor.
  - Permite identificar qué categorías concentran la mayor parte de las ventas.

- **Segmentador (Slicer) de fecha (opcional):**
  - Campo: `ventas csv[fecha]`
  - Permite filtrar el análisis por período.

---

### 5.2 Página 2 – Productos

**Objetivo:** analizar el desempeño de los productos.

Elementos:

- **Gráfico de barras – Top 10 productos más vendidos (unidades):**
  - Eje: `productos csv[nombre_producto]`
  - Valor: `[Unidades vendidas]`
  - Filtro de visual: **Top N = 10** por `[Unidades vendidas]`.
  - Orden descendente para mostrar primero los productos de mayor rotación.

- **Tabla de detalle por producto (opcional):**
  - Columnas:
    - `productos csv[nombre_producto]`
    - `productos csv[categoria]`
    - `[Unidades vendidas]`
    - `[Importe total]`
    - `[% participación producto]`
  - Permite ver cuánto aporta cada producto al total de ventas, tanto en unidades como en importe.

Esta página responde a la pregunta:  
**“¿Qué productos son los más importantes para el negocio y cuánto representan?”**

---

### 5.3 Página 3 – Clientes

**Objetivo:** identificar los clientes más relevantes para la tienda.

Elementos:

- **Gráfico de barras – Top 10 clientes más activos:**
  - Eje: `clientes csv[nombre_cliente]`
  - Valor: `[Unidades vendidas]` o `[Importe total]`
  - Filtro de visual: **Top N = 10**.
  - Orden descendente.

- **Tabla de detalle por cliente (opcional):**
  - Columnas:
    - `clientes csv[nombre_cliente]`
    - `[Unidades vendidas]`
    - `[Importe total]`

Esta página permite detectar:

- Clientes que generan un **volumen significativo** de ventas.
- Posibles candidatos para **acciones de fidelización** o beneficios comerciales.

---

### 5.4 Página 4 – Predicciones

**Objetivo:** visualizar las predicciones de demanda generadas por el modelo de Machine Learning.

Elementos:

- **Relación de datos:**  
  La tabla `top_predichos` se relaciona con `productos csv` mediante `id_producto`, permitiendo usar los nombres y categorías de producto como contexto.

- **Gráfico de barras – Top 10 productos predichos (próximo mes):**
  - Eje: `productos csv[nombre_producto]`
  - Valor: `top_predichos[predicted_quantity]`
  - Filtro: **Top N = 10** por `predicted_quantity`.
  - Muestra los productos con mayor demanda esperada según el modelo de ML.

- **Comparación histórico vs predicho (opcional):**
  - Gráfico adicional con el Top 10 histórico (último mes), utilizando `[Unidades vendidas]` y/o la tabla `ranking_historico`.
  - Permite comparar productos que:
    - Se mantienen fuertes en ambos rankings.
    - Podrían estar **ganando** o **perdiendo** relevancia según la predicción.

Esta página conecta directamente el trabajo de **Machine Learning** (sprint 3) con la visualización final en Power BI.

---

## 6. Conclusiones

- El modelo de datos en Power BI se diseñó siguiendo un **esquema estrella**, con una tabla de hechos (`detalle_ventas csv`) y dimensiones de productos, clientes y ventas, lo que facilita la creación de medidas DAX y visualizaciones flexibles.
- El dashboard permite explorar las ventas desde distintas perspectivas (producto, categoría, cliente, período) y apoyarse en **KPIs claros** para evaluar el desempeño de la tienda.
- La integración de la tabla `top_predichos` incorpora las **predicciones de demanda** al análisis visual, permitiendo usar Power BI no solo para reportar el pasado, sino también para apoyar decisiones futuras.
- El trabajo realizado en los sprints anteriores (limpieza de datos, unificación de bases, entrenamiento del modelo de ML) se ve reflejado en un tablero final que integra **análisis descriptivo y predictivo** de manera coherente.

Este dashboard constituye la **entrega final del proyecto Tienda Aurelion**, combinando Python, Machine Learning y Power BI como herramientas complementarias para la toma de decisiones basadas en datos.

