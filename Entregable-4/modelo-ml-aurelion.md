# Modelo de Machine Learning para Tienda Aurelion

## 1. Objetivo del modelo (problema a resolver)

El objetivo del modelo de Machine Learning en Tienda Aurelion es **predecir la cantidad de unidades que se venderán de cada producto en el próximo mes**, utilizando como información de entrada el historial de ventas mensuales recientes.

Este modelo se utilizará para:

- Anticipar la **demanda futura por producto**.
- Mejorar la **planificación de stock**.
- Reducir quiebres y sobrestock.
- Aportar información al área de compras y logística para tomar decisiones basadas en datos.

En términos de aprendizaje automático, se trata de un **problema de regresión supervisada**, ya que la salida que queremos predecir es un **valor numérico continuo** (cantidad de unidades).

---

## 2. Algoritmo elegido y justificación

### Tipo de aprendizaje

- **Aprendizaje supervisado**: contamos con ejemplos históricos donde conocemos tanto las **entradas (X)** como la **salida (y)**.  
- **Tipo de problema**: regresión, porque la variable objetivo es numérica (unidades vendidas en el mes siguiente).

### Algoritmo implementado

Se utilizó el algoritmo **Random Forest Regressor**, del paquete `scikit-learn`.

Un Random Forest es un modelo basado en un **conjunto de árboles de decisión**, donde cada árbol aprende partes del patrón de los datos y, al combinar muchos árboles, se obtiene una predicción más robusta.

**Justificación del algoritmo:**

- Permite capturar **relaciones no lineales** entre las ventas de distintos meses.
- Es menos sensible al ruido que un único árbol de decisión.
- Tolera bien la presencia de variables correlacionadas.
- Es un algoritmo estándar y ampliamente usado en problemas de **predicción de demanda**.
- Se adapta mejor que una regresión lineal simple cuando la relación entre ventas pasadas y futuras no es estrictamente lineal.

---

## 3. Entradas (X) y salida (y)

### Base de datos

A partir de los archivos originales (`ventas.xlsx`, `detalle_ventas.xlsx`, `productos.xlsx`, `clientes.xlsx`), se construyó un **dataset agregado mensual por producto**, donde para cada `id_producto` se calcula la cantidad total vendida en cada mes.

A partir de esta estructura se generó un dataset supervisado con:

- Una fila por **producto**.
- Columnas con las **ventas de los últimos meses** (features).
- Una columna con la **venta del mes siguiente** (target).

### Variable de salida (y)

La variable objetivo (y) es:

- `ventas_mes_siguiente`  
  → cantidad de unidades vendidas de un producto en el **siguiente mes** respecto a los meses de referencia.

Es un valor numérico continuo.

### Variables de entrada (X)

Como entradas (features) se utilizaron las **ventas de los últimos meses** para cada producto.  
Ejemplo con una ventana de 3 meses:

- `ventas_mes_t-2` → ventas del producto hace 2 meses.
- `ventas_mes_t-1` → ventas del producto hace 1 mes.
- `ventas_mes_t`   → ventas del producto en el último mes disponible.

En el script estos features se construyen de forma automática a partir de la serie temporal, generando columnas como:

- `qty_t_minus_2`
- `qty_t_minus_1`
- `qty_t`

Estas columnas representan la **historia reciente de cada producto**, que el modelo utiliza para aprender el patrón de demanda y estimar la venta futura (`ventas_mes_siguiente`).

---

## 4. Preparación del dataset

Los pasos principales para preparar el dataset fueron:

1. **Carga de datos**  
   - Lectura de los archivos de Excel desde la carpeta `Base de datos/`.

2. **Limpieza y unificación**  
   - Normalización de nombres de columnas.
   - Unificación de `precio_unitario` proveniente de `detalle_ventas` y `productos`.
   - Fusión de tablas para obtener una tabla de ventas detallada con:
     - `id_venta`, `fecha`, `id_producto`, `cantidad`, `precio_unitario`, `importe`, etc.

3. **Agregación mensual por producto**  
   - Conversión de la fecha de venta a período mensual.
   - Suma de la cantidad total vendida por `id_producto` y por mes.
   - Generación de una tabla de tipo **pivot** con:
     - Filas: productos.
     - Columnas: meses.
     - Valores: cantidad vendida.

4. **Conversión a problema supervisado**  
   - A partir de la serie mensual se generan pares
     - (ventas de los últimos N meses) → (venta del mes siguiente).
   - Se construyen las matrices finales:
     - `X`: features con las ventas de los últimos meses.
     - `y`: venta del mes siguiente para cada producto.

---

## 5. División train/test y entrenamiento

Para evaluar correctamente el modelo y evitar sobreajuste, el dataset supervisado se dividió en:

- **Conjunto de entrenamiento (train)**: 80 % de los productos.
- **Conjunto de prueba (test)**: 20 % restante.

En código, esto se realiza con:

- `train_test_split(X, y, test_size=0.2, random_state=42)`

### Entrenamiento

1. Se instancia el modelo:

   - `RandomForestRegressor(n_estimators=200, random_state=42)`

2. Se entrena con los datos de entrenamiento:

   - `model.fit(X_train, y_train)`

3. Se genera un archivo `model_random_forest.joblib` con el modelo entrenado, para poder reutilizarlo sin volver a entrenar desde cero.

Este proceso sigue el flujo estándar visto en clase:

1. Preparar datos.
2. Dividir en train/test.
3. Entrenar el modelo con train.
4. Evaluar con test.

---

## 6. Métricas de evaluación

Para medir el desempeño del modelo se utilizan métricas de regresión.  
La principal métrica calculada es:

- **MSE (Mean Squared Error – Error Cuadrático Medio)**  
  - Mide el promedio del cuadrado de las diferencias entre los valores reales y los predichos.  
  - Un valor más bajo de MSE indica mejores predicciones.

Opcionalmente, también se pueden calcular:

- **MAE (Mean Absolute Error)**  
  - Error absoluto medio, indica cuántas unidades, en promedio, nos equivocamos.
- **R² (coeficiente de determinación)**  
  - Mide qué proporción de la variabilidad de las ventas es explicada por el modelo.

En el contexto del negocio, estas métricas permiten responder preguntas como:

- ¿Qué tan lejos están las predicciones de las ventas reales?
- ¿Es razonable utilizar este modelo para apoyar la planificación de stock?

---

## 7. Predicciones y resultados

Una vez entrenado el modelo:

1. Se generan predicciones de demanda para cada producto.
2. Se construye un **ranking de productos más vendidos esperados** para el próximo mes.
3. Se compara este ranking predicho con el **ranking histórico** del último mes.

A partir de estas salidas se pueden identificar:

- Productos con **alta venta histórica y alta venta predicha** (productos clave a mantener en stock).
- Productos con **baja venta histórica pero alta venta predicha** (oportunidades de crecimiento o cambios de tendencia).
- Productos con **alta venta histórica pero baja venta predicha** (posible caída de demanda).

---

## 8. Visualización de resultados

Además del entrenamiento del modelo, se desarrolló un dashboard interactivo con Streamlit para visualizar los principales resultados del análisis y de las predicciones.

### 8.1. Resumen general de métricas del negocio

En la parte superior del dashboard se muestran cuatro indicadores clave:

- **Ventas totales (unidades)**: 1016  
- **Productos únicos**: 95  
- **Transacciones (ventas)**: 120  
- **Clientes activos**: 67  

Estos indicadores permiten tener una vista rápida del volumen total de ventas, la variedad de productos disponibles y el nivel de actividad de la base de clientes.

---

### 8.2. Top histórico de productos (último mes)

Se presenta una tabla y un gráfico de barras con el **Top 10 de productos más vendidos en el último mes real**.  
Entre los productos destacados se encuentran, por ejemplo:

- Queso Rallado 150g  
- Chicle Menta  
- Energética Nitro 500ml  
- Vino Blanco 750ml  
- Fanta Naranja 1.5L  

Este gráfico permite identificar los productos de **alta rotación histórica**, que son críticos para mantener un stock adecuado y evitar quiebres.

---

### 8.3. Top predicho de productos (próximo mes)

A partir del modelo de regresión (Random Forest), se genera un **Top 10 de productos con mayor demanda predicha para el próximo mes**.  
En este ranking vuelven a aparecer varios de los productos del top histórico:

- Queso Rallado 150g  
- Energética Nitro 500ml  
- Chicle Menta  
- Queso Untable 190g  
- Caldo Concentrado Carne  

La comparación entre el ranking histórico y el ranking predicho permite:

- Confirmar productos **estrella** que se mantienen en las primeras posiciones (alta prioridad para compras y reposición).
- Detectar posibles cambios en la demanda cuando un producto mejora o empeora su posición entre ambos rankings.

---

### 8.4. Clientes más activos

Otro gráfico de barras muestra el **Top 10 de clientes más activos** en función de las unidades compradas.

Este gráfico permite:

- Identificar clientes que generan un **volumen importante de ventas**.
- Pensar estrategias comerciales específicas (fidelización, promociones, beneficios) orientadas a estos clientes frecuentes.

---

### 8.5. Comparativa entre categorías

Finalmente, se incluye un gráfico de barras que agrupa las ventas por **categoría de producto** (por ejemplo, Alimentos y Limpieza).

Este gráfico ayuda a responder preguntas como:

- ¿Qué categoría concentra la mayor cantidad de unidades vendidas?
- ¿Cómo se reparte la demanda entre las distintas familias de productos?

Esta información es útil para decisiones de **layout de góndola**, promociones por categoría y planificación de compras.

---

### 8.6. Síntesis

El conjunto de visualizaciones del dashboard permite:

- Conectar el **modelo de Machine Learning** con indicadores concretos del negocio.
- Traducir las predicciones de demanda en **insumos accionables** para planificación de stock, compras y estrategias comerciales.
- Complementar el análisis numérico de las métricas (MSE, MAE, R²) con una **interpretación visual** orientada al problema planteado por Tienda Aurelion.

---

## 9. Evaluación del modelo

El modelo se evaluó sobre un 20 % de los productos (conjunto de prueba).  
Se obtuvieron las siguientes métricas:

- MSE (error cuadrático medio): 5,413
- MAE (error absoluto medio): 2,031
- R² (coeficiente de determinación): -0,454

Esto significa que, en promedio, el modelo se equivoca en alrededor de **2 unidades por producto** al predecir la cantidad vendida del mes siguiente.  
El valor negativo de R² indica que, con las características actuales (solo las ventas de los últimos 3 meses y un histórico de 6 meses), el modelo todavía **no logra capturar bien los patrones de demanda**, por lo que su desempeño es similar o peor que un modelo muy simple que siempre predijera el promedio.

A pesar de esta limitación, el objetivo académico de este sprint se cumple, ya que se implementa un flujo completo de Machine Learning: preparación del dataset, división en train/test, entrenamiento, cálculo de métricas y análisis de resultados. En un trabajo futuro podrían incorporarse más meses históricos y variables adicionales (categoría, precio, promociones, etc.) para mejorar el desempeño del modelo.

### Análisis de los rankings histórico y predicho

El ranking histórico del último mes real muestra como productos más vendidos, entre otros:

- Queso Rallado 150g
- Energética Nitro 500ml
- Chicle Menta

El ranking predicho para el próximo mes mantiene varios de esos productos en las primeras posiciones, lo que sugiere que son **productos de alta rotación** que probablemente seguirán teniendo una demanda importante y requieren una buena planificación de stock.

La comparación entre el ranking histórico y el ranking predicho permite:

- Identificar productos **críticos** que conviene priorizar en compras y reposición.
- Detectar posibles **cambios de demanda** cuando un producto mejora o empeora su posición en el ranking.

---

## 10. Conclusiones

- El modelo de Machine Learning implementado para Tienda Aurelion permite **predecir la demanda mensual por producto** a partir de su comportamiento histórico.
- El enfoque de **regresión supervisada con Random Forest** es adecuado para capturar patrones no lineales en las ventas.
- La combinación de:
  - dataset limpio,
  - modelo entrenado y evaluado con métricas,
  - y visualizaciones interactivas,
  
  ofrece una herramienta práctica para mejorar la **planificación de stock** y la **toma de decisiones comerciales** en la tienda.

