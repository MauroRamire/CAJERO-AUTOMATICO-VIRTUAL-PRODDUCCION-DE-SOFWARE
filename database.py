from typing import Dict,List,Optional
from domain import Cuenta,Movimiento
from uuid import UUID

cuentas_db:Dict[str,Cuenta]={}
movimientos_db:Dict[str,List[Movimiento]]={}

def crear_cuenta(c:Cuenta):
    if c.numero in cuentas_db: raise ValueError('Existe')
    cuentas_db[c.numero]=c; movimientos_db[c.numero]=[]

def obtener_cuenta(n): 
    if n not in cuentas_db: raise ValueError('No existe')
    return cuentas_db[n]

def registrar_movimiento(n,m): movimientos_db[n].append(m)
def obtener_movimientos(n): return movimientos_db[n]
def buscar_movimiento_por_id(i:UUID):
    for lst in movimientos_db.values():
        for m in lst:
            if m.id==i: return m
    return None
