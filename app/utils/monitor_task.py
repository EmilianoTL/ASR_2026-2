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

    while monitor_state["activo"]:
        print(f"[HILO] Esperando {monitor_state['intervalo']}s para siguiente muestra...")

        inicio = time.time()
        while monitor_state["activo"]:
            time.sleep(1)
            if time.time() - inicio >= monitor_state["intervalo"]:
                break

        if not monitor_state["activo"]:
            break

        ts           = time.strftime('%H:%M:%S')
        contador_raw = consulta_snmp_v3(Config.OID_UNICAST_IN)
        estado_raw   = consulta_snmp_v3(Config.OID_ADMIN_STATUS)

        # Guardar el contador crudo; el delta se calcula al generar la gráfica
        estado_admin = estado_raw if estado_raw is not None else 2

        muestra = {
            "tiempo":          ts,
            "contador_raw":    contador_raw,   # None si SNMP falló
            "estado_admin_raw": estado_admin,  # 1=Up, 2=Down
        }
        monitor_state["datos_capturados"].append(muestra)

        print(f"[MUESTRA {ts}] contador_raw={contador_raw} "
              f"(snmp={'OK' if contador_raw is not None else 'FALLO'}) | "
              f"estado={estado_admin} ({'UP' if estado_admin == 1 else 'DOWN'}) "
              f"(snmp={'OK' if estado_raw is not None else 'FALLO'}) | "
              f"total={len(monitor_state['datos_capturados'])}")

    print("[HILO] Detenido.")


def iniciar_hilo(tiempo):
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
