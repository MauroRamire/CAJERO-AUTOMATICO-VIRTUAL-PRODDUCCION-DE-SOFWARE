from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import test_query, get_saldo, hacer_deposito, hacer_retiro
from database import (
    test_query,
    get_saldo,
    hacer_deposito,
    hacer_retiro,
    hacer_transferencia,
    obtener_historial,
    cambiar_pin_db,
    bloquear_cuenta_db,
)






app = FastAPI(title="Cajero Virtual API")


# =====================
# Modelos de petición
# =====================

class LoginRequest(BaseModel):
    email: str
    password: str

class RetiroRequest(BaseModel):
    numero_cuenta: str
    monto: float
    pin: str

class DepositoRequest(BaseModel):
    numero_cuenta: str
    monto: float

class TransferenciaRequest(BaseModel):
    cuenta_origen: str
    cuenta_destino: str
    monto: float
    pin: str

class CambiarPINRequest(BaseModel):
    numero_cuenta: str
    pin_actual: str
    pin_nuevo: str

class BloquearCuentaRequest(BaseModel):
    numero_cuenta: str
    motivo: Optional[str] = None


# =====================
# Endpoints
# =====================

@app.get("/")
def root():
    return {"message": "Cajero Virtual API funcionando"}

@app.post("/login")
def login(data: LoginRequest):
    # Por ahora, respuesta simulada
    return {"status": "ok", "message": "Login correcto (mock)", "user": data.email}

@app.post("/logout")
def logout():
    return {"status": "ok", "message": "Logout correcto (mock)"}

@app.get("/saldo")
def obtener_saldo(numero_cuenta: str):
    row = get_saldo(numero_cuenta)
    if row is None:
        return {"status": "error", "message": "Cuenta no encontrada"}
    return {
        "status": "ok",
        "numero_cuenta": numero_cuenta,
        "saldo": float(row["saldo"])
    }


@app.post("/deposito")
def deposito(data: DepositoRequest):
    try:
        nuevo_saldo = hacer_deposito(data.numero_cuenta, data.monto)
        return {
            "status": "ok",
            "tipo": "deposito",
            "numero_cuenta": data.numero_cuenta,
            "monto": data.monto,
            "nuevo_saldo": float(nuevo_saldo),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 👇 cambiar esta línea
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transferencia")
def transferencia(data: TransferenciaRequest):
    try:
        nuevo_saldo_origen, nuevo_saldo_destino = hacer_transferencia(
        data.cuenta_origen,
        data.cuenta_destino,
        data.monto,
        data.pin,
        )
        
        return {
            "status": "ok",
            "tipo": "transferencia",
            "cuenta_origen": data.cuenta_origen,
            "cuenta_destino": data.cuenta_destino,
            "monto": data.monto,
            "nuevo_saldo_origen": float(nuevo_saldo_origen),
            "nuevo_saldo_destino": float(nuevo_saldo_destino),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/historial")
def historial(numero_cuenta: str, limite: int = 10):
    rows = obtener_historial(numero_cuenta, limite)
    if rows is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    return {
        "status": "ok",
        "numero_cuenta": numero_cuenta,
        "cantidad_movimientos": len(rows),
        "movimientos": [
            {
                "tipo": r["tipo"],
                "monto": float(r["monto"]),
                "fecha": r["fecha"],
                "descripcion": r["descripcion"],
                "saldo_resultante": float(r["saldo_resultante"]),
            }
            for r in rows
        ],
    }


@app.put("/cambiarPIN")
def cambiar_pin(data: CambiarPINRequest):
    try:
        cambiar_pin_db(data.numero_cuenta, data.pin_actual, data.pin_nuevo)
        return {
            "status": "ok",
            "message": "PIN cambiado correctamente",
            "numero_cuenta": data.numero_cuenta,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/bloquearCuenta")
def bloquear_cuenta(data: BloquearCuentaRequest):
    try:
        bloquear_cuenta_db(data.numero_cuenta, data.motivo)
        return {
            "status": "ok",
            "message": "Cuenta bloqueada correctamente",
            "numero_cuenta": data.numero_cuenta,
            "motivo": data.motivo,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/comprobante")
def comprobante(id_transaccion: str):
    return {
        "id_transaccion": id_transaccion,
        "detalle": "Comprobante simulado de la transacción"
    }

@app.get("/db-test")
def db_test():
    try:
        result = test_query()
        return {"status": "ok", "db_response": result}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/retiro")
def retiro(data: RetiroRequest):
    try:
        nuevo_saldo = hacer_retiro(data.numero_cuenta, data.monto, data.pin)
        return {
            "status": "ok",
            "tipo": "retiro",
            "numero_cuenta": data.numero_cuenta,
            "monto": data.monto,
            "nuevo_saldo": float(nuevo_saldo),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 👇 cambiar esta línea
        raise HTTPException(status_code=500, detail=str(e))





