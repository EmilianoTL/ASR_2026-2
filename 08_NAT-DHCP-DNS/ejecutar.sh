#!/bin/bash

# Obtener la ruta absoluta de la carpeta donde está este script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Cambiar a ese directorio para que Ansible encuentre los archivos
cd "$DIR"

echo "=== Iniciando automatización con Ansible ==="
ansible-playbook -i hosts.ini site.yml