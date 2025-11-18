from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from domain import (
    Cuenta, 
    Movimiento, 
    TipoMovimiento, 
    EstadoCuenta,
    DatosMonto,
    DatosTransfer,
    DatosPin
)
from database import (
    crear_cuenta,
    obtener_cuenta,
    obtener_movimientos,
    registrar_movimiento,
    buscar_movimiento_por_id,
)
from movimiento import depositar

app = FastAPI()

# ======================================================
# CORS (permitir que el frontend acceda)
# ======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# CUENTA INICIAL (para que el login funcione)
# ======================================================
cuenta_inicial = Cuenta(
    numero="1234",
    nombre="Mauro",
    pin="1234",
    saldo=5000000,
    estado=EstadoCuenta.ACTIVA
)

try:
    crear_cuenta(cuenta_inicial)
except:
    pass


@app.get("/")
def home():
    return {"ok": True}

# ======================================================
# CREAR CUENTA
# ======================================================
@app.post("/cuentas")
def crear_nueva_cuenta(cuenta: Cuenta):
    try:
        crear_cuenta(cuenta)
        return {"mensaje": "Cuenta creada correctamente", "cuenta": cuenta}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ======================================================
# OBTENER CUENTA
# ======================================================
@app.get("/cuentas/{numero}")
def obtener_cuenta_por_numero(numero: str):
    try:
        return obtener_cuenta(numero)
    except ValueError:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")


# ======================================================
# DEPÓSITO
# ======================================================
@app.post("/deposito/{numero}")
def realizar_deposito(numero: str, datos: DatosMonto):
    try:
        monto = datos.monto
        nuevo_saldo = depositar(numero, monto)

        registrar_movimiento(
            numero,
            Movimiento(
                tipo=TipoMovimiento.CONSIGNACION,
                monto=monto,
                descripcion="Depósito"
            )
        )

        return {"mensaje": "Depósito exitoso", "saldo": nuevo_saldo}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ======================================================
# RETIRO
# ======================================================
@app.post("/retiro/{numero}")
def realizar_retiro(numero: str, datos: DatosMonto):
    monto = datos.monto
    cuenta = obtener_cuenta(numero)

    if cuenta.saldo < monto:
        raise HTTPException(status_code=400, detail="Fondos insuficientes")

    cuenta.saldo -= monto

    registrar_movimiento(
        numero,
        Movimiento(
            tipo=TipoMovimiento.RETIRO,
            monto=monto,
            descripcion="Retiro de dinero",
        )
    )

    return {"mensaje": "Retiro exitoso", "saldo": cuenta.saldo}


# ======================================================
# TRANSFERENCIA
# ======================================================
@app.post("/transferencia")
def transferir(datos: DatosTransfer):
    origen = datos.origen
    destino = datos.destino
    monto = datos.monto

    c_origen = obtener_cuenta(origen)
    c_destino = obtener_cuenta(destino)

    if c_origen.saldo < monto:
        raise HTTPException(status_code=400, detail="Fondos insuficientes")

    c_origen.saldo -= monto
    c_destino.saldo += monto

    registrar_movimiento(
        origen,
        Movimiento(
            tipo=TipoMovimiento.TRANSFERENCIA_SALIDA,
            monto=monto,
            descripcion=f"Transferido a {destino}"
        )
    )

    registrar_movimiento(
        destino,
        Movimiento(
            tipo=TipoMovimiento.TRANSFERENCIA_ENTRADA,
            monto=monto,
            descripcion=f"Recibido de {origen}"
        )
    )

    return {"mensaje": "Transferencia exitosa"}


# ======================================================
# HISTORIAL
# ======================================================
@app.get("/historial/{numero}")
def historial(numero: str):
    return obtener_movimientos(numero)


# ======================================================
# COMPROBANTE
# ======================================================
@app.get("/comprobante/{id}")
def comprobar(id: str):
    mov = buscar_movimiento_por_id(id)
    if not mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    return mov


# ======================================================
# CAMBIAR PIN
# ======================================================
@app.post("/cambiar_pin/{numero}")
def cambiar_pin(numero: str, datos: DatosPin):
    cuenta = obtener_cuenta(numero)

    if cuenta.pin != datos.actual:
        raise HTTPException(status_code=400, detail="PIN incorrecto")

    cuenta.pin = datos.nuevo
    return {"mensaje": "PIN actualizado correctamente"}


# ======================================================
# BLOQUEAR CUENTA
# ======================================================
@app.post("/bloquear/{numero}")
def bloquear(numero: str):
    cuenta = obtener_cuenta(numero)
    cuenta.estado = EstadoCuenta.BLOQUEADA
    return {"mensaje": "Cuenta bloqueada exitosamente"}
