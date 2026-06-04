from flask import Flask, jsonify
import json
import os
from ssh_manager import execute_on_routers

app = Flask(__name__)

SCENARIOS_FILE = os.path.join(os.path.dirname(__file__), "config", "scenarios.json")

with open(SCENARIOS_FILE) as f:
    SCENARIOS = json.load(f)


def apply_scenario(number: str) -> tuple:
    """
    Limpia ACLs previas y aplica el escenario indicado.
    Retorna (response_dict, http_status).
    """
    # 1. Siempre limpiar primero
    clear_results = execute_on_routers(SCENARIOS["clear"])

    # 2. Si es escenario 0, solo limpiar
    if number == "0":
        return {
            "escenario"   : 0,
            "descripcion" : SCENARIOS["clear"]["description"],
            "estado"      : "activo",
            "resultados"  : clear_results,
        }, 200

    # 3. Aplicar escenario solicitado
    if number not in SCENARIOS:
        return {"error": f"Escenario {number} no existe"}, 404

    scenario    = SCENARIOS[number]
    apply_results = execute_on_routers(scenario)

    return {
        "escenario"   : int(number),
        "descripcion" : scenario.get("description", ""),
        "estado"      : "activo",
        "limpieza"    : clear_results,
        "aplicacion"  : apply_results,
    }, 200


# ── Rutas ────────────────────────────────────────────────

@app.get("/api-rest/ACL/escenario/<int:n>")
def get_escenario(n: int):
    available = [k for k in SCENARIOS if k != "clear"]
    return jsonify({"escenarios_disponibles": available})


@app.post("/api-rest/ACL/escenario/<int:n>")
def post_escenario(n: int):
    response, status = apply_scenario(str(n))
    return jsonify(response), status


@app.delete("/api-rest/ACL/escenario/<int:n>")
def delete_escenario(n: int):
    results = execute_on_routers(SCENARIOS["clear"])
    return jsonify({
        "escenario" : n,
        "estado"    : "eliminado",
        "resultados": results,
    }), 200


# ── Inicio ───────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)