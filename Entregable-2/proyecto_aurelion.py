"""
proyecto_aurelion.py
Script académico para:
- carga y limpieza de archivos Excel (clientes, productos, ventas, detalle_ventas)
- construcción de dataset agregado mensual por producto
- entrenamiento de modelo basado en frecuencia histórica (RandomForest)
- predicción de productos más vendidos (Top N)
- mini-dashboard con Streamlit (opcional)

Instrucciones:
- Colocar los archivos en ./Base de datos/ con los nombres:
    clientes.xlsx, productos.xlsx, ventas.xlsx, detalle_ventas.xlsx
- Requisitos:
    
    
- Ejecutar (CLI): python proyecto_aurelion.py
- Ejecutar (Dashboard): streamlit run proyecto_aurelion.py
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

# Optional visualization libs for dashboard
try:
    import streamlit as st
    import altair as alt
    STREAMLIT_AVAILABLE = True
except Exception:
    STREAMLIT_AVAILABLE = False

# Config
BASE_DIR = Path.cwd() / "Base de datos"
FILES = {
    "clientes": "clientes.xlsx",
    "productos": "productos.xlsx",
    "ventas": "ventas.xlsx",
    "detalle": "detalle_ventas.xlsx"
}
RANDOM_STATE = 42
MODEL_PATH = Path("model_random_forest.joblib")
TOP_N = 10  # número de productos top que queremos obtener en la predicción
PAST_MONTHS_FEATURES = 3  # cuántos meses anteriores usamos como features


# ---------------------------
# Utilities: lectura y chequeos
# ---------------------------
def read_excel_safe(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    return pd.read_excel(path)


def load_datasets(base_dir=BASE_DIR):
    """Carga los 4 archivos Excel y retorna un dict de DataFrames."""
    dfs = {}
    for key, fname in FILES.items():
        path = base_dir / fname
        dfs[key] = read_excel_safe(path)
        print(f"Loaded {fname}: {dfs[key].shape[0]} rows, {dfs[key].shape[1]} cols")
    return dfs


def standardize_columns(dfs):
    """Normaliza nombres de columnas para robustez."""
    # Map de columnas esperadas a nombres reales
    # (según lo que especificaste)
    # clientes: id_cliente, nombre_cliente, email, ciudad, fecha_alta
    # productos: id_producto, nombre_producto, categoria, precio_unitario
    # ventas: id_venta, fecha, id_cliente, nombre_cliente, email, medio_pago
    # detalle: id_venta, id_producto, nombre_producto, cantidad, precio_unitario, importe

    # Convertir a minúsculas y quitar espacios
    for k, df in dfs.items():
        df.columns = [c.strip() for c in df.columns]
    return dfs


# ---------------------------
# Preprocesamiento y merge
# ---------------------------
def preprocess_and_merge(dfs):
    """Normaliza y fusiona los DataFrames en un dataset unificado."""
    ventas = dfs["ventas"]
    detalle = dfs["detalle"]
    clientes = dfs.get("clientes", pd.DataFrame())
    productos = dfs.get("productos", pd.DataFrame())

    # 1. Renombrar columnas antes del merge para evitar duplicados
    if "precio_unitario" in detalle.columns:
        detalle.rename(columns={"precio_unitario": "precio_unitario_detalle"}, inplace=True)

    if "precio_unitario" in productos.columns:
        productos.rename(columns={"precio_unitario": "precio_unitario_producto"}, inplace=True)

    # 2. Merge secuencial controlado
    merged = pd.merge(ventas, detalle, on="id_venta", how="left")
    merged = pd.merge(merged, productos, on="id_producto", how="left")

    # 3. Unificar precio
    merged["precio_unitario"] = merged["precio_unitario_detalle"].fillna(merged["precio_unitario_producto"])

    # 4. Eliminar columnas auxiliares
    merged.drop(columns=["precio_unitario_detalle", "precio_unitario_producto"], inplace=True, errors="ignore")

    return merged



# ---------------------------
# Construcción serie mensual por producto
# ---------------------------
def build_monthly_table(merged_df):
    """Construye tabla mensual (product_id x period) con suma de cantidades vendidas."""
    df = merged_df.copy()
    df['period'] = df['fecha'].dt.to_period('M').dt.to_timestamp()
    monthly = df.groupby(['id_producto', 'period']).agg({
        'cantidad': 'sum'
    }).reset_index()
    # Asegurar que no haya periodos faltantes por producto (rellenar con 0)
    pivot = monthly.pivot_table(index='id_producto', columns='period', values='cantidad', fill_value=0)
    pivot = pivot.sort_index(axis=1)  # columnas cronológicas
    return pivot


# ---------------------------
# Crear dataset supervisado (lags) para predecir siguiente mes
# ---------------------------
def create_supervised_dataset(pivot_table, n_lags=PAST_MONTHS_FEATURES):
    """
    Para cada producto, usa los últimos n_lags meses como features
    y el mes siguiente como target (cantidad).
    Retorna X (features), y (target) y la fecha objetivo (next_period)
    """
    # Ordenar columnas (periods) por fecha
    cols = list(pivot_table.columns)
    cols_sorted = sorted(cols)
    pivot_table = pivot_table[cols_sorted]

    # Verificar que haya meses suficientes
    if len(cols_sorted) < n_lags + 1:
        raise ValueError(f"No hay meses suficientes (necesarios {n_lags+1}, hay {len(cols_sorted)})")

    # Selección de features y target
    feature_cols = cols_sorted[-(n_lags + 1):-1]
    target_col = cols_sorted[-1]

    # Construcción de dataset supervisado
    X = pivot_table[feature_cols].reset_index()
    y = pivot_table[[target_col]].reset_index()

    data = pd.merge(X, y, on='id_producto', suffixes=('_feat', '_target'))

    # Asignación de índices correctamente
    X_final = data[[c for c in data.columns if c not in ['id_producto', target_col]]].copy()
    X_final.index = data['id_producto']
    y_final = pd.Series(data[target_col].values, index=data['id_producto'], name=target_col)

    return X_final, y_final, feature_cols, target_col



# ---------------------------
# Entrenamiento y predicción
# ---------------------------
def train_and_predict(X, y):
    """Entrena RandomForestRegressor y predice la demanda (cantidad) en next period."""
    # Dividir
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)

    model = RandomForestRegressor(n_estimators=200, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)

    # Evaluación
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    print(f"Modelo entrenado. MSE en test: {mse:.3f}")

    # Predecir para todos productos (usamos el X completo para ranking)
    preds_all = model.predict(X)
    preds_series = pd.Series(preds_all, index=X.index, name='predicted_quantity')
    return model, preds_series


# ---------------------------
# Pipeline completo
# ---------------------------
def pipeline():
    print("=== Pipeline Aurelion: carga, preproc, modelado, predicción ===")
    dfs = load_datasets()
    dfs = standardize_columns(dfs)
    merged = preprocess_and_merge(dfs)
    pivot = build_monthly_table(merged)
    print(f"Pivot table creada: {pivot.shape[0]} productos x {pivot.shape[1]} meses")

    # Crear supervisado
    X, y, feat_cols, target_col = create_supervised_dataset(pivot, n_lags=PAST_MONTHS_FEATURES)
    print(f"Dataset supervisado: {X.shape[0]} productos, features: {list(X.columns)} -> target: {target_col}")

    model, preds_series = train_and_predict(X, y)

    # Ranking histórico (último mes real)
    histórico = pivot[target_col].sort_values(ascending=False).rename('historical_quantity')
    ranking_historico = histórico.reset_index().rename(columns={'id_producto': 'id_producto', target_col: 'historical_quantity'})

    # Ranking predicho
    ranking_predicho = preds_series.sort_values(ascending=False).reset_index().rename(columns={'index': 'id_producto', 'predicted_quantity': 'predicted_quantity'})

    # Unir con tabla productos si existe para mostrar nombres
    productos_df = dfs.get('productos')
    if productos_df is not None:
        ranking_predicho = ranking_predicho.merge(productos_df[['id_producto', 'nombre_producto']], on='id_producto', how='left')
        ranking_historico = ranking_historico.merge(productos_df[['id_producto', 'nombre_producto']], on='id_producto', how='left')

    # Guardar modelo
    joblib.dump(model, MODEL_PATH)
    print(f"Modelo guardado en: {MODEL_PATH}")

    # Guardar predicciones top-N en CSV
    ranking_predicho.head(TOP_N).to_csv("top_predichos.csv", index=False)
    print(f"Top {TOP_N} productos predichos guardados en top_predichos.csv")

    # Mostrar resumen en consola
    print("\n=== Top productos históricos (último mes real) ===")
    print(ranking_historico.head(TOP_N).to_string(index=False))
    print("\n=== Top productos predichos (próximo mes) ===")
    print(ranking_predicho.head(TOP_N).to_string(index=False))

    return {
        'merged': merged,
        'pivot': pivot,
        'ranking_historico': ranking_historico,
        'ranking_predicho': ranking_predicho,
        'model': model
    }


# ---------------------------
# Simple Streamlit dashboard (opcional)
# ---------------------------
# ---------------------------
# Simple Streamlit dashboard (completo)
# ---------------------------
def run_streamlit_app(artifacts):
    if not STREAMLIT_AVAILABLE:
        print("Streamlit no está instalado. Instala streamlit para usar el dashboard: pip install streamlit")
        return

    st.title("📊 Aurelion - Dashboard Interactivo de Ventas y Predicción")
    st.markdown("Visualiza las métricas clave, productos más vendidos y predicciones de demanda basadas en el modelo Random Forest.")

    ranking_historico = artifacts['ranking_historico']
    ranking_predicho = artifacts['ranking_predicho']
    merged = artifacts['merged']

    # ---------------------------
    # MÉTRICAS PRINCIPALES (KPIs)
    # ---------------------------
    total_ventas = merged['cantidad'].sum()
    n_productos = merged['id_producto'].nunique()
    n_ventas = merged['id_venta'].nunique()
    n_clientes = merged['id_cliente'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Ventas totales (unidades)", int(total_ventas))
    col2.metric("📦 Productos únicos", int(n_productos))
    col3.metric("🧾 Transacciones (ventas)", int(n_ventas))
    col4.metric("👥 Clientes activos", int(n_clientes))

    # ---------------------------
    # TOP HISTÓRICO Y PREDICHO
    # ---------------------------
    st.subheader("🏆 Top histórico (último mes)")
    st.dataframe(ranking_historico.head(20))

    st.subheader("🔮 Top predicho (próximo mes)")
    st.dataframe(ranking_predicho.head(20))

    # ---------------------------
    # GRÁFICOS COMPARATIVOS
    # ---------------------------
    st.subheader("📈 Comparativa de productos más vendidos")

    hist_top = ranking_historico.head(10).reset_index(drop=True)
    pred_top = ranking_predicho.head(10).reset_index(drop=True)

    chart_h = alt.Chart(hist_top).mark_bar(color='#1f77b4').encode(
        x=alt.X('historical_quantity:Q', title='Unidades vendidas'),
        y=alt.Y('nombre_producto:N', sort='-x', title='Producto'),
        tooltip=['nombre_producto', 'historical_quantity']
    ).properties(title='Top 10 histórico (último mes)')

    chart_p = alt.Chart(pred_top).mark_bar(color='#ff7f0e').encode(
        x=alt.X('predicted_quantity:Q', title='Unidades predichas'),
        y=alt.Y('nombre_producto:N', sort='-x', title='Producto'),
        tooltip=['nombre_producto', 'predicted_quantity']
    ).properties(title='Top 10 predicho (próximo mes)')

    st.altair_chart(chart_h, use_container_width=True)
    st.altair_chart(chart_p, use_container_width=True)

    # ---------------------------
    # CLIENTES MÁS ACTIVOS
    # ---------------------------
    st.subheader("👥 Clientes más activos")
    clientes_top = (
        merged.groupby("nombre_cliente")["cantidad"]
        .sum()
        .reset_index()
        .sort_values(by="cantidad", ascending=False)
        .head(10)
    )
    chart_clientes = alt.Chart(clientes_top).mark_bar(color='#2ca02c').encode(
        x=alt.X('cantidad:Q', title='Unidades compradas'),
        y=alt.Y('nombre_cliente:N', sort='-x', title='Cliente'),
        tooltip=['nombre_cliente', 'cantidad']
    ).properties(title='Top 10 clientes más activos')
    st.altair_chart(chart_clientes, use_container_width=True)

    # ---------------------------
    # COMPARATIVA POR CATEGORÍA
    # ---------------------------
    if "categoria" in merged.columns:
        st.subheader("🧮 Comparativa entre categorías")
        categoria_sum = (
            merged.groupby("categoria")["cantidad"]
            .sum()
            .reset_index()
            .sort_values(by="cantidad", ascending=False)
        )
        chart_cat = alt.Chart(categoria_sum).mark_bar(color='#9467bd').encode(
            x=alt.X('cantidad:Q', title='Unidades vendidas'),
            y=alt.Y('categoria:N', sort='-x', title='Categoría'),
            tooltip=['categoria', 'cantidad']
        ).properties(title='Ventas por categoría')
        st.altair_chart(chart_cat, use_container_width=True)
    else:
        st.info("No se encontró la columna 'categoria' en el dataset de productos.")

    # ---------------------------
    # NOTA FINAL
    # ---------------------------
    st.markdown("---")
    st.markdown("📘 **Dashboard académico - Proyecto Aurelion** | Modelo predictivo basado en frecuencia histórica y análisis de ventas con Python + Streamlit + Altair.")

    


# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Pipeline Aurelion - análisis y predicción de productos más vendidos")
    parser.add_argument("--run-streamlit", action="store_true", help="Ejecutar dashboard Streamlit tras procesar (streamlit debe estar instalado).")
    args = parser.parse_args()

    try:
        artifacts = pipeline()
    except Exception as e:
        print("Error en pipeline:", e)
        raise

    if args.run_streamlit:
        # Si se desea, ejecutar el dashboard (se asume que se ejecuta mediante `streamlit run proyecto_aurelion.py -- --run-streamlit`)
        run_streamlit_app(artifacts)
    else:
        print("\nEjecución completa. Para ver un dashboard interactivo ejecuta:")
        print("    streamlit run proyecto_aurelion.py -- --run-streamlit")
