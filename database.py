from typing import Dict, List
from domain import Cuenta, Movimiento

cuentas_db: Dict[str, Cuenta] = {}
movimientos_db: Dict[str, List[Movimiento]] = {}

def crear_cuenta(cuenta: Cuenta):
    if cuenta.numero in cuentas_db:
        raise ValueError("La cuenta ya existe")
    cuentas_db[cuenta.numero] = cuenta
    movimientos_db[cuenta.numero] = []

def obtener_cuenta(numero: str):
    if numero not in cuentas_db:
        raise ValueError("La cuenta no existe")
    return cuentas_db[numero]

def registrar_movimiento(numero: str, movimiento: Movimiento):
    movimientos_db[numero].append(movimiento)

def obtener_movimientos(numero: str):
    return movimientos_db[numero]

def buscar_movimiento_por_id(id_mov):
    for lista in movimientos_db.values():
        for m in lista:
            if str(m.id) == id_mov:
                return m
    return None
