class Config:
    # SNMPv3 Settings
    SNMP_USER = 'admin_snmp'
    AUTH_PWD = 'MiPasswordAuth'
    PRIV_PWD = 'MiPasswordPriv'
    IP_ROUTER = '192.168.3.1'
    
    # OIDs (Asegúrate de que el índice sea el correcto, ej. 2 para f2/0)
    INDICE_F2_0 = "2"
    OID_UNICAST_IN = f"1.3.6.1.2.1.2.2.1.11.{INDICE_F2_0}"
    OID_ADMIN_STATUS = f"1.3.6.1.2.1.2.2.1.7.{INDICE_F2_0}"