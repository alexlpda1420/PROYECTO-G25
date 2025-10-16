import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración general
st.set_page_config(page_title="Aurelion IA Retail", page_icon="🧠", layout="wide")

# Cargar datasets
@st.cache_data
def cargar_datos():
    ventas = pd.read_excel("./base_de_datos/ventas.xlsx")
    detalle = pd.read_excel("./base_de_datos/detalle_ventas.xlsx")
    productos = pd.read_excel("./base_de_datos/productos.xlsx")
    clientes = pd.read_excel("./base_de_datos/clientes.xlsx")

    merged = detalle.merge(productos, on="id_producto", how="left")
    merged = merged.merge(ventas, on="id_venta", how="left")
    return merged, ventas, clientes

df, ventas, clientes = cargar_datos()

st.title("🧠 Dashboard de Ventas - Proyecto Aurelion")
st.markdown("### **Análisis histórico y predictivo del comportamiento de ventas.**")

# KPIs principales
col1, col2, col3, col4 = st.columns(4)
col1.metric("🛒 Total Ventas", f"{len(ventas):,}")
col2.metric("💰 Importe Total", f"${df['importe'].sum():,.2f}")
col3.metric("📦 Productos Vendidos", f"{df['cantidad'].sum():,}")
col4.metric("👥 Clientes Activos", f"{len(clientes):,}")

# Top 10 productos
st.subheader("🏆 Top 10 Productos Más Vendidos (Histórico)")
ranking = df.groupby("nombre_producto")["cantidad"].sum().reset_index().sort_values("cantidad", ascending=False).head(10)
fig_top = px.bar(ranking, x="nombre_producto", y="cantidad", color="cantidad",
                 color_continuous_scale="blues", title="Top 10 Productos por Cantidad Vendida")
st.plotly_chart(fig_top, use_container_width=True)

# Evolución mensual
df["mes"] = pd.to_datetime(df["fecha"]).dt.to_period("M").astype(str)
evolucion = df.groupby(["mes", "nombre_producto"])["cantidad"].sum().reset_index()
fig_line = px.line(evolucion, x="mes", y="cantidad", color="nombre_producto", title="📈 Evolución Mensual por Producto")
st.plotly_chart(fig_line, use_container_width=True)

# Recomendación automática
st.subheader("⚠ Recomendaciones Automáticas")
caidas = evolucion.groupby("nombre_producto")["cantidad"].agg(["max", "min"]).reset_index()
caidas["variacion_%"] = ((caidas["min"] - caidas["max"]) / caidas["max"]) * 100
recomendaciones = caidas[caidas["variacion_%"] < -30]

if not recomendaciones.empty:
    for _, row in recomendaciones.iterrows():
        st.warning(f"⚠ {row['nombre_producto']} presenta una caída de {abs(row['variacion_%']):.1f}%. Reforzar stock o campañas.")
else:
    st.success("✅ No se detectaron productos con caídas significativas.")
