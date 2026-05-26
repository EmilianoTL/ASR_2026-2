from flask import Blueprint, jsonify, make_response
from app.utils.monitor_task import monitor_state, iniciar_hilo, detener_hilo, calcular_deltas
from app.services.graph_service import generar_svg

api_bp = Blueprint('api', __name__)


def _error(mensaje, codigo):
    return jsonify({"error": mensaje, "codigo": codigo}), codigo


# ---------------------------------------------------------------------------
# POST /R1/monitoreo/f2_0/<tiempo>
# Inicia el monitoreo en f2/0 cada <tiempo> segundos eliminando capturas
# anteriores.
# 201 Created  → monitoreo iniciado por primera vez
# 200 OK       → monitoreo reiniciado (ya estaba activo)
# 400 Bad Request → tiempo inválido
# ---------------------------------------------------------------------------
@api_bp.route('/R1/monitoreo/f2_0/<int:tiempo>', methods=['POST'])
def iniciar_monitoreo(tiempo):
    if tiempo <= 0:
        print(f"[POST 400] tiempo={tiempo} inválido")
        return _error("El tiempo de muestreo debe ser un entero mayor a 0.", 400)

    ya_activo = monitor_state["activo"]
    iniciar_hilo(tiempo)

    codigo  = 200 if ya_activo else 201
    mensaje = "Monitoreo reiniciado" if ya_activo else "Monitoreo iniciado"
    print(f"[POST {codigo}] /R1/monitoreo/f2_0/{tiempo} → {mensaje}")
    return jsonify({
        "mensaje":             mensaje,
        "interfaz":            "FastEthernet2/0",
        "estado_monitoreo":    "activo",
        "intervalo_segundos":  tiempo,
    }), codigo


# ---------------------------------------------------------------------------
# GET /R1/monitoreo/f2_0
# Devuelve el historial de muestras y el estado de la interfaz.
# 200 OK siempre (lista vacía si aún no hay muestras)
# ---------------------------------------------------------------------------
@api_bp.route('/R1/monitoreo/f2_0', methods=['GET'])
def obtener_datos():
    estado   = "activo" if monitor_state["activo"] else "detenido"
    muestras = calcular_deltas(monitor_state["datos_capturados"])
    n        = len(muestras)
    print(f"[GET 200] /R1/monitoreo/f2_0 → estado={estado} | deltas={n} | "
          f"intervalo={monitor_state['intervalo']}s")
    return jsonify({
        "interfaz":           "FastEthernet2/0",
        "estado_monitoreo":   estado,
        "intervalo_segundos": monitor_state["intervalo"],
        "total_muestras":     n,
        "muestras":           muestras,
    }), 200


# ---------------------------------------------------------------------------
# PUT /R1/monitoreo/f2_0/<tiempo>
# Cambia el intervalo de muestreo en un monitoreo activo.
# 200 OK        → intervalo actualizado
# 400 Bad Request → tiempo inválido
# 409 Conflict  → no hay monitoreo activo
# ---------------------------------------------------------------------------
@api_bp.route('/R1/monitoreo/f2_0/<int:tiempo>', methods=['PUT'])
def actualizar_tiempo(tiempo):
    if tiempo <= 0:
        print(f"[PUT 400] tiempo={tiempo} inválido")
        return _error("El tiempo de muestreo debe ser un entero mayor a 0.", 400)

    if not monitor_state["activo"]:
        print("[PUT 409] No hay monitoreo activo")
        return _error("No hay monitoreo activo. Use POST para iniciar uno.", 409)

    anterior = monitor_state["intervalo"]
    monitor_state["intervalo"] = tiempo
    print(f"[PUT 200] /R1/monitoreo/f2_0/{tiempo} → {anterior}s → {tiempo}s")
    return jsonify({
        "mensaje":                    "Intervalo de muestreo actualizado",
        "interfaz":                   "FastEthernet2/0",
        "intervalo_anterior_segundos": anterior,
        "intervalo_nuevo_segundos":    tiempo,
    }), 200


# ---------------------------------------------------------------------------
# DELETE /R1/monitoreo/f2_0
# Detiene el monitoreo y devuelve todas las muestras capturadas.
# 200 OK       → monitoreo detenido
# 409 Conflict → no había monitoreo activo
# ---------------------------------------------------------------------------
@api_bp.route('/R1/monitoreo/f2_0', methods=['DELETE'])
def detener_monitoreo():
    if not monitor_state["activo"]:
        print("[DELETE 409] No hay monitoreo activo")
        return _error("No hay monitoreo activo para detener.", 409)

    # Calcular deltas y detener
    muestras = calcular_deltas(monitor_state["datos_capturados"])
    detener_hilo()
    print(f"[DELETE 200] /R1/monitoreo/f2_0 → {len(muestras)} deltas devueltos")
    return jsonify({
        "mensaje":        "Monitoreo detenido",
        "interfaz":       "FastEthernet2/0",
        "total_muestras": len(muestras),
        "muestras":       muestras,
    }), 200


# ---------------------------------------------------------------------------
# GET /R1/monitoreo/f2_0/grafica
# Genera y devuelve la gráfica SVG con tráfico y estado administrativo.
# 200 OK    → SVG generado correctamente
# 404 Not Found → sin datos para graficar
# ---------------------------------------------------------------------------
@api_bp.route('/R1/monitoreo/f2_0/grafica', methods=['GET'])
def generar_grafica():
    n = len(monitor_state["datos_capturados"])
    print(f"[GET] /R1/monitoreo/f2_0/grafica → {n} muestras disponibles")

    svg_data = generar_svg(monitor_state["datos_capturados"])

    if not svg_data:
        print("[GET 404] /R1/monitoreo/f2_0/grafica → sin datos")
        return _error(
            "Se necesitan al menos 2 muestras para graficar. Inicie el monitoreo "
            "con POST /R1/monitoreo/f2_0/<tiempo> y espere al menos 2 muestras.",
            404
        )

    print(f"[GET 200] /R1/monitoreo/f2_0/grafica → SVG generado ({n} muestras)")
    response = make_response(svg_data)
    response.headers['Content-Type'] = 'image/svg+xml'
    return response, 200
