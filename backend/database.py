import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from decimal import Decimal
import bcrypt



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

    monto_decimal = Decimal(str(monto))

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Traer cuenta, incluyendo ESTADO
            cur.execute(
                "SELECT id, saldo, estado FROM cuentas WHERE numero_cuenta = %s FOR UPDATE",
                (numero_cuenta,),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError("Cuenta no encontrada")

            # Validar bloqueo
            if row["estado"] == "BLOQUEADA":
                raise ValueError("Cuenta bloqueada")

            saldo_actual = Decimal(row["saldo"])
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
                (
                    row["id"],
                    "DEPOSITO",
                    monto_decimal,
                    "Depósito en cajero",
                    nuevo_saldo,
                ),
            )

        conn.commit()
        return nuevo_saldo
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def hacer_retiro(numero_cuenta: str, monto: float, pin: str):
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    monto_decimal = Decimal(str(monto))

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, saldo, pin_hash, estado FROM cuentas WHERE numero_cuenta = %s FOR UPDATE",
                (numero_cuenta,),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError("Cuenta no encontrada")

            if row["estado"] == "BLOQUEADA":
                raise ValueError("Cuenta bloqueada")

            if not bcrypt.checkpw(pin.encode("utf-8"), row["pin_hash"].encode("utf-8")):
                raise ValueError("PIN incorrecto")

            saldo_actual = Decimal(row["saldo"])

            if saldo_actual < monto_decimal:
                raise ValueError("Saldo insuficiente")

            nuevo_saldo = saldo_actual - monto_decimal

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
                (
                    row["id"],
                    "RETIRO",
                    monto_decimal,
                    "Retiro en cajero",
                    nuevo_saldo,
                ),
            )

        conn.commit()
        return nuevo_saldo
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()



def hacer_transferencia(cuenta_origen: str, cuenta_destino: str, monto: float, pin: str):
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    if cuenta_origen == cuenta_destino:
        raise ValueError("La cuenta origen y destino no pueden ser la misma")

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Traer cuenta origen
            cur.execute(
                "SELECT id, saldo, pin_hash, estado FROM cuentas WHERE numero_cuenta = %s FOR UPDATE",
                (cuenta_origen,),
            )
            origen = cur.fetchone()
            if origen is None:
                raise ValueError("Cuenta origen no encontrada")

            if origen["estado"] == "BLOQUEADA":
                raise ValueError("Cuenta origen bloqueada")

            if not bcrypt.checkpw(pin.encode("utf-8"), origen["pin_hash"].encode("utf-8")):
                raise ValueError("PIN incorrecto")

            # Traer cuenta destino
            cur.execute(
                "SELECT id, saldo FROM cuentas WHERE numero_cuenta = %s FOR UPDATE",
                (cuenta_destino,),
            )
            destino = cur.fetchone()
            if destino is None:
                raise ValueError("Cuenta destino no encontrada")

            saldo_origen = Decimal(origen["saldo"])
            saldo_destino = Decimal(destino["saldo"])
            monto_decimal = Decimal(str(monto))

            if saldo_origen < monto_decimal:
                raise ValueError("Saldo insuficiente en cuenta origen")

            nuevo_saldo_origen = saldo_origen - monto_decimal
            nuevo_saldo_destino = saldo_destino + monto_decimal

            # Actualizar saldos
            cur.execute(
                "UPDATE cuentas SET saldo = %s WHERE id = %s",
                (nuevo_saldo_origen, origen["id"]),
            )
            cur.execute(
                "UPDATE cuentas SET saldo = %s WHERE id = %s",
                (nuevo_saldo_destino, destino["id"]),
            )

            # Registrar movimientos (OJO: la columna se llama 'monto', no 'monto_decimal')
            cur.execute(
                """
                INSERT INTO movimientos (cuenta_id, tipo, monto, descripcion, saldo_resultante)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    origen["id"],
                    "TRF_SALIDA",
                    monto_decimal,
                    f"Transferencia a {cuenta_destino}",
                    nuevo_saldo_origen,
                ),
            )

            cur.execute(
                """
                INSERT INTO movimientos (cuenta_id, tipo, monto, descripcion, saldo_resultante)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    destino["id"],
                    "TRF_ENTRADA",
                    monto_decimal,
                    f"Transferencia desde {cuenta_origen}",
                    nuevo_saldo_destino,
                ),
            )

        conn.commit()
        return nuevo_saldo_origen, nuevo_saldo_destino
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def obtener_historial(numero_cuenta: str, limite: int = 10):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Buscar la cuenta
            cur.execute(
                "SELECT id FROM cuentas WHERE numero_cuenta = %s",
                (numero_cuenta,),
            )
            cuenta = cur.fetchone()
            if cuenta is None:
                return None

            # Traer últimos movimientos
            cur.execute(
                """
                SELECT tipo, monto, fecha, descripcion, saldo_resultante
                FROM movimientos
                WHERE cuenta_id = %s
                ORDER BY fecha DESC
                LIMIT %s
                """,
                (cuenta["id"], limite),
            )
            rows = cur.fetchall()
            return rows
    finally:
        conn.close()

import bcrypt
from decimal import Decimal
from psycopg2.extras import RealDictCursor

def cambiar_pin(numero_cuenta: str, pin_actual: str, pin_nuevo: str):
    if len(pin_nuevo) != 4 or not pin_nuevo.isdigit():
        raise ValueError("El nuevo PIN debe tener 4 dígitos numéricos")

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Obtener la cuenta
            cur.execute(
                "SELECT id, pin_hash FROM cuentas WHERE numero_cuenta = %s FOR UPDATE",
                (numero_cuenta,)
            )
            cuenta = cur.fetchone()

            if cuenta is None:
                raise ValueError("Cuenta no encontrada")

            # Verificar PIN actual
            if not bcrypt.checkpw(pin_actual.encode("utf-8"), cuenta["pin_hash"].encode("utf-8")):
                raise ValueError("El PIN actual es incorrecto")

            # Hashear nuevo PIN
            nuevo_hash = bcrypt.hashpw(pin_nuevo.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            # Actualizar PIN
            cur.execute(
                "UPDATE cuentas SET pin_hash = %s WHERE id = %s",
                (nuevo_hash, cuenta["id"])
            )

            # Registrar movimiento
            cur.execute(
                """
                INSERT INTO movimientos (cuenta_id, tipo, monto, descripcion, saldo_resultante)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (cuenta["id"], "CAMBIO_PIN", Decimal("0"), "Cambio de PIN", Decimal("0"))
            )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def bloquear_cuenta(numero_cuenta: str, motivo: str = None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Verificar cuenta
            cur.execute(
                "SELECT id FROM cuentas WHERE numero_cuenta = %s",
                (numero_cuenta,)
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError("Cuenta no encontrada")

            # Bloquear
            cur.execute(
                "UPDATE cuentas SET estado = 'BLOQUEADA' WHERE id = %s",
                (row["id"],)
            )

            # Registrar movimiento
            cur.execute(
                """
                INSERT INTO movimientos (cuenta_id, tipo, monto, descripcion, saldo_resultante)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    row["id"],
                    "BLOQUEO",
                    Decimal("0.00"),
                    motivo or "Bloqueo manual de cuenta",
                    Decimal("0.00"),
                ),
            )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()








