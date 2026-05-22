from flask import Blueprint, jsonify, make_response
from app.utils.monitor_task import monitor_state, iniciar_hilo, detener_hilo
from app.services.graph_service import generar_svg

api_bp = Blueprint('api', __name__)

@api_bp.route('/R1/monitoreo/f2_0/<int:tiempo>', methods=['POST'])
def iniciar_monitoreo(tiempo):
    print(f"[POST] /R1/monitoreo/f2_0/{tiempo} → Iniciando monitoreo")
    iniciar_hilo(tiempo)
    return jsonify({"mensaje": "Monitoreo iniciado", "intervalo": tiempo})

@api_bp.route('/R1/monitoreo/f2_0', methods=['GET'])
def obtener_datos():
    n = len(monitor_state["datos_capturados"])
    estado = "Activo" if monitor_state["activo"] else "Detenido"
    print(f"[GET] /R1/monitoreo/f2_0 → estado={estado} | muestras={n} | intervalo={monitor_state['intervalo']}s")
    return jsonify({
        "muestras": monitor_state["datos_capturados"],
        "estado_interfaz": estado
    })

@api_bp.route('/R1/monitoreo/f2_0/<int:tiempo>', methods=['PUT'])
def actualizar_tiempo(tiempo):
    anterior = monitor_state["intervalo"]
    monitor_state["intervalo"] = tiempo
    print(f"[PUT] /R1/monitoreo/f2_0/{tiempo} → Intervalo cambiado de {anterior}s a {tiempo}s")
    return jsonify({"mensaje": "Tiempo actualizado", "nuevo_intervalo": tiempo})

@api_bp.route('/R1/monitoreo/f2_0', methods=['DELETE'])
def detener_monitoreo():
    n = len(monitor_state["datos_capturados"])
    print(f"[DELETE] /R1/monitoreo/f2_0 → Deteniendo. Muestras capturadas={n}")
    detener_hilo()
    return jsonify({
        "mensaje": "Monitoreo detenido",
        "muestras_finales": monitor_state["datos_capturados"]
    })

@api_bp.route('/R1/monitoreo/f2_0/grafica', methods=['GET'])
def generar_grafica():
    n = len(monitor_state["datos_capturados"])
    print(f"[GET] /R1/monitoreo/f2_0/grafica → Generando gráfica con {n} muestras")
    svg_data = generar_svg(monitor_state["datos_capturados"])

    if not svg_data:
        print("[GET] /R1/monitoreo/f2_0/grafica → Sin datos suficientes")
        return jsonify({"error": "No hay datos suficientes para graficar"}), 400

    response = make_response(svg_data)
    response.headers['Content-Type'] = 'image/svg+xml'
    return response
