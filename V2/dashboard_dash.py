"""
Dashboard Corporativo Aurelion 🧩
Visualización interactiva con Plotly Dash.
"""

import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import os

# --- FUNCIONES ---
def cargar_dataset(path_file: str) -> pd.DataFrame:
    """
    Carga un dataset desde CSV con manejo de errores y limpieza básica.
    Devuelve un DataFrame limpio y listo para usar en el dashboard.
    """

    try:
        if not os.path.exists(path_file):
            print(f"❌ Archivo no encontrado: {path_file}")
            return pd.DataFrame()

        df = pd.read_csv(path_file)
        print(f"📂 Archivo cargado correctamente: {path_file}")

        # Normalizar nombres de columnas
        df.columns = [col.strip().lower() for col in df.columns]

        # Asegurar existencia de columnas numéricas
        if 'cantidad' in df.columns:
            df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
        else:
            df['cantidad'] = 0

        if 'precio_unitario' in df.columns:
            df['precio_unitario'] = pd.to_numeric(df['precio_unitario'], errors='coerce').fillna(0)
        else:
            df['precio_unitario'] = 0

        # Calcular importe si no existe
        if 'importe' not in df.columns:
            df['importe'] = df['cantidad'] * df['precio_unitario']

        # Mostrar preview informativo
        print(f"✅ {len(df)} registros cargados. Columnas: {list(df.columns)}")
        print(df.head(3).to_string(index=False))

        return df

    except Exception as e:
        print(f"⚠️ Error al cargar los datos desde {path_file}: {e}")
        return pd.DataFrame()

# --- CARGA DE DATOS ---
for f in ["ranking_historico.csv", "top_predichos.csv"]:
    if not os.path.exists(f):
        raise FileNotFoundError(f"❌ Falta {f}. Ejecutá primero 'proyecto_aurelion.py'.")

ranking = cargar_dataset("ranking_historico.csv")
pred = cargar_dataset("top_predichos.csv")

# --- DASHBOARD ---
app = dash.Dash(__name__)
app.title = "Aurelion Dashboard"

fig_top = px.bar(ranking.head(10), x="nombre_producto", y="cantidad",
                 title="🏆 Top 10 Productos Históricos",
                 color_discrete_sequence=["#1f77b4"])

fig_pred = px.bar(pred.head(10), x="producto", y="frecuencia",
                  title="🤖 Predicciones IA (Top 10)",
                  color_discrete_sequence=["#7f7f7f"])

layout = html.Div([
    html.H1("📊 Dashboard Aurelion", style={"textAlign": "center"}),
    dcc.Graph(figure=fig_top),
    dcc.Graph(figure=fig_pred)
])

app.layout = layout

if __name__ == "__main__":
   app.run(debug=True)

