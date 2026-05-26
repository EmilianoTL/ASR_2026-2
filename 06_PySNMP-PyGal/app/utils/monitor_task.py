import time
import threading
from app.services.snmp_service import consulta_snmp_v3
from app.config import Config

monitor_state = {
    "activo": False,
    "intervalo": 20,
    "datos_capturados": [],
    "hilo": None
}

def tarea_monitoreo():
    print(f"[HILO] Iniciado. Intervalo={monitor_state['intervalo']}s | IP router={Config.IP_ROUTER}")
    print(f"[HILO] OID unicast={Config.OID_UNICAST_IN} | OID admin={Config.OID_ADMIN_STATUS}")

    paquetes_anteriores_raw = consulta_snmp_v3(Config.OID_UNICAST_IN)
    paquetes_anteriores = paquetes_anteriores_raw if paquetes_anteriores_raw is not None else 0
    print(f"[HILO] Valor inicial paquetes unicast: {paquetes_anteriores} "
          f"({'OK' if paquetes_anteriores_raw is not None else 'FALLO SNMP - revisa credenciales/índice'})")

    while monitor_state["activo"]:
        intervalo_objetivo = monitor_state["intervalo"]
        print(f"[HILO] Esperando {intervalo_objetivo}s para siguiente muestra...")

        # Sleep en trozos de 1s para reaccionar a cambios de intervalo
        inicio = time.time()
        while monitor_state["activo"]:
            time.sleep(1)
            if time.time() - inicio >= monitor_state["intervalo"]:
                break

        if not monitor_state["activo"]:
            break

        ts = time.strftime('%H:%M:%S')
        paquetes_raw = consulta_snmp_v3(Config.OID_UNICAST_IN)
        estado_raw   = consulta_snmp_v3(Config.OID_ADMIN_STATUS)

        # None = fallo SNMP; usar último valor conocido para paquetes y asumir DOWN
        paquetes_actuales = paquetes_raw if paquetes_raw is not None else paquetes_anteriores
        estado_admin      = estado_raw   if estado_raw  is not None else 2

        print(f"[MUESTRA {ts}] paquetes={paquetes_actuales} (snmp={'OK' if paquetes_raw is not None else 'FALLO'}) | "
              f"estado_admin={estado_admin} ({'UP' if estado_admin == 1 else 'DOWN'}) "
              f"(snmp={'OK' if estado_raw is not None else 'FALLO'})")

        delta_paquetes = paquetes_actuales - paquetes_anteriores
        if delta_paquetes < 0:
            delta_paquetes = 0
        paquetes_anteriores = paquetes_actuales

        estado_grafica = 100 if estado_admin == 1 else 0

        muestra = {
            "tiempo": ts,
            "delta_paquetes": delta_paquetes,
            "estado_admin_raw": estado_admin,
            "estado_grafica": estado_grafica
        }
        monitor_state["datos_capturados"].append(muestra)
        print(f"[MUESTRA {ts}] Guardada → delta={delta_paquetes} | "
              f"total muestras={len(monitor_state['datos_capturados'])}")

    print("[HILO] Detenido.")


def iniciar_hilo(tiempo):
    # Si ya hay un hilo corriendo, detenerlo primero
    if monitor_state["activo"]:
        print(f"[API] Monitoreo ya activo. Reiniciando con nuevo intervalo={tiempo}s")
        monitor_state["activo"] = False
        if monitor_state["hilo"] and monitor_state["hilo"].is_alive():
            monitor_state["hilo"].join(timeout=3)

    monitor_state["intervalo"] = tiempo
    monitor_state["datos_capturados"] = []
    monitor_state["activo"] = True

    monitor_state["hilo"] = threading.Thread(target=tarea_monitoreo, daemon=True)
    monitor_state["hilo"].start()
    print(f"[API] Hilo de monitoreo arrancado con intervalo={tiempo}s")


def detener_hilo():
    print("[API] Deteniendo monitoreo...")
    monitor_state["activo"] = False
