"""
Versión Streamlit del Dashboard Aurelion 🖥️
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Aurelion Dashboard", page_icon="🛒", layout="wide")

ranking = pd.read_csv("ranking_historico.csv")
pred = pd.read_csv("top_predichos.csv")

st.title("📊 Dashboard de Ventas - Aurelion")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🏆 Top 10 Productos Históricos")
    fig1 = px.bar(ranking.head(10), x="nombre_producto", y="cantidad", color_discrete_sequence=["#007bff"])
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.subheader("🤖 Predicciones IA")
    fig2 = px.bar(pred.head(10), x="producto", y="frecuencia", color_discrete_sequence=["#888888"])
    st.plotly_chart(fig2, use_container_width=True)
