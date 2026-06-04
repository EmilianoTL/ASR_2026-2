import paramiko
import time
import json
import os

ROUTERS_FILE = os.path.join(os.path.dirname(__file__), "config", "routers.json")

with open(ROUTERS_FILE) as f:
    ROUTERS = json.load(f)


def execute_commands(router_key: str, commands: list[str]) -> dict:
    """
    Abre una sesión SSH al router indicado,
    ejecuta los comandos y retorna el output.
    """
    if router_key not in ROUTERS:
        return {"error": f"Router '{router_key}' no encontrado en routers.json"}

    router = ROUTERS[router_key]

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname = router["host"],
            port     = router["port"],
            username = router["username"],
            password = router["password"],
            timeout  = 10,
        )

        channel = client.invoke_shell()
        time.sleep(0.5)

        for cmd in commands:
            channel.send(cmd + "\n")
            time.sleep(0.3)

        output = channel.recv(65535).decode(errors="ignore")
        client.close()

        return {"router": router_key, "host": router["host"], "output": output}

    except Exception as e:
        return {"router": router_key, "error": str(e)}


def execute_on_routers(scenario_block: dict) -> list:
    """
    Recibe un bloque del JSON de escenarios (sin 'description')
    y ejecuta los comandos en cada router indicado.
    """
    results = []
    for router_key, commands in scenario_block.items():
        if router_key == "description":
            continue
        result = execute_commands(router_key, commands)
        results.append(result)
    return results