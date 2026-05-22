import pygal

MAX_ETIQUETAS_X = 12

def generar_svg(datos_capturados):
    if not datos_capturados:
        return None

    tiempos  = [d["tiempo"]         for d in datos_capturados]
    paquetes = [d["delta_paquetes"] for d in datos_capturados]
    estados  = [d["estado_grafica"] for d in datos_capturados]

    # Eje X dinámico: mostrar como máximo MAX_ETIQUETAS_X etiquetas
    n = len(tiempos)
    if n <= MAX_ETIQUETAS_X:
        etiquetas_visibles = tiempos
    else:
        paso = n // MAX_ETIQUETAS_X
        etiquetas_visibles = tiempos[::paso]
        if tiempos[-1] not in etiquetas_visibles:
            etiquetas_visibles = list(etiquetas_visibles) + [tiempos[-1]]

    # Escala del eje secundario (derecha) para estado: 0=Down, 100=Up
    chart = pygal.Line(
        title='Tráfico de Entrada vs Estado Administrativo f2/0',
        x_label_rotation=45,
        secondary_range=(0, 110),
        legend_at_bottom=True,
        show_minor_x_labels=False,
        y_title='Paquetes Unicast (delta)',
        secondary_y_title='Estado Interfaz',
    )

    chart.x_labels        = tiempos
    chart.x_labels_major  = etiquetas_visibles

    chart.add('Paquetes Unicast (Delta)',   paquetes)
    chart.add('Estado Admin (100=Up, 0=Down)', estados, secondary=True)

    return chart.render()
