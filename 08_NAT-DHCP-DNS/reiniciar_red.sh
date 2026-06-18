#!/bin/bash

# Asegurar que el script se ejecute como root
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, ejecuta este script como root (sudo)."
  exit 1
fi

echo "1. Matando procesos DHCP anteriores..."
killall udhcpc 2>/dev/null

echo "2. Purgando IPs y rutas viejas de las interfaces..."
ip addr flush dev eth0 2>/dev/null
ip addr flush dev eth1 2>/dev/null

echo "3. Bajando interfaces..."
ifdown eth0 2>/dev/null
ifdown eth1 2>/dev/null

echo "4. Levantando eth1 (Internet Real)..."
ifup eth1

echo "5. Levantando eth0 (Laboratorio GNS3)..."
# Lanzamos ifup en segundo plano para que el script no se quede pasmado
ifup eth0 &
PID_IFUP=$!

echo "   Esperando 5 segundos para que el router asigne una IP..."
sleep 5

# Verificamos si la interfaz eth0 consiguió una IP
if ! ip addr show eth0 | grep -q "inet "; then
    echo "   [!] DHCP falló o tardó demasiado."
    echo "   [!] Rescatando interfaz... Asignando IP provisional (192.168.0.50)."
    
    # Detenemos el ifup y el cliente DHCP que se quedaron en bucle
    kill $PID_IFUP 2>/dev/null
    killall udhcpc 2>/dev/null
    
    # Limpiamos y aplicamos configuración manual
    ip addr flush dev eth0
    ip addr add 192.168.0.50/24 dev eth0
    ip link set dev eth0 up
    
    # Agregamos la ruta hacia el router (ignoramos error si ya existe)
    ip route add default via 192.168.0.1 2>/dev/null
else
    echo "   [OK] IP obtenida por DHCP correctamente."
fi

echo "6. Aplicando contramedida de DNS para GitHub..."
echo "nameserver 8.8.8.8" > /etc/resolv.conf

echo "========================================="
echo "       RED ACTUALIZADA CON ÉXITO        "
echo "========================================="
echo "-> Tu estado actual de IP en eth0 (Lab):"
ip addr show eth0 | grep "inet " || echo "   Sin IP asignada en eth0"
echo "-----------------------------------------"
echo "-> Probando resolución DNS hacia GitHub:"
if ping -c 1 github.com >/dev/null 2>&1; then
    echo "   [OK] ¡github.com es accesible!"
else
    echo "   [ERROR] No hay resolución a GitHub. Revisa el cableado."
fi
echo "========================================="