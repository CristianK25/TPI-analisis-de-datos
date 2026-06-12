"""
load_db.py – Carga del dataset limpio a PostgreSQL para el Hito 3 (Grafana).

Lee `data/dataset_CLEAN.csv` y lo vuelca en la tabla `students` de una base
PostgreSQL (la que levanta `docker-compose.yml`). Usa COPY por bloques para
cargar las ~500.000 filas de forma eficiente.

Uso:
    python src/load_db.py

Variables de entorno reconocidas (con valores por defecto que coinciden con
docker-compose.yml):
    DB_HOST     (default: localhost)
    DB_PORT     (default: 5432)
    DB_NAME     (default: tpi)
    DB_USER     (default: tpi)
    DB_PASSWORD (default: tpi)
    CSV_PATH    (default: data/dataset_CLEAN.csv)
"""

import io
import os
import sys
import time

import pandas as pd
import psycopg2

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "tpi"),
    "user": os.getenv("DB_USER", "tpi"),
    "password": os.getenv("DB_PASSWORD", "tpi"),
}

CSV_PATH = os.getenv("CSV_PATH", os.path.join(BASE_DIR, "data", "dataset_CLEAN.csv"))
TABLE_NAME = "students"
CHUNK_SIZE = 50_000

# Mapeo de tipos pandas -> SQL para el CREATE TABLE.
SQL_TYPES = {
    "int64": "BIGINT",
    "float64": "DOUBLE PRECISION",
    "bool": "BOOLEAN",
    "object": "TEXT",
}


def _normalizar_columna(nombre: str) -> str:
    """Pasa los nombres de columna a snake_case en minúsculas (estándar SQL)."""
    return nombre.strip().lower()


def conectar(reintentos: int = 10, espera: int = 3) -> psycopg2.extensions.connection:
    """Abre una conexión a PostgreSQL, reintentando mientras la DB arranca."""
    ultimo_error = None
    for intento in range(1, reintentos + 1):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            print(f"[OK] Conectado a PostgreSQL en {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")
            return conn
        except psycopg2.OperationalError as e:
            ultimo_error = e
            print(f"[..] Intento {intento}/{reintentos}: la base aún no responde. Reintento en {espera}s.")
            time.sleep(espera)
    raise RuntimeError(f"No se pudo conectar a PostgreSQL tras {reintentos} intentos: {ultimo_error}")


def crear_tabla(conn, df_muestra: pd.DataFrame) -> None:
    """Crea la tabla `students` infiriendo los tipos desde una muestra del CSV."""
    columnas_sql = []
    for col in df_muestra.columns:
        tipo = SQL_TYPES.get(str(df_muestra[col].dtype), "TEXT")
        columnas_sql.append(f'    "{col}" {tipo}')
    ddl = (
        f"DROP TABLE IF EXISTS {TABLE_NAME};\n"
        f"CREATE TABLE {TABLE_NAME} (\n" + ",\n".join(columnas_sql) + "\n);"
    )
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()
    print(f"[OK] Tabla '{TABLE_NAME}' creada con {len(df_muestra.columns)} columnas.")


def cargar_por_bloques(conn) -> int:
    """Lee el CSV en bloques y los inserta con COPY (rápido para grandes volúmenes)."""
    total = 0
    columnas = None
    for i, chunk in enumerate(pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE)):
        chunk.columns = [_normalizar_columna(c) for c in chunk.columns]
        if columnas is None:
            columnas = chunk.columns
            crear_tabla(conn, chunk)

        buffer = io.StringIO()
        chunk.to_csv(buffer, index=False, header=False, na_rep="\\N")
        buffer.seek(0)
        cols_sql = ", ".join(f'"{c}"' for c in columnas)
        with conn.cursor() as cur:
            cur.copy_expert(
                f"COPY {TABLE_NAME} ({cols_sql}) FROM STDIN WITH (FORMAT csv, NULL '\\N')",
                buffer,
            )
        conn.commit()
        total += len(chunk)
        print(f"[..] Bloque {i + 1}: {len(chunk):>6} filas cargadas (acumulado: {total:>7}).")
    return total


def crear_indices(conn) -> None:
    """Índices sobre las columnas más usadas por los paneles del dashboard."""
    indices = [
        f"CREATE INDEX IF NOT EXISTS idx_major ON {TABLE_NAME} (major_subject);",
        f"CREATE INDEX IF NOT EXISTS idx_study ON {TABLE_NAME} (weekly_study_hours);",
        f"CREATE INDEX IF NOT EXISTS idx_internet ON {TABLE_NAME} (internet_quality);",
        f"CREATE INDEX IF NOT EXISTS idx_riesgo ON {TABLE_NAME} (alerta_riesgo);",
    ]
    with conn.cursor() as cur:
        for sql in indices:
            cur.execute(sql)
    conn.commit()
    print("[OK] Índices creados.")


def main() -> int:
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] No se encontró el CSV en: {CSV_PATH}")
        print("        Descargá 'dataset_CLEAN.csv' desde el Google Drive del repo")
        print("        y dejalo en la carpeta data/. Ver README para el enlace.")
        return 1

    print(f"[..] Origen de datos: {CSV_PATH}")
    inicio = time.time()
    conn = conectar()
    try:
        total = cargar_por_bloques(conn)
        crear_indices(conn)
    finally:
        conn.close()
    dur = time.time() - inicio
    print(f"\n[LISTO] {total:,} filas cargadas en '{TABLE_NAME}' en {dur:.1f}s.")
    print("        Grafana ya puede consultar la base. Abrí http://localhost:3000")
    return 0


if __name__ == "__main__":
    sys.exit(main())
