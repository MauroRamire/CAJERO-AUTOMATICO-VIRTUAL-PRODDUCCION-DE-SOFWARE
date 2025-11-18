from domain import Movimiento,TipoMovimiento
from database import obtener_cuenta,registrar_movimiento

def depositar(num,monto):
    c=obtener_cuenta(num)
    c.saldo+=monto
    registrar_movimiento(num,Movimiento(tipo=TipoMovimiento.CONSIGNACION,monto=monto,descripcion='Depósito'))
    return c.saldo
