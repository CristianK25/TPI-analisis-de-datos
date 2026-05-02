import pandas as pd
import numpy as np
import os

# --- REGLAS DE NEGOCIO (Configuración de Calidad) ---
REGLAS_CALIDAD = {
    'rango_edad': (15, 95),
    'max_horas_estudio': 168,
    'nota_minima': 0,
    'nota_maxima': 100,
    'asistencia_minima_alerta': 75,
    'gpa_minimo_alerta': 2.5
}

def obtener_rutas_datos():
    """Gestiona las rutas según el entorno de ejecución."""
    cwd = os.getcwd()
    if cwd.endswith('notebooks') or cwd.endswith('src'):
        ruta_base = os.path.join('..', 'data')
    else:
        ruta_base = 'data'
    
    return {
        'sucio': os.path.join(ruta_base, 'dataset_DIRTY.csv'),
        'limpio': os.path.join(ruta_base, 'dataset_CLEAN.csv')
    }

def auditar_datos(df):
    """Analiza el dataset y devuelve un reporte dinámico de inconsistencias."""
    reporte_nulos = df.isnull().sum()[df.isnull().sum() > 0].to_dict()
    
    outliers = {}
    if 'Age' in df.columns:
        outliers['edad_invalida'] = int(df[(df['Age'] < REGLAS_CALIDAD['rango_edad'][0]) | 
                                           (df['Age'] > REGLAS_CALIDAD['rango_edad'][1])].shape[0])
    
    if 'Previous_GPA' in df.columns:
        outliers['gpa_invalido'] = int(df[df['Previous_GPA'] < REGLAS_CALIDAD['nota_minima']].shape[0])
        
    if 'Weekly_Study_Hours' in df.columns:
        outliers['horas_estudio_imposibles'] = int(df[df['Weekly_Study_Hours'] > REGLAS_CALIDAD['max_horas_estudio']].shape[0])
    
    cols_numericas = df.select_dtypes(include=[np.number]).columns
    valores_negativos = {col: int((df[col] < 0).sum()) for col in cols_numericas if 'ID' not in col and (df[col] < 0).any()}

    return {
        'total_filas': len(df),
        'duplicados': int(df.duplicated().sum()),
        'columnas_con_nulos': reporte_nulos,
        'outliers': outliers,
        'valores_negativos_genericos': valores_negativos
    }

def limpiar_datos(df):
    """Ejecuta la limpieza y NORMALIZACIÓN de strings."""
    df_limpio = df.copy()
    
    # 1. Eliminar duplicados
    df_limpio = df_limpio.drop_duplicates()
    
    # 2. Normalización de STRINGS (Hito 2 consigna)
    # Vuela espacios y estandariza mayúsculas/minúsculas en columnas de texto
    cols_texto = df_limpio.select_dtypes(include=['object']).columns
    for col in cols_texto:
        df_limpio[col] = df_limpio[col].str.strip().str.title()
    
    # 3. Limpiar Outliers
    if 'Age' in df_limpio.columns:
        df_limpio.loc[(df_limpio['Age'] < REGLAS_CALIDAD['rango_edad'][0]) | 
                      (df_limpio['Age'] > REGLAS_CALIDAD['rango_edad'][1]), 'Age'] = np.nan
                     
    if 'Previous_GPA' in df_limpio.columns:
        df_limpio.loc[df_limpio['Previous_GPA'] < REGLAS_CALIDAD['nota_minima'], 'Previous_GPA'] = np.nan
        
    if 'Weekly_Study_Hours' in df_limpio.columns:
        df_limpio.loc[df_limpio['Weekly_Study_Hours'] > REGLAS_CALIDAD['max_horas_estudio'], 'Weekly_Study_Hours'] = np.nan

    # 4. IMPUTACIÓN DINÁMICA DE NULOS
    cols_con_nulos = df_limpio.columns[df_limpio.isnull().any()].tolist()
    for col in cols_con_nulos:
        if pd.api.types.is_numeric_dtype(df_limpio[col]):
            df_limpio[col] = df_limpio[col].fillna(df_limpio[col].median())
        else:
            df_limpio[col] = df_limpio[col].fillna(df_limpio[col].mode()[0] if not df_limpio[col].mode().empty else "Desconocido")
            
    return df_limpio

def crear_caracteristicas(df):
    """Feature Engineering: Creación de nuevas variables (Hito 2 consigna)."""
    df_feat = df.copy()
    
    # A. Eficiencia de Estudio (Puntos por hora estudiada)
    # Evitamos división por cero sumando un pequeño valor
    df_feat['Eficiencia_Estudio'] = df_feat['Final_Exam_Score'] / (df_feat['Weekly_Study_Hours'] + 0.1)
    
    # B. Índice de Desgaste (Relación Estrés / Sueño)
    df_feat['Indice_Desgaste'] = df_feat['Stress_Level'] / (df_feat['Sleep_Hours'] + 0.1)
    
    # C. Alerta de Riesgo (Booleano)
    df_feat['Alerta_Riesgo'] = (df_feat['Attendance_Rate'] < REGLAS_CALIDAD['asistencia_minima_alerta']) & \
                               (df_feat['Previous_GPA'] < REGLAS_CALIDAD['gpa_minimo_alerta'])
                               
    return df_feat

def ejecutar_etl():
    """Flujo completo: Extracción -> Limpieza -> Feature Engineering -> Carga."""
    rutas = obtener_rutas_datos()
    if not os.path.exists(rutas['sucio']):
        return "Error: No se encontró el dataset."
        
    df = pd.read_csv(rutas['sucio'])
    
    # Limpieza y Normalización
    df_limpio = limpiar_datos(df)
    
    # Ingeniería de Variables
    df_final = crear_caracteristicas(df_limpio)
    
    # Guardado
    df_final.to_csv(rutas['limpio'], index=False)
    
    return {
        'reporte_inicial': auditar_datos(df),
        'reporte_final': auditar_datos(df_limpio),
        'nuevas_variables': ['Eficiencia_Estudio', 'Indice_Desgaste', 'Alerta_Riesgo']
    }

if __name__ == "__main__":
    ejecutar_etl()
