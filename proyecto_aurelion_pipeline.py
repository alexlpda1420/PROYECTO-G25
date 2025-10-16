"""
proyecto_aurelion_pipeline.py
Pipeline directo y comentado (estudiante IA, modo exposición)

Funcionalidad:
- Carga los 4 archivos Excel desde ./Base de datos/
- Normaliza y une tablas (evita pérdida de columnas como precio_unitario)
- Construye tabla mensual por producto
- Genera dataset supervisado usando n meses previos como features
- Entrena RandomForestRegressor sobre la frecuencia histórica
- Guarda: modelo (.joblib), top_predichos.csv y dataset_unificado.csv
- Muestra resúmenes por consola

Instrucciones:
- Colocar los Excel en ./Base de datos/:
    clientes.xlsx, productos.xlsx, ventas.xlsx, detalle_ventas.xlsx
- Instalar dependencias:
    pip install pandas numpy scikit-learn joblib
- Ejecutar:
    python proyecto_aurelion_pipeline.py
"""

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import sys

# ---------------------------
# Configuración
# ---------------------------
BASE_DIR = Path.cwd() / "Base de datos"   # carpeta donde están los Excel
FILES = {
    "clientes": "clientes.xlsx",
    "productos": "productos.xlsx",
    "ventas": "ventas.xlsx",
    "detalle": "detalle_ventas.xlsx"
}
RANDOM_STATE = 42
MODEL_PATH = Path("model_random_forest_aurelion.joblib")
TOP_N = 10
PAST_MONTHS_FEATURES = 3
OUTPUT_UNIFIED = Path("dataset_unificado.csv")
OUTPUT_TOP = Path("top_predichos.csv")

# ---------------------------
# Helpers: lectura segura y logging simple
# ---------------------------
def read_excel_safe(path: Path):
    """Lee un Excel o lanza error claro si no existe."""
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    print(f"↳ Leyendo: {path.name}")
    return pd.read_excel(path)


def load_all():
    """Carga los 4 DataFrames desde BASE_DIR y devuelve un dict."""
    dfs = {}
    for key, fname in FILES.items():
        path = BASE_DIR / fname
        dfs[key] = read_excel_safe(path)
    print("✅ Carga inicial completada.\n")
    return dfs

# ---------------------------
# Normalización de columnas
# ---------------------------
def normalize_column_names(dfs):
    """
    Normaliza nombres de columnas: quita espacios al inicio/fin
    y detecta variantes simples (mayúsculas/minúsculas).
    """
    for k, df in dfs.items():
        # Strip y mantener nombres originales en caso de duplicados
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        dfs[k] = df
    print("✅ Normalización de nombres de columnas aplicada.\n")
    return dfs

# ---------------------------
# Merge y unificación de precios
# ---------------------------
def preprocess_and_merge(dfs):
    """
    Explicación (como para defensa):
    - Renombramos columnas de precio en detalle/productos para evitar colisiones
    - Hacemos merges controlados: ventas <- detalle <- productos
    - Unificamos precio_unitario final tomando prioridad del detalle y
      cayendo al precio del catálogo si el detalle no lo trae.
    - Guardamos dataset unificado para inspección.
    """
    ventas = dfs["ventas"].copy()
    detalle = dfs["detalle"].copy()
    productos = dfs["productos"].copy()

    # Mensaje introductorio
    print(">>> Preprocesamiento y merge de tablas (explicación):")
    print(" - Objetivo: tener un dataset unificado por línea de venta con precio y fecha.\n")

    # Asegurar que la columna fecha exista y esté en formato datetime
    # Buscamos una columna que contenga 'fecha'
    fecha_col = None
    for c in ventas.columns:
        if 'fecha' in str(c).lower():
            fecha_col = c
            break
    if fecha_col is None:
        raise KeyError("No se encontró columna de fecha en ventas. Revisa 'ventas.xlsx'.")

    ventas.rename(columns={fecha_col: 'fecha'}, inplace=True)
    ventas['fecha'] = pd.to_datetime(ventas['fecha'], errors='coerce')

    # Renombrar columnas de precio para evitar duplicados en merges
    if 'precio_unitario' in detalle.columns:
        detalle.rename(columns={'precio_unitario': 'precio_unitario_detalle'}, inplace=True)
    else:
        # búsqueda tolerante: si hay columna que contenga 'precio'
        for c in detalle.columns:
            if 'precio' in c.lower():
                detalle.rename(columns={c: 'precio_unitario_detalle'}, inplace=True)
                break

    if 'precio_unitario' in productos.columns:
        productos.rename(columns={'precio_unitario': 'precio_unitario_producto'}, inplace=True)
    else:
        for c in productos.columns:
            if 'precio' in c.lower():
                productos.rename(columns={c: 'precio_unitario_producto'}, inplace=True)
                break

    # Hacemos merge: primero ventas + detalle (por id_venta), luego con productos (por id_producto)
    # Usamos left joins para no perder ventas aunque falte detalle (marcaremos después)
    merged = pd.merge(ventas, detalle, on='id_venta', how='left', validate='1:m')
    merged = pd.merge(merged, productos, on='id_producto', how='left', validate='m:1')

    # Unificar precio: priorizamos el precio del detalle (precio al vender), sino precio del catálogo
    if 'precio_unitario_detalle' in merged.columns or 'precio_unitario_producto' in merged.columns:
        merged['precio_unitario'] = merged.get('precio_unitario_detalle').fillna(merged.get('precio_unitario_producto'))
    else:
        # Si por alguna razón ninguno existe, creamos columna a 0 y mostramos advertencia
        print("⚠️ Atención: no se encontraron columnas de precio detectables. Se crea columna 'precio_unitario' con ceros.")
        merged['precio_unitario'] = 0.0

    # Asegurar tipos numéricos
    merged['cantidad'] = pd.to_numeric(merged.get('cantidad', 0), errors='coerce').fillna(0).astype(int)
    merged['precio_unitario'] = pd.to_numeric(merged['precio_unitario'], errors='coerce').fillna(0.0)

    # Calcular importe si no existe o verificar si existe
    if 'importe' not in merged.columns:
        merged['importe'] = merged['cantidad'] * merged['precio_unitario']
    else:
        # marcar diferencias importantes sin corregir automáticamente
        diffs = merged.loc[merged['importe'].notna(), :]
        diffs_mask = np.abs(diffs['importe'] - (diffs['cantidad'] * diffs['precio_unitario'])) > 1e-2
        n_diffs = diffs_mask.sum()
        if n_diffs > 0:
            print(f"⚠️ Nota: {n_diffs} filas con discrepancia entre 'importe' y cantidad*precio_unitario.")

    # Filtrar filas sin fecha (no sirven para series temporales)
    before = len(merged)
    merged = merged[merged['fecha'].notna()].copy()
    after = len(merged)
    if after < before:
        print(f"ℹ️ Se descartaron {before-after} registros sin fecha válida.")

    # Guardar dataset unificado para que el juez/profesor lo pueda revisar
    merged.to_csv(OUTPUT_UNIFIED, index=False, encoding='utf-8')
    print(f"✅ Dataset unificado guardado en '{OUTPUT_UNIFIED}' ({len(merged)} filas).")

    return merged

# ---------------------------
# Construir tabla mensual por producto
# ---------------------------
def build_monthly_pivot(merged):
    """Construye una tabla producto x periodo (mensual) con suma de cantidades vendidas."""
    print("\n>>> Construyendo tabla mensual por producto (agregados por mes).")
    df = merged.copy()
    # Crear columna period = primer día del mes (timestamp) para pivot ordenable
    df['period'] = df['fecha'].dt.to_period('M').dt.to_timestamp()
    monthly = df.groupby(['id_producto', 'period']).agg({'cantidad': 'sum'}).reset_index()
    pivot = monthly.pivot_table(index='id_producto', columns='period', values='cantidad', fill_value=0)
    pivot = pivot.sort_index(axis=1)
    print(f"✅ Pivot generado: {pivot.shape[0]} productos x {pivot.shape[1]} meses.")
    return pivot

# ---------------------------
# Crear dataset supervisado (lags)
# ---------------------------
def create_supervised(pivot, n_lags=PAST_MONTHS_FEATURES):
    """
    Explicación para defensa:
    - Para cada producto usamos los n_lags meses previos como features (X)
    - El target (y) es la demanda (cantidad) del mes siguiente
    - Esto es un enfoque simple y robusto basado en frecuencia histórica
    """
    print("\n>>> Creando dataset supervisado (lags)...")
    cols = list(pivot.columns)
    cols_sorted = sorted(cols)
    if len(cols_sorted) < n_lags + 1:
        raise ValueError(f"No hay meses suficientes para crear features (se requieren {n_lags + 1}).")

    feature_cols = cols_sorted[-(n_lags + 1):-1]
    target_col = cols_sorted[-1]

    X = pivot[feature_cols].copy()
    y = pivot[target_col].copy()

    # Index: id_producto
    X.index.name = 'id_producto'
    y.index.name = 'id_producto'
    print(f" - Features: {feature_cols}")
    print(f" - Target (último mes real): {target_col}")
    return X, y, feature_cols, target_col

# ---------------------------
# Entrenamiento y predicción
# ---------------------------
def train_and_predict(X, y):
    """Entrena RandomForestRegressor y devuelve predicciones para ranking."""
    print("\n>>> Entrenando modelo RandomForestRegressor...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)

    model = RandomForestRegressor(n_estimators=200, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)

    preds_test = model.predict(X_test)
    mse = mean_squared_error(y_test, preds_test)
    print(f"✅ Modelo entrenado. MSE en test: {mse:.3f}")

    # Predicción para todos los productos (para ranking global)
    preds_all = model.predict(X)
    preds_series = pd.Series(preds_all, index=X.index, name='predicted_quantity')
    return model, preds_series

# ---------------------------
# Pipeline principal (directo)
# ---------------------------
def pipeline_directo():
    print("=== Iniciando pipeline directo — Aurelion (estudiante IA) ===\n")
    dfs = load_all()
    dfs = normalize_column_names(dfs)

    merged = preprocess_and_merge(dfs)  # unificado con precios saneados
    pivot = build_monthly_pivot(merged)

    X, y, feat_cols, target_col = create_supervised(pivot, n_lags=PAST_MONTHS_FEATURES)

    model, preds_series = train_and_predict(X, y)

    # Ranking histórico (último mes real) y ranking predicho
    ranking_historico = pivot[target_col].sort_values(ascending=False).rename('historical_quantity').reset_index()
    ranking_predicho = preds_series.sort_values(ascending=False).reset_index().rename(columns={'index': 'id_producto', 'predicted_quantity': 'predicted_quantity'})

    # Añadir nombres de productos si están disponibles para mejor lectura
    productos_df = dfs.get('productos')
    if productos_df is not None:
        # Si productos tiene columna 'nombre_producto', la usamos; si no, buscamos variantes
        name_col = None
        for c in productos_df.columns:
            if 'nombre' in c.lower():
                name_col = c
                break
        if name_col:
            ranking_predicho = ranking_predicho.merge(productos_df[['id_producto', name_col]], on='id_producto', how='left')
            ranking_historico = ranking_historico.merge(productos_df[['id_producto', name_col]], on='id_producto', how='left')
            ranking_predicho.rename(columns={name_col: 'nombre_producto'}, inplace=True)
            ranking_historico.rename(columns={name_col: 'nombre_producto'}, inplace=True)

        # Guardar artefactos
    joblib.dump(model, MODEL_PATH)
    ranking_predicho.head(TOP_N).to_csv(OUTPUT_TOP, index=False)
    ranking_historico.head(TOP_N).to_csv("ranking_historico.csv", index=False)
    print(f"\n✅ Modelo guardado: {MODEL_PATH}")
    print(f"✅ Top {TOP_N} predichos exportados: {OUTPUT_TOP}")
    print(f"✅ Top {TOP_N} históricos exportados: ranking_historico.csv")

    # Resumen en consola (formato presentable)
    print("\n--- Resumen — Top productos históricos (último mes real) ---")
    if 'nombre_producto' in ranking_historico.columns:
        print(ranking_historico[['id_producto', 'nombre_producto', 'historical_quantity']].head(TOP_N).to_string(index=False))
    else:
        print(ranking_historico.head(TOP_N).to_string(index=False))

    print("\n--- Resumen — Top productos predichos (próximo mes) ---")
    if 'nombre_producto' in ranking_predicho.columns:
        print(ranking_predicho[['id_producto', 'nombre_producto', 'predicted_quantity']].head(TOP_N).to_string(index=False))
    else:
        print(ranking_predicho.head(TOP_N).to_string(index=False))

    # Resumen en consola (formato presentable)
    print("\n--- Resumen — Top productos históricos (último mes real) ---")
    if 'nombre_producto' in ranking_historico.columns:
        print(ranking_historico[['id_producto', 'nombre_producto', 'historical_quantity']].head(TOP_N).to_string(index=False))
    else:
        print(ranking_historico.head(TOP_N).to_string(index=False))

    print("\n--- Resumen — Top productos predichos (próximo mes) ---")
    if 'nombre_producto' in ranking_predicho.columns:
        print(ranking_predicho[['id_producto', 'nombre_producto', 'predicted_quantity']].head(TOP_N).to_string(index=False))
    else:
        print(ranking_predicho.head(TOP_N).to_string(index=False))

    print("\n=== Pipeline completo. Resultado listo para incorporar al informe. ===\n")
    
    ranking_historico.head(TOP_N).to_csv("ranking_historico.csv", index=False)
    print(f"✅ Top {TOP_N} históricos exportados: ranking_historico.csv")

    return {
        'merged': merged,
        'pivot': pivot,
        'ranking_historico': ranking_historico,
        'ranking_predicho': ranking_predicho,
        'model': model
    }

# ---------------------------
# Ejecutar
# ---------------------------
if __name__ == "__main__":
    try:
        artifacts = pipeline_directo()
    except Exception as e:
        print("\n❌ Error en pipeline:", str(e))
        print("Revisá las cabeceras de tus archivos o la carpeta 'Base de datos'.")
        sys.exit(1)

    # Mensaje final motivador (estudiante que cierra su demo)
    print("¡Listo! 🎓 Pipeline finalizado sin romper nada (esperemos).")
    print("Siguientes archivos creados:")
    print(f" - {OUTPUT_UNIFIED}")
    print(f" - {OUTPUT_TOP}")
    print(f" - {MODEL_PATH}")
    print("\nConsejo: si querés el dashboard interactivo, podemos activar Streamlit en un siguiente paso.")
