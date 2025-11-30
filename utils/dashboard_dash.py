# ======================================
# 📊 DASHBOARD DE VENTAS - PROYECTO G25
# ======================================
# Autor: Alexis Roldan
# Descripción: Dashboard interactivo con KPIs, gráficos Plotly y alertas automáticas.
# ======================================

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# =============================
# 📂 CARGA DE DATOS
# =============================

# Archivos de entrada (ajustá si cambian los nombres)
PATH_VENTAS = "./base de datos/ventas.xlsx"
PATH_DETALLE = "./base de datos/detalle_ventas.xlsx"
PATH_PRODUCTOS = "./base de datos/productos.xlsx"
PATH_CLIENTES = "./base de datos/clientes.xlsx"

try:
    ventas = pd.read_excel(PATH_VENTAS)
    detalle = pd.read_excel(PATH_DETALLE)
    productos = pd.read_excel(PATH_PRODUCTOS)
    clientes = pd.read_excel(PATH_CLIENTES)
except Exception as e:
    raise FileNotFoundError(f"❌ Error al cargar los datos: {e}")

# =============================
# 🧮 PREPROCESAMIENTO
# =============================

# Unir tablas
df = detalle.merge(ventas, on="id_venta", how="left")
df = df.merge(productos, on="id_producto", how="left")
df = df.merge(clientes, on="id_cliente", how="left")

# Crear columna total
if "precio_unitario" in df.columns and "cantidad" in df.columns:
    df["total"] = df["precio_unitario"] * df["cantidad"]
else:
    raise KeyError("❌ Faltan columnas 'precio_unitario' o 'cantidad' en los datos.")

# Convertir fechas
if "fecha_venta" in df.columns:
    df["fecha_venta"] = pd.to_datetime(df["fecha_venta"])
else:
    raise KeyError("❌ Falta la columna 'fecha_venta' en los datos.")

# =============================
# 📈 KPI CARDS
# =============================

total_ventas = df["total"].sum()
clientes_unicos = df["id_cliente"].nunique()
productos_vendidos = df["id_producto"].nunique()

kpi_cards = dbc.Row([
    dbc.Col(html.Div([
        html.H6("🏅 Ventas Totales", className="text-muted"),
        html.H3(f"${total_ventas:,.2f}", className="text-light"),
    ]), md=4),
    dbc.Col(html.Div([
        html.H6("🎮 Clientes únicos", className="text-muted"),
        html.H3(f"{clientes_unicos}", className="text-light"),
    ]), md=4),
    dbc.Col(html.Div([
        html.H6("📦 Productos vendidos", className="text-muted"),
        html.H3(f"{productos_vendidos}", className="text-light"),
    ]), md=4),
], className="text-center mb-4")

# =============================
# 🎨 GRAFICOS PLOTLY
# =============================

# --- Top 10 productos ---
ventas_por_producto = (
    df.groupby("nombre_producto")
    .agg({"total": "sum"})
    .sort_values("total", ascending=False)
    .head(10)
    .reset_index()
)

fig_top_productos = px.bar(
    ventas_por_producto,
    x="total",
    y="nombre_producto",
    orientation="h",
    title="🏆 Top 10 Productos más vendidos (por monto total)",
    labels={"total": "Monto total ($)", "nombre_producto": "Producto"},
    color="total",
    color_continuous_scale=["#3a7bd5", "#00d2ff"]
)
fig_top_productos.update_layout(
    template="plotly_dark",
    xaxis_title="Monto total ($)",
    yaxis_title="Producto",
    yaxis=dict(autorange="reversed"),
    margin=dict(l=80, r=20, t=60, b=60)
)

# --- Evolución mensual de ventas ---
df["fecha"] = pd.to_datetime(df["fecha_venta"])
ventas_mensuales = (
    df.groupby(df["fecha"].dt.to_period("M"))
    .agg({"total": "sum"})
    .reset_index()
)
ventas_mensuales["fecha"] = ventas_mensuales["fecha"].dt.to_timestamp()

fig_evolucion = px.line(
    ventas_mensuales,
    x="fecha",
    y="total",
    markers=True,
    title="📈 Evolución Mensual de Ventas",
    labels={"fecha": "Mes", "total": "Monto Total ($)"},
    line_shape="spline",
)
fig_evolucion.update_traces(line_color="#3a7bd5", fill="tozeroy", fillcolor="rgba(58,123,213,0.2)")
fig_evolucion.update_layout(template="plotly_dark", margin=dict(l=40, r=40, t=60, b=40))

# =============================
# ⚠ RECOMENDACIONES AUTOMÁTICAS
# =============================

ventas_mensuales_prod = (
    df.groupby([df["fecha"].dt.to_period("M"), "nombre_producto"])
    .agg({"total": "sum"})
    .reset_index()
)
ventas_mensuales_prod["fecha"] = ventas_mensuales_prod["fecha"].dt.to_timestamp()

ultimos = ventas_mensuales_prod["fecha"].sort_values().unique()[-3:]
caidas = []
for prod in ventas_mensuales_prod["nombre_producto"].unique():
    subset = ventas_mensuales_prod[ventas_mensuales_prod["nombre_producto"] == prod]
    subset = subset[subset["fecha"].isin(ultimos)]
    if len(subset) >= 2:
        diff = (subset["total"].iloc[-1] - subset["total"].iloc[-2]) / subset["total"].iloc[-2]
        if diff < -0.2:
            caidas.append(prod)

mensaje = "✅ Todo estable en las ventas recientes." if not caidas else \
    "⚠ Los siguientes productos muestran caída de ventas: " + ", ".join(caidas)

# =============================
# 🧱 LAYOUT DEL DASHBOARD
# =============================

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Dashboard de Ventas - G25"

app.layout = html.Div([
    html.H1("📊 Dashboard de Ventas", className="text-center text-light mt-3"),
    kpi_cards,
    html.Hr(),
    dbc.Container([
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_top_productos), md=6),
            dbc.Col(dcc.Graph(figure=fig_evolucion), md=6),
        ], className="g-4"),
        html.Hr(className="my-4"),
        html.H3("🔮 Predicciones del modelo", className="text-center text-light"),
        dcc.Graph(id="grafico_predicciones"),  # Placeholder para futuro ML
        html.Div(
            html.P(mensaje, className="text-center text-warning mt-3 fw-bold"),
        ),
    ], fluid=True)
])

# =============================
# ▶️ EJECUCIÓN LOCAL
# =============================
if __name__ == "__main__":
    app.run_server(debug=True, port=8501)
