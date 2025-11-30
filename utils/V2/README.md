# 📊 Proyecto Dashboard de Ventas – Python + Dash + Power BI

Bienvenido al **Proyecto de Dashboard de Ventas G25**, una solución analítica completa para visualizar y explorar datos de clientes, productos y ventas 💼.  
Este proyecto combina **Python + Dash** para un dashboard web interactivo y **Power BI** para análisis avanzados y KPIs ejecutivos.  

---

## 🚀 Objetivos del Proyecto

✅ Integrar múltiples fuentes de datos (`ventas`, `productos`, `detalle_ventas`, `clientes`).  
✅ Calcular KPIs de negocio (ingresos, volumen de ventas, clientes activos, etc.).  
✅ Generar visualizaciones interactivas con **Plotly Dash**.  
✅ Crear un **dashboard Power BI** para reportes ejecutivos.  

---

## 🧠 Estructura del Proyecto

```yaml
📁 Proyecto_G25/
├── 📂 data/
│ ├── clientes.xlsx
│ ├── productos.xlsx
│ ├── ventas.xlsx
│ └── detalle_ventas.xlsx
├── 📄 dashboard_dash.py
├── 📄 dashboard_powerbi.pbix
├── 📄 README.md
├── 📄 README_short.md
└── 📄 requirements.txt
```

---

## ⚙️ Requisitos Previos

Antes de ejecutar el proyecto, asegurate de tener instalado:

- 🐍 **Python 3.10+**
- 📦 Librerías necesarias:

```bash
  pip install -r requirements.txt

``` 
- 📊 Power BI Desktop (para abrir el archivo .pbix)

---

## 🧩 Archivos de Datos

Los archivos deben ubicarse en la carpeta data/ con la siguiente estructura de columnas:

🧾 clientes.xlsx
| id_cliente | nombre_cliente | email | ciudad | fecha_alta |
| ---------- | -------------- | ----- | ------ | ---------- |

💰 productos.xlsx
| id_producto | nombre_producto | categoria | precio_unitario |
| ----------- | --------------- | --------- | --------------- |

🧩 detalle_ventas.xlsx
| id_venta | id_producto | nombre_producto | cantidad | precio_unitario | importe |
| -------- | ----------- | --------------- | -------- | --------------- | ------- |

🧾 ventas.xlsx
| id_venta | fecha | id_cliente | nombre_cliente | email | medio_pago |
| -------- | ----- | ---------- | -------------- | ----- | ---------- |

---

## 🧮 Cálculos Principales

El sistema genera automáticamente métricas clave:
| KPI                        | Descripción                          |
| -------------------------- | ------------------------------------ |
| 💵 **Ingresos totales**    | Suma de `cantidad × precio_unitario` |
| 📈 **Promedio por venta**  | `importe_total / cantidad_ventas`    |
| 👥 **Clientes activos**    | Conteo único de `id_cliente`         |
| 🛒 **Ventas por producto** | Agrupado por `nombre_producto`       |
| 🌎 **Ventas por ciudad**   | Relación con el cliente              |

---

## 🧠 Flujo de Ejecución

```yaml
📥 Carga de datos desde los archivos Excel (pandas.read_excel).

🔗 Unión de tablas mediante claves (id_cliente, id_venta, id_producto).

🧮 Cálculo de métricas y KPIs globales.

📊 Visualización interactiva con Dash + Plotly.

📈 Análisis avanzado con Power BI (dashboard_powerbi.pbix).

```
---

## 🖥️ Ejecución del Dashboard en Python

```yaml
🪄 1. Activar entorno

    ```bash

        python -m venv venv
        source venv/Scripts/activate   # En Windows

    ```
📦 2. Instalar dependencias

   ```bash
    
        pip install -r requirements.txt

    ```
▶️ 3. Ejecutar el dashboard

   ```bash
    
       python dashboard_dash.py

    ```

Luego abrí tu navegador en:
👉 http://127.0.0.1:8050/

```
---

## 📊 Visualizaciones Incluidas (Python Dash)

| Gráfico                   | Descripción                                  |
| ------------------------- | -------------------------------------------- |
| 📅 **Ventas por mes**     | Evolución temporal de ingresos               |
| 🏙️ **Ventas por ciudad** | Distribución geográfica                      |
| 💸 **Top 10 productos**   | Ranking de productos más vendidos            |
| 👥 **Clientes activos**   | Dinámica de crecimiento                      |
| 🧾 **Resumen de KPIs**    | Ingresos, volumen, clientes, ticket promedio |

---

## 🧠 Power BI Dashboard

El archivo dashboard_powerbi.pbix incluye:


```yaml
* KPI Cards (Ingresos, Ticket promedio, Ventas totales)

* Gráficos dinámicos (por categoría, ciudad, medio de pago)

* Segmentadores para filtrar por fechas y categorías

* Vista ejecutiva (para reportes directivos)

```
---

## 🧰 Troubleshooting

```vbnet
KeyError: "❌ Faltan columnas 'precio_unitario' o 'cantidad' en los datos."
```
👉 Revisa que los archivos tengan las columnas correctas, sin tildes ni espacios extra.
También asegurate de que todos estén en la carpeta data/.

---

## 📈 Ejemplo de Slide de KPIs

🎯 Dashboard Comercial – Resumen Ejecutivo

| KPI                 | Valor      | Variación |
| ------------------- | ---------- | --------- |
| 💵 Ingresos Totales | $2.540.000 | ▲ +12%    |
| 🛒 Ventas Totales   | 1.246      | ▲ +8%     |
| 👥 Clientes Activos | 324        | ▲ +6%     |
| 🎯 Ticket Promedio  | $2.038     | ▼ -3%     |

📊 Gráficos:

```yaml
- Línea de ventas mensuales (evolución)

- Barra de productos más vendidos
```