import time
import threading
from app.services.snmp_service import consulta_snmp_v3
from app.config import Config

COUNTER32_MAX = 2 ** 32

monitor_state = {
    "activo": False,
    "intervalo": 20,
    "datos_capturados": [],
    "hilo": None
}


def calcular_deltas(datos):
    """
    Calcula los deltas a partir de lecturas crudas consecutivas.
    Fórmula de desbordamiento Counter32: delta = MAX - prev + actual
    Retorna lista de dicts con tiempo, delta_paquetes y estado_admin_raw.
    """
    resultado = []
    for i in range(1, len(datos)):
        raw_actual   = datos[i]["contador_raw"]
        raw_anterior = datos[i - 1]["contador_raw"]

        if raw_actual is not None and raw_anterior is not None:
            delta = raw_actual - raw_anterior
            if delta < 0:
                delta = COUNTER32_MAX - raw_anterior + raw_actual
        else:
            delta = 0

        resultado.append({
            "tiempo":          datos[i]["tiempo"],
            "delta_paquetes":  delta,
            "estado_admin_raw": datos[i]["estado_admin_raw"],
            "estado":          "Up" if datos[i]["estado_admin_raw"] == 1 else "Down",
        })
    return resultado


def tarea_monitoreo():
    print(f"[HILO] Iniciado. Intervalo={monitor_state['intervalo']}s | IP={Config.IP_ROUTER}")
    print(f"[HILO] OID_unicast={Config.OID_UNICAST_IN} | OID_admin={Config.OID_ADMIN_STATUS}")

    while monitor_state["activo"]:
        print(f"[HILO] Esperando {monitor_state['intervalo']}s...")

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
        estado_admin = estado_raw if estado_raw is not None else 2

        muestra = {
            "tiempo":           ts,
            "contador_raw":     contador_raw,
            "estado_admin_raw": estado_admin,
        }
        monitor_state["datos_capturados"].append(muestra)
        print(f"[MUESTRA {ts}] raw={contador_raw} "
              f"({'OK' if contador_raw is not None else 'FALLO'}) | "
              f"admin={estado_admin} ({'UP' if estado_admin == 1 else 'DOWN'}) | "
              f"total={len(monitor_state['datos_capturados'])}")

    print("[HILO] Detenido.")


def iniciar_hilo(tiempo):
    if monitor_state["activo"]:
        print(f"[API] Reiniciando monitoreo con intervalo={tiempo}s")
        monitor_state["activo"] = False
        if monitor_state["hilo"] and monitor_state["hilo"].is_alive():
            monitor_state["hilo"].join(timeout=3)

    monitor_state["intervalo"] = tiempo
    monitor_state["datos_capturados"] = []
    monitor_state["activo"] = True
    monitor_state["hilo"] = threading.Thread(target=tarea_monitoreo, daemon=True)
    monitor_state["hilo"].start()
    print(f"[API] Hilo arrancado con intervalo={tiempo}s")


def detener_hilo():
    print("[API] Deteniendo monitoreo...")
    monitor_state["activo"] = False
