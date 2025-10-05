import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Dashboard Inteligente Aurelion", layout="wide")

# 📥 Carga flexible desde Excel
def cargar_archivo(nombre_archivo_default, key):
    archivo = st.sidebar.file_uploader(f"Subí el archivo: {nombre_archivo_default}", type=["xlsx"], key=key)
    if archivo:
        return pd.read_excel(archivo)
    else:
        return pd.read_excel(nombre_archivo_default)

# 📂 Cargar los datasets
clientes = cargar_archivo("clientes.xlsx", "clientes")
productos = cargar_archivo("productos.xlsx", "productos")
ventas = cargar_archivo("ventas.xlsx", "ventas")
detalle = cargar_archivo("detalle_ventas.xlsx", "detalle")

# 🧩 Preparar y unir los datasets
ventas["fecha"] = pd.to_datetime(ventas["fecha"])
detalle = detalle.merge(productos[["id_producto", "categoria"]], on="id_producto", how="left")
dataset = ventas.merge(detalle, on="id_venta", how="inner")

# 🎛️ Filtros laterales
st.sidebar.markdown("### Filtros")

min_fecha = dataset["fecha"].min()
max_fecha = dataset["fecha"].max()

fecha_inicio = st.sidebar.date_input("Desde", min_fecha, min_value=min_fecha, max_value=max_fecha)
fecha_fin = st.sidebar.date_input("Hasta", max_fecha, min_value=min_fecha, max_value=max_fecha)

categorias = productos["categoria"].unique().tolist()
categoria_seleccionada = st.sidebar.multiselect("Filtrar por categoría", categorias, default=categorias)

# 🔍 Aplicar filtros
dataset_filtrado = dataset[
    (dataset["fecha"] >= pd.to_datetime(fecha_inicio)) &
    (dataset["fecha"] <= pd.to_datetime(fecha_fin)) &
    (dataset["categoria"].isin(categoria_seleccionada))
]

# 📊 KPIs
ventas_totales = dataset_filtrado["importe"].sum()
clientes_unicos = dataset_filtrado["id_cliente"].nunique()
productos_unicos = dataset_filtrado["id_producto"].nunique()

# 🧾 Título y métricas
st.title("📊 Dashboard Inteligente - Aurelion")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Ventas Totales", f"${ventas_totales:,.2f}")
col2.metric("👥 Clientes únicos", clientes_unicos)
col3.metric("📦 Productos vendidos", productos_unicos)

st.markdown("---")

# 📈 Análisis por producto
ventas_por_producto = (
    dataset_filtrado.groupby(["id_producto", "nombre_producto"])
    .agg(
        cantidad_total_vendida=("cantidad", "sum"),
        precio_unitario=("precio_unitario", "mean"),
        subtotal_total=("importe", "sum")
    )
    .reset_index()
)

# 🔮 Modelo predictivo de productos más vendidos
ventas_por_producto["es_top_10"] = ventas_por_producto["cantidad_total_vendida"].rank(ascending=False) <= 10
ventas_por_producto["es_top_10"] = ventas_por_producto["es_top_10"].astype(int)

X = ventas_por_producto[["cantidad_total_vendida", "precio_unitario"]]
y = ventas_por_producto["es_top_10"]

# Solo entrenar si hay suficientes datos
if len(ventas_por_producto) >= 10:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    # Generar predicciones
    ventas_por_producto["prob_top"] = modelo.predict_proba(X)[:, 1]
    top_predichos = ventas_por_producto.sort_values("prob_top", ascending=False).head(5)

    # 📊 Gráfico: Top 10 productos históricos
    st.subheader("🏆 Top 10 productos más vendidos (histórico)")
    top10 = ventas_por_producto.sort_values("cantidad_total_vendida", ascending=False).head(10)
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(top10["nombre_producto"], top10["cantidad_total_vendida"], color="skyblue")
    ax1.set_xticklabels(top10["nombre_producto"], rotation=45, ha="right")
    ax1.set_ylabel("Cantidad vendida")
    st.pyplot(fig1)

    # 🔮 Predicción futura
    st.subheader("🔮 Top 5 productos más vendidos (predicción)")
    st.dataframe(top_predichos[["id_producto", "nombre_producto", "cantidad_total_vendida", "prob_top"]])

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.bar(top_predichos["nombre_producto"], top_predichos["prob_top"], color="lightgreen")
    ax2.set_xticklabels(top_predichos["nombre_producto"], rotation=45, ha="right")
    ax2.set_ylabel("Probabilidad de ser top")
    st.pyplot(fig2)

    # 💾 Botón para descargar predicciones
    buffer = io.BytesIO()
    top_predichos.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="⬇️ Descargar predicciones en Excel",
        data=buffer,
        file_name="predicciones_top_productos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("⚠️ No hay suficientes productos filtrados para entrenar el modelo.")
