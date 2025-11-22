import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from decimal import Decimal


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
        # sslmode="require",  # si lo necesitas, ya te funcionaba sin esto
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
                (numero_cuenta,),
            )
            row = cur.fetchone()   # None si no existe
            return row
    finally:
        conn.close()


def hacer_deposito(numero_cuenta: str, monto: float):
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Bloquear la fila de la cuenta mientras se actualiza
            cur.execute(
                "SELECT id, saldo FROM cuentas WHERE numero_cuenta = %s FOR UPDATE",
                (numero_cuenta,),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError("Cuenta no encontrada")

            saldo_actual = Decimal(row["saldo"])
            monto_decimal = Decimal(str(monto))
            nuevo_saldo = saldo_actual + monto_decimal

            # Actualizar saldo
            cur.execute(
                "UPDATE cuentas SET saldo = %s WHERE id = %s",
                (nuevo_saldo, row["id"]),
            )

            # Registrar movimiento
            cur.execute(
                """
                INSERT INTO movimientos (cuenta_id, tipo, monto, descripcion, saldo_resultante)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (row["id"], "DEPOSITO", monto_decimal, "Depósito en efectivo", nuevo_saldo),
            )

        conn.commit()
        return nuevo_saldo
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()



def hacer_retiro(numero_cuenta: str, monto: float):
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, saldo FROM cuentas WHERE numero_cuenta = %s FOR UPDATE",
                (numero_cuenta,),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError("Cuenta no encontrada")

            if row["saldo"] < monto:
                raise ValueError("Saldo insuficiente")

            nuevo_saldo = row["saldo"] - monto

            # Actualizar saldo
            cur.execute(
                "UPDATE cuentas SET saldo = %s WHERE id = %s",
                (nuevo_saldo, row["id"]),
            )

            # Registrar movimiento
            cur.execute(
                """
                INSERT INTO movimientos (cuenta_id, tipo, monto, descripcion, saldo_resultante)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (row["id"], "RETIRO", monto, "Retiro en cajero", nuevo_saldo),
            )

        conn.commit()
        return nuevo_saldo
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()





