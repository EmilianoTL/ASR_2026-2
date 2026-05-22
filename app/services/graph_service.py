import pygal

DIVISIONES = 20      # divisiones fijas en ambos ejes
COUNTER32_MAX = 2**32


def _calcular_deltas(datos):
    """
    Calcula el delta entre lecturas consecutivas de contador_raw.
    Maneja wrap-around de Counter32.
    Retorna (tiempos, deltas, estados) como listas paralelas.
    """
    tiempos, deltas, estados = [], [], []

    for i in range(1, len(datos)):
        raw_actual   = datos[i]["contador_raw"]
        raw_anterior = datos[i - 1]["contador_raw"]

        if raw_actual is not None and raw_anterior is not None:
            delta = raw_actual - raw_anterior
            if delta < 0:
                delta = COUNTER32_MAX + delta  # wrap-around Counter32
        else:
            delta = 0  # SNMP falló en alguna de las dos lecturas

        tiempos.append(datos[i]["tiempo"])
        deltas.append(delta)
        estados.append(1 if datos[i]["estado_admin_raw"] == 1 else 0)

    return tiempos, deltas, estados


def _etiquetas_x(tiempos):
    """
    Selecciona exactamente DIVISIONES etiquetas distribuidas uniformemente,
    garantizando que aparezcan la primera y la última.
    """
    n = len(tiempos)
    if n <= DIVISIONES:
        return tiempos[:]

    indices = {int(round(i * (n - 1) / (DIVISIONES - 1))) for i in range(DIVISIONES)}
    indices.add(0)
    indices.add(n - 1)
    return [tiempos[i] for i in sorted(indices)]


def _y_labels_primario(deltas):
    """
    Genera exactamente DIVISIONES + 1 ticks (0 … max) para el eje Y primario.
    """
    max_val = max(deltas) if deltas and max(deltas) > 0 else DIVISIONES
    return [round(max_val * i / DIVISIONES) for i in range(DIVISIONES + 1)]


def generar_svg(datos_capturados):
    """
    Calcula los deltas al vuelo a partir de los contadores crudos
    y genera la gráfica SVG con doble eje Y.
    Requiere al menos 2 muestras para poder calcular un delta.
    """
    if len(datos_capturados) < 2:
        return None

    tiempos, deltas, estados = _calcular_deltas(datos_capturados)

    if not deltas:
        return None

    etiquetas_visibles = _etiquetas_x(tiempos)
    y_labels_prim      = _y_labels_primario(deltas)

    chart = pygal.Line(
        title='Tráfico de Entrada vs Estado Administrativo f2/0',
        x_label_rotation=45,
        # Eje Y secundario: binario 0 (Off) / 1 (On)
        secondary_range=(0, 1),
        legend_at_bottom=True,
        show_minor_x_labels=False,
        y_title='Paquetes Unicast (delta/muestra)',
        secondary_y_title='Estado Admin (0=Off, 1=On)',
    )

    # Eje X: DIVISIONES etiquetas fijas entre inicio y fin
    chart.x_labels       = tiempos
    chart.x_labels_major = etiquetas_visibles

    # Eje Y primario: 0 a max con DIVISIONES divisiones iguales
    chart.y_labels = y_labels_prim

    chart.add('Paquetes Unicast (Delta)', deltas)
    chart.add('Estado Admin (1=On, 0=Off)', estados, secondary=True)

    return chart.render()
