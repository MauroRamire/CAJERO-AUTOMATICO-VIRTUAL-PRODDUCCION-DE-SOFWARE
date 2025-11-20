from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import uvicorn

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

# ---------------------------
# FRONTEND (html, css, js)
# ---------------------------

app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse(BASE_DIR / "frontend" / "index.html")


# ---------------------------
# MODELOS DE DATOS
# ---------------------------

class LoginRequest(BaseModel):
    usuario: str
    pin: str

class MontoRequest(BaseModel):
    usuario: str
    monto: float


# ---------------------------
# "BASE DE DATOS" EN MEMORIA (ejemplo)
# ---------------------------

# Usuario de prueba: 1234 / 1234
usuarios = {
    "1234": {
        "pin": "1234",
        "saldo": 100000.0,
        "bloqueado": False,
        "historial": []
    }
}


# ---------------------------
# ENDPOINTS DEL CAJERO
# ---------------------------

@app.post("/api/login")
def login(data: LoginRequest):
    user = usuarios.get(data.usuario)
    if not user or user["pin"] != data.pin:
        raise HTTPException(status_code=401, detail="Usuario o PIN incorrectos")
    if user["bloqueado"]:
        raise HTTPException(status_code=403, detail="Cuenta bloqueada")
    return {"ok": True, "usuario": data.usuario}


@app.get("/api/saldo/{usuario}")
def obtener_saldo(usuario: str):
    user = usuarios.get(usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"saldo": user["saldo"]}


@app.post("/api/depositar")
def depositar(data: MontoRequest):
    user = usuarios.get(data.usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if data.monto <= 0:
        raise HTTPException(status_code=400, detail="Monto inválido")

    user["saldo"] += data.monto
    user["historial"].append({"tipo": "DEPÓSITO", "monto": data.monto})
    return {"mensaje": "Depósito exitoso", "saldo": user["saldo"]}


@app.post("/api/retirar")
def retirar(data: MontoRequest):
    user = usuarios.get(data.usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if data.monto <= 0:
        raise HTTPException(status_code=400, detail="Monto inválido")
    if data.monto > user["saldo"]:
        raise HTTPException(status_code=400, detail="Fondos insuficientes")

    user["saldo"] -= data.monto
    user["historial"].append({"tipo": "RETIRO", "monto": data.monto})
    return {"mensaje": "Retiro exitoso", "saldo": user["saldo"]}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

