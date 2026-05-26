import re
import pygal
from app.utils.monitor_task import calcular_deltas

DIVISIONES_Y  = 5   # divisiones eje Y primario (paquetes)
DIVISIONES_X  = 20  # divisiones eje X (tiempo)
COUNTER32_MAX = 2 ** 32

# Valores intermedios que pygal auto-genera en secondary_range=(0,1)
_INTERMEDIOS_SECUNDARIO = ['0.2', '0.4', '0.6', '0.8', '0.25', '0.5', '0.75']


def _etiquetas_x(tiempos):
    """Selecciona exactamente DIVISIONES_X etiquetas (inicio … fin)."""
    n = len(tiempos)
    if n <= DIVISIONES_X:
        return tiempos[:]
    indices = sorted({int(round(i * (n - 1) / (DIVISIONES_X - 1)))
                      for i in range(DIVISIONES_X)} | {0, n - 1})
    return [tiempos[i] for i in indices]


def _y_ticks_primario(deltas):
    """6 ticks (0 … max) creando exactamente 5 divisiones iguales."""
    max_val = max(deltas) if deltas and max(deltas) > 0 else DIVISIONES_Y
    return [round(max_val * i / DIVISIONES_Y) for i in range(DIVISIONES_Y + 1)]


def _limpiar_eje_secundario(svg_bytes):
    """
    Elimina del SVG los labels intermedios del eje secundario derecho.
    Pygal auto-genera 0.2, 0.4, 0.6, 0.8 para secondary_range=(0,1).
    """
    svg_str = svg_bytes.decode('utf-8')
    for val in _INTERMEDIOS_SECUNDARIO:
        svg_str = re.sub(
            r'<text\b[^>]*>\s*' + re.escape(val) + r'\s*</text>',
            '',
            svg_str
        )
    return svg_str.encode('utf-8')


def generar_svg(datos_capturados):
    """
    Calcula deltas al vuelo desde los contadores crudos y genera SVG.
    Requiere mínimo 2 muestras.
    """
    if len(datos_capturados) < 2:
        return None

    muestras = calcular_deltas(datos_capturados)
    if not muestras:
        return None

    tiempos = [m["tiempo"]         for m in muestras]
    deltas  = [m["delta_paquetes"] for m in muestras]
    estados = [1 if m["estado_admin_raw"] == 1 else 0 for m in muestras]

    chart = pygal.Line(
        title='Tráfico de Entrada vs Estado Administrativo f2/0',
        x_label_rotation=45,
        secondary_range=(0, 1),
        legend_at_bottom=True,
        show_minor_x_labels=False,
        y_title='Paquetes Unicast (delta/muestra)',
        secondary_y_title='Estado Admin (0=Off  1=On)',
    )

    chart.x_labels       = tiempos
    chart.x_labels_major = _etiquetas_x(tiempos)
    chart.y_labels        = _y_ticks_primario(deltas)

    chart.add('Paquetes Unicast (Delta)', deltas)
    chart.add('Estado Admin (1=On, 0=Off)', estados, secondary=True)

    return _limpiar_eje_secundario(chart.render())
