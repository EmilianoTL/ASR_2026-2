import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from app.config import Config

async def _consulta_asincrona(oid):
    transportTarget = await UdpTransportTarget.create((Config.IP_ROUTER, 161), timeout=2, retries=1)

    errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
        SnmpEngine(),
        UsmUserData(
            Config.SNMP_USER,
            authKey=Config.AUTH_PWD,
            authProtocol=usmHMACSHAAuthProtocol,
        ),
        transportTarget,
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    if errorIndication:
        print(f"[SNMP ERROR] OID={oid} | errorIndication={errorIndication}")
        return None

    if errorStatus:
        print(f"[SNMP ERROR] OID={oid} | errorStatus={errorStatus.prettyPrint()} "
              f"en índice {errorIndex}")
        return None

    for varBind in varBinds:
        oid_resp, valor = varBind
        print(f"[SNMP OK] OID={oid_resp.prettyPrint()} → valor={valor.prettyPrint()} "
              f"(tipo={type(valor).__name__})")
        try:
            return int(valor)
        except (ValueError, TypeError):
            print(f"[SNMP WARN] No se pudo convertir a int: {valor!r}")
            return None

    print(f"[SNMP WARN] OID={oid} → respuesta vacía")
    return None


def consulta_snmp_v3(oid):
    return asyncio.run(_consulta_asincrona(oid))
