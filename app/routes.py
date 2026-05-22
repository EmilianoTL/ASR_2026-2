from flask import Blueprint, jsonify, make_response
from app.utils.monitor_task import monitor_state, iniciar_hilo, detener_hilo
from app.services.graph_service import generar_svg

# Blueprint para agrupar las rutas
api_bp = Blueprint('api', __name__)

@api_bp.route('/R1/monitoreo/f2_0/<int:tiempo>', methods=['POST'])
def iniciar_monitoreo(tiempo):
    iniciar_hilo(tiempo)
    return jsonify({"mensaje": "Monitoreo iniciado", "intervalo": tiempo})

@api_bp.route('/R1/monitoreo/f2_0', methods=['GET'])
def obtener_datos():
    return jsonify({
        "muestras": monitor_state["datos_capturados"], 
        "estado_interfaz": "Activo" if monitor_state["activo"] else "Detenido"
    })

@api_bp.route('/R1/monitoreo/f2_0/<int:tiempo>', methods=['PUT'])
def actualizar_tiempo(tiempo):
    monitor_state["intervalo"] = tiempo
    return jsonify({"mensaje": "Tiempo actualizado", "nuevo_intervalo": tiempo})

@api_bp.route('/R1/monitoreo/f2_0', methods=['DELETE'])
def detener_monitoreo():
    detener_hilo()
    return jsonify({
        "mensaje": "Monitoreo detenido", 
        "muestras_finales": monitor_state["datos_capturados"]
    })

@api_bp.route('/R1/monitoreo/f2_0/grafica', methods=['GET'])
def generar_grafica():
    svg_data = generar_svg(monitor_state["datos_capturados"])
    
    if not svg_data:
        return jsonify({"error": "No hay datos suficientes para graficar"}), 400
    
    response = make_response(svg_data)
    response.headers['Content-Type'] = 'image/svg+xml'
    return response