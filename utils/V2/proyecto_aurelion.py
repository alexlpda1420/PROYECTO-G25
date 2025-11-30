"""
Proyecto Aurelion 🛒
Pipeline de Análisis Predictivo para Ventas Minoristas
Autor: Alexis Roldan
Descripción: Este script integra los datos, limpia inconsistencias,
entrena un modelo de predicción y genera artefactos para el dashboard.
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import os

# --- CONFIGURACIÓN ---
DATA_DIR = "./base de datos"
MODEL_PATH = "modelo_ventas.pkl"
OUTPUT_TOP = "top_predichos.csv"
TOP_N = 10

# --- FUNCIÓN: CARGA DE DATOS ---
def load_data():
    try:
        clientes = pd.read_excel(f"{DATA_DIR}/clientes.xlsx")
        productos = pd.read_excel(f"{DATA_DIR}/productos.xlsx")
        ventas = pd.read_excel(f"{DATA_DIR}/ventas.xlsx")
        detalle = pd.read_excel(f"{DATA_DIR}/detalle_ventas.xlsx")
        print("✅ Datos cargados correctamente.")
        return clientes, productos, ventas, detalle
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        raise

# --- FUNCIÓN: PREPROCESAMIENTO Y MERGE ---
def preprocess_and_merge(dfs):
    clientes, productos, ventas, detalle = dfs

    merged = pd.merge(ventas, detalle, on="id_venta", how="inner")
    merged = pd.merge(merged, productos, on="id_producto", how="left")

    # Normalización de columnas
    if 'precio_unitario_x' in merged.columns and 'precio_unitario_y' in merged.columns:
        merged['precio_unitario'] = merged['precio_unitario_x'].fillna(merged['precio_unitario_y'])
        merged.drop(columns=['precio_unitario_x', 'precio_unitario_y'], inplace=True)
    elif 'precio_unitario_x' in merged.columns:
        merged.rename(columns={'precio_unitario_x': 'precio_unitario'}, inplace=True)
    elif 'precio_unitario_y' in merged.columns:
        merged.rename(columns={'precio_unitario_y': 'precio_unitario'}, inplace=True)

    merged['precio_unitario'] = pd.to_numeric(merged['precio_unitario'], errors='coerce').fillna(0)
    merged['cantidad'] = pd.to_numeric(merged['cantidad'], errors='coerce').fillna(0)

    if 'importe' not in merged.columns:
        merged['importe'] = merged['precio_unitario'] * merged['cantidad']
    if 'nombre_producto_x' in merged.columns:
        merged['nombre_producto'] = merged['nombre_producto_x']
    elif 'nombre_producto_y' in merged.columns:
        merged['nombre_producto'] = merged['nombre_producto_y']

    print("✅ Merge y limpieza completados.")
    return merged

# --- FUNCIÓN: ANÁLISIS HISTÓRICO ---
def analisis_historico(df):
    ranking = df.groupby(['nombre_producto'], as_index=False).agg({
        'cantidad': 'sum',
        'importe': 'sum'
    }).sort_values(by='cantidad', ascending=False)

    ranking['ranking'] = range(1, len(ranking) + 1)
    return ranking

# --- FUNCIÓN: MODELO PREDICTIVO ---
def modelo_predictivo(df):
    df['precio_unitario'] = pd.to_numeric(df['importe'] / df['cantidad'], errors='coerce').fillna(0)
    X = df[['cantidad', 'precio_unitario']]
    y = df['nombre_producto']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = RandomForestClassifier(random_state=42)
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    predicciones = pd.DataFrame({'producto_predicho': y_pred})
    top_predichos = predicciones['producto_predicho'].value_counts().head(TOP_N).reset_index()
    top_predichos.columns = ['producto', 'frecuencia']

    return modelo, top_predichos

# --- PIPELINE PRINCIPAL ---
def pipeline():
    dfs = load_data()
    merged = preprocess_and_merge(dfs)
    ranking_historico = analisis_historico(merged)
    modelo, ranking_predicho = modelo_predictivo(ranking_historico)

    joblib.dump(modelo, MODEL_PATH)
    ranking_historico.head(TOP_N).to_csv("ranking_historico.csv", index=False)
    ranking_predicho.head(TOP_N).to_csv(OUTPUT_TOP, index=False)

    print("\n📊 Artefactos generados correctamente:")
    print(f"✅ Modelo: {MODEL_PATH}")
    print(f"✅ Ranking histórico: ranking_historico.csv")
    print(f"✅ Predicciones: {OUTPUT_TOP}")

if __name__ == "__main__":
    pipeline()
