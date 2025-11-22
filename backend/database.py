import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar .env que está en la misma carpeta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    return conn

def test_query():
    """Hace un SELECT 1 para probar la conexión."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT 1 AS ok;")
            row = cur.fetchone()
            return row
    finally:
        conn.close()

def get_saldo(numero_cuenta: str):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT saldo FROM cuentas WHERE numero_cuenta = %s",
                (numero_cuenta,)
            )
            row = cur.fetchone()   # None si no existe
            return row
    finally:
        conn.close()


