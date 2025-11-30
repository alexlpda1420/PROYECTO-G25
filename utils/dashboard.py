import streamlit as st
import pandas as pd
import plotly.express as px
import os


st.set_page_config(page_title="Dashboard Aurelion", layout="wide")

st.title("📊 Dashboard de Ventas — Proyecto Aurelion")

# --- Cargar datasets ---
def load_csv_safe(path, demo_data=None):
    if os.path.exists(path):
        st.success(f"✅ Datos cargados desde {path}")
        return pd.read_csv(path)
    else:
        st.warning(f"⚠ No se encontró {path}. Cargando datos de ejemplo.")
        return demo_data

# Datos de ejemplo (en caso de no haber ejecutado el pipeline)
demo_hist = pd.DataFrame({
    "id_producto": [1, 2, 3],
    "nombre_producto": ["Notebook", "Mouse", "Teclado"],
    "historical_quantity": [120, 90, 80]
})
demo_pred = pd.DataFrame({
    "id_producto": [1, 2, 3],
    "nombre_producto": ["Notebook", "Mouse", "Teclado"],
    "predicted_quantity": [130, 85, 70]
})

ranking_historico = load_csv_safe("ranking_historico.csv", demo_hist)
ranking_predicho = load_csv_safe("top_predichos.csv", demo_pred)

# --- Gráficos Plotly con tema corporativo ---
theme_colors = {"color_discrete_sequence": ["#004080", "#7f8c8d", "#3498db", "#95a5a6"]}

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top Productos Históricos (último mes)")
    fig_hist = px.bar(
        ranking_historico.head(10),
        x="nombre_producto",
        y="historical_quantity",
        text="historical_quantity",
        **theme_colors
    )
    fig_hist.update_traces(textposition='outside')
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader("🔮 Predicciones Próximo Mes")
    fig_pred = px.bar(
        ranking_predicho.head(10),
        x="nombre_producto",
        y="predicted_quantity",
        text="predicted_quantity",
        **theme_colors
    )
    fig_pred.update_traces(textposition='outside')
    st.plotly_chart(fig_pred, use_container_width=True)

# --- Comparativa automática ---
st.markdown("### 📈 Comparativa y recomendaciones automáticas")

merged = pd.merge(
    ranking_historico, ranking_predicho,
    on=["id_producto", "nombre_producto"],
    how="outer"
).fillna(0)

merged["variacion"] = merged["predicted_quantity"] - merged["historical_quantity"]

def generate_recommendation(row):
    if row["variacion"] < -10:
        return "⚠ Decrece — revisar estrategia"
    elif row["variacion"] > 10:
        return "🚀 En crecimiento — mantener impulso"
    else:
        return "ℹ Estable"

merged["recomendacion"] = merged.apply(generate_recommendation, axis=1)
st.dataframe(merged, use_container_width=True)

# --- Exportar ---
if st.button("📎 Exportar resumen a PDF"):
    st.info("💾 Función de exportación a PDF próximamente disponible.")

