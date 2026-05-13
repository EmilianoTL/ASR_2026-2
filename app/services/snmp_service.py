import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from app.config import Config

async def _consulta_asincrona(oid):
    """Realiza la consulta real usando la nueva sintaxis asíncrona de PySNMP 7+"""
    
    # 1. Creamos el objetivo de red con el nuevo método await .create() que pedía el error
    transportTarget = await UdpTransportTarget.create((Config.IP_ROUTER, 161))
    
    # 2. Ejecutamos la consulta (ahora se usa 'await' en lugar de 'next')
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        UsmUserData(
            Config.SNMP_USER, 
            authKey=Config.AUTH_PWD, 
            privKey=Config.PRIV_PWD,
            authProtocol=usmHMACSHAAuthProtocol,
            privProtocol=usmAesCfb128Protocol
        ),
        transportTarget,
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    
    if errorIndication or errorStatus:
        return 0
        
    for varBind in varBinds:
        try:
            return int(varBind[1])
        except (ValueError, TypeError):
            return 0

def consulta_snmp_v3(oid):
    """
    Función envoltorio (wrapper) síncrona.
    Permite que el resto de tu aplicación (como el hilo de monitoreo)
    siga llamando a 'consulta_snmp_v3' de forma normal, mientras Python
    maneja la complejidad asíncrona en segundo plano.
    """
    return asyncio.run(_consulta_asincrona(oid))