from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from database import test_query


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

class DepositoRequest(BaseModel):
    numero_cuenta: str
    monto: float

class TransferenciaRequest(BaseModel):
    cuenta_origen: str
    cuenta_destino: str
    monto: float

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
    # mock
    return {"numero_cuenta": numero_cuenta, "saldo": 123456.78}

@app.post("/retiro")
def retiro(data: RetiroRequest):
    return {
        "status": "ok",
        "tipo": "retiro",
        "numero_cuenta": data.numero_cuenta,
        "monto": data.monto
    }

@app.post("/deposito")
def deposito(data: DepositoRequest):
    return {
        "status": "ok",
        "tipo": "deposito",
        "numero_cuenta": data.numero_cuenta,
        "monto": data.monto
    }

@app.post("/transferencia")
def transferencia(data: TransferenciaRequest):
    return {
        "status": "ok",
        "tipo": "transferencia",
        "cuenta_origen": data.cuenta_origen,
        "cuenta_destino": data.cuenta_destino,
        "monto": data.monto
    }

@app.get("/historial")
def historial(numero_cuenta: str):
    # mock de movimientos
    return {
        "numero_cuenta": numero_cuenta,
        "movimientos": [
            {"tipo": "retiro", "monto": 100000},
            {"tipo": "deposito", "monto": 200000},
        ]
    }

@app.put("/cambiarPIN")
def cambiar_pin(data: CambiarPINRequest):
    return {
        "status": "ok",
        "message": "PIN cambiado (mock)",
        "numero_cuenta": data.numero_cuenta
    }

@app.put("/bloquearCuenta")
def bloquear_cuenta(data: BloquearCuentaRequest):
    return {
        "status": "ok",
        "message": "Cuenta bloqueada (mock)",
        "numero_cuenta": data.numero_cuenta,
        "motivo": data.motivo,
    }

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




