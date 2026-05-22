import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from app.config import Config

async def _consulta_asincrona(oid):
    transportTarget = await UdpTransportTarget.create((Config.IP_ROUTER, 161), timeout=3, retries=1)

    errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
        SnmpEngine(),
        CommunityData(Config.SNMP_COMMUNITY, mpModel=1),  # mpModel=1 → SNMPv2c
        transportTarget,
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    if errorIndication:
        print(f"[SNMP ERROR] OID={oid} | {errorIndication}")
        return None

    if errorStatus:
        print(f"[SNMP ERROR] OID={oid} | {errorStatus.prettyPrint()} en índice {errorIndex}")
        return None

    for varBind in varBinds:
        oid_resp, valor = varBind
        print(f"[SNMP OK] {oid_resp.prettyPrint()} → {valor.prettyPrint()} ({type(valor).__name__})")
        try:
            return int(valor)
        except (ValueError, TypeError):
            print(f"[SNMP WARN] No se pudo convertir a int: {valor!r}")
            return None

    print(f"[SNMP WARN] OID={oid} → respuesta vacía")
    return None


def consulta_snmp_v3(oid):
    return asyncio.run(_consulta_asincrona(oid))
