"""
Ejecuta este script en el Gestor con el mismo Python que usa Flask:
    python test_diagnostico.py
"""

print("=== Diagnóstico de entorno ===\n")

import sys
print(f"Python ejecutándose: {sys.executable}")
print(f"Versión: {sys.version}\n")

# 1. Verificar pycryptodomex
try:
    from Cryptodome.Cipher import DES
    print("✓ pycryptodomex está instalado y funciona")
except ImportError as e:
    print(f"✗ pycryptodomex NO disponible: {e}")
    print("  → Solución: pip install pycryptodomex\n")

# 2. Verificar pycryptodome
try:
    from Crypto.Cipher import DES
    print("✓ pycryptodome está instalado")
except ImportError:
    print("✗ pycryptodome no disponible (no es crítico si pycryptodomex sí está)")

# 3. Verificar pysnmp
try:
    import pysnmp
    print(f"✓ pysnmp versión: {pysnmp.__version__}")
except ImportError as e:
    print(f"✗ pysnmp NO disponible: {e}")

# 4. Prueba SNMP real
print("\n=== Prueba SNMP al router ===\n")
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

IP_ROUTER = '192.168.3.1'
SNMP_USER = 'admin_snmp'
AUTH_PWD  = 'MiPasswordAuth'
PRIV_PWD  = 'MiPasswordPriv'
OID_TEST  = '1.3.6.1.2.1.1.1.0'  # sysDescr - OID básico de prueba

async def prueba():
    try:
        target = await UdpTransportTarget.create((IP_ROUTER, 161), timeout=3, retries=1)

        # Prueba 1: SNMPv3 con auth+priv DES
        print("Prueba 1: SNMPv3 auth=SHA, priv=DES")
        errI, errS, errIdx, vbs = await get_cmd(
            SnmpEngine(),
            UsmUserData(SNMP_USER, authKey=AUTH_PWD, privKey=PRIV_PWD,
                        authProtocol=usmHMACSHAAuthProtocol,
                        privProtocol=usmDESPrivProtocol),
            target, ContextData(),
            ObjectType(ObjectIdentity(OID_TEST))
        )
        if errI:
            print(f"  ✗ Error: {errI}")
        elif errS:
            print(f"  ✗ Error SNMP: {errS}")
        else:
            print(f"  ✓ Éxito → {vbs[0][1].prettyPrint()[:60]}")

        # Prueba 2: SNMPv3 solo auth (sin privacidad)
        print("Prueba 2: SNMPv3 auth=SHA, sin priv")
        errI, errS, errIdx, vbs = await get_cmd(
            SnmpEngine(),
            UsmUserData(SNMP_USER, authKey=AUTH_PWD,
                        authProtocol=usmHMACSHAAuthProtocol),
            target, ContextData(),
            ObjectType(ObjectIdentity(OID_TEST))
        )
        if errI:
            print(f"  ✗ Error: {errI}")
        elif errS:
            print(f"  ✗ Error SNMP: {errS}")
        else:
            print(f"  ✓ Éxito → {vbs[0][1].prettyPrint()[:60]}")

    except Exception as e:
        print(f"  ✗ Excepción: {e}")

asyncio.run(prueba())
