import time
import threading
from app.services.snmp_service import consulta_snmp_v3
from app.config import Config

# Diccionario para mantener el estado global del monitoreo
monitor_state = {
    "activo": False,
    "intervalo": 20,
    "datos_capturados": [],
    "hilo": None
}

def tarea_monitoreo():
    paquetes_anteriores = consulta_snmp_v3(Config.OID_UNICAST_IN) or 0
    
    while monitor_state["activo"]:
        time.sleep(monitor_state["intervalo"])
        
        paquetes_actuales = consulta_snmp_v3(Config.OID_UNICAST_IN) or 0
        estado_admin = consulta_snmp_v3(Config.OID_ADMIN_STATUS) or 2 # 1=Up, 2=Down
        
        delta_paquetes = paquetes_actuales - paquetes_anteriores
        if delta_paquetes < 0: delta_paquetes = 0
        paquetes_anteriores = paquetes_actuales
        
        estado_grafica = 100 if estado_admin == 1 else 0
        
        muestra = {
            "tiempo": time.strftime('%H:%M:%S'),
            "delta_paquetes": delta_paquetes,
            "estado_admin_raw": estado_admin,
            "estado_grafica": estado_grafica
        }
        monitor_state["datos_capturados"].append(muestra)

def iniciar_hilo(tiempo):
    monitor_state["intervalo"] = tiempo
    monitor_state["datos_capturados"] = []
    
    if not monitor_state["activo"]:
        monitor_state["activo"] = True
        monitor_state["hilo"] = threading.Thread(target=tarea_monitoreo)
        monitor_state["hilo"].daemon = True
        monitor_state["hilo"].start()

def detener_hilo():
    monitor_state["activo"] = False