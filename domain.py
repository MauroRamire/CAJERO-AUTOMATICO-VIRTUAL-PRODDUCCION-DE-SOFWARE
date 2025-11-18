from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class EstadoCuenta(str, Enum):
    ACTIVA="ACTIVA"; BLOQUEADA="BLOQUEADA"; CERRADA="CERRADA"

class TipoMovimiento(str, Enum):
    CONSIGNACION="CONSIGNACION"; RETIRO="RETIRO"
    TRANSFERENCIA_ENTRADA="TRANSFERENCIA_ENTRADA"
    TRANSFERENCIA_SALIDA="TRANSFERENCIA_SALIDA"

class Movimiento(BaseModel):
    id:UUID=Field(default_factory=uuid4)
    fecha:datetime=Field(default_factory=datetime.now)
    tipo:TipoMovimiento
    monto:float
    descripcion:str

class Cuenta(BaseModel):
    numero:str
    titular:str
    pin:str
    saldo:float
    estado:EstadoCuenta=EstadoCuenta.ACTIVA
