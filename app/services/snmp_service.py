from pysnmp.hlapi import *
from app.config import Config

def consulta_snmp_v3(oid):
    """Realiza una consulta GET usando SNMPv3."""
    iterator = getCmd(
        SnmpEngine(),
        UsmUserData(
            Config.SNMP_USER, 
            authKey=Config.AUTH_PWD, 
            privKey=Config.PRIV_PWD,
            authProtocol=usmHMACSHAAuthProtocol,
            privProtocol=usmDESPrivProtocol
        ),
        UdpTransportTarget((Config.IP_ROUTER, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    if errorIndication or errorStatus:
        return None
    for varBind in varBinds:
        try:
            return int(varBind[1])
        except (ValueError, TypeError):
            # Si el router devuelve "NoSuchInstance", devolvemos 0 en lugar de crashear
            return 0