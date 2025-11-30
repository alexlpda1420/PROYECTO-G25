# 🛒 Aurelion - Sistema Inteligente de Análisis de Ventas

Este proyecto presenta una solución híbrida de análisis de datos para **Aurelion**, un supermercado minorista. El sistema integra un **dashboard interactivo** y un **modelo predictivo de productos más vendidos**.

Desarrollado en **Python** utilizando **Streamlit**, **Pandas**, **Scikit-learn** y visualizaciones con **Matplotlib**.

---

## 🚀 Funcionalidades principales

- 📊 Visualización de ventas totales, productos más vendidos y clientes activos
- 🔍 Filtros dinámicos por fecha y categoría
- 🔮 Modelo predictivo de productos con mayor probabilidad de alta demanda
- 🧠 Entrenamiento automático con Random Forest
- 💾 Descarga de resultados en Excel desde el dashboard

---

## 📁 Estructura del proyecto

# 🛒 Aurelion - Sistema Inteligente de Análisis de Ventas

Este proyecto presenta una solución híbrida de análisis de datos para **Aurelion**, un supermercado minorista. El sistema integra un **dashboard interactivo** y un **modelo predictivo de productos más vendidos**.

Desarrollado en **Python** utilizando **Streamlit**, **Pandas**, **Scikit-learn** y visualizaciones con **Matplotlib**.

---

## 🚀 Funcionalidades principales

- 📊 Visualización de ventas totales, productos más vendidos y clientes activos
- 🔍 Filtros dinámicos por fecha y categoría
- 🔮 Modelo predictivo de productos con mayor probabilidad de alta demanda
- 🧠 Entrenamiento automático con Random Forest
- 💾 Descarga de resultados en Excel desde el dashboard

---

## 📁 Estructura del proyecto

# 🛒 Aurelion - Sistema Inteligente de Análisis de Ventas

Este proyecto presenta una solución híbrida de análisis de datos para **Aurelion**, un supermercado minorista. El sistema integra un **dashboard interactivo** y un **modelo predictivo de productos más vendidos**.

Desarrollado en **Python** utilizando **Streamlit**, **Pandas**, **Scikit-learn** y visualizaciones con **Matplotlib**.

---

## 🚀 Funcionalidades principales

- 📊 Visualización de ventas totales, productos más vendidos y clientes activos
- 🔍 Filtros dinámicos por fecha y categoría
- 🔮 Modelo predictivo de productos con mayor probabilidad de alta demanda
- 🧠 Entrenamiento automático con Random Forest
- 💾 Descarga de resultados en Excel desde el dashboard

---

## 📁 Estructura del proyecto
```yaml

Proyecto/
│
├── app.py # Aplicación principal de Streamlit
├── requirements.txt # Librerías necesarias
├── README.md # Instrucciones y documentación
│
├── clientes.xlsx # Dataset de clientes
├── productos.xlsx # Dataset de productos
├── ventas.xlsx # Dataset de ventas
├── detalle_ventas.xlsx # Dataset con el detalle de ventas

```

---

## ⚙️ Instalación

### 1. Cloná el repositorio (o descargalo)
```bash
git clone https://github.com/tuusuario/aurelion-ventas.git
cd aurelion-ventas

```

### 2. (Opcional) Crear entorno virtual
```bash
python -m venv .venv
.venv\Scripts\activate      # En Windows
source .venv/bin/activate  # En Linux/macOS
```

### 3. Instalá las dependencias
```bash

pip install -r requirements.txt

```

## ▶️ Ejecución del sistema

Una vez dentro del proyecto, ejecutá:

```bash
streamlit run app.py

```
Abrirá una pestaña en tu navegador con el dashboard interactivo. Desde allí podrás subir tus propios archivos .xlsx o usar los que vienen por defecto.

## 🧠 Modelo de predicción

El modelo predictivo se entrena automáticamente en base al historial de ventas y precio promedio, usando un algoritmo Random Forest. Clasifica qué productos tienen más chances de ser Top 10 más vendidos en el siguiente período.

## 📦 Requisitos

- Python 3.9 o superior
- Navegador web moderno
- Archivos `.xlsx` con los siguientes nombres:
  - `clientes.xlsx`
  - `productos.xlsx`
  - `ventas.xlsx`
  - `detalle_ventas.xlsx`
