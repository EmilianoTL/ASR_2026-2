import pygal

def generar_svg(datos_capturados):
    """Genera la gráfica en formato SVG a partir de los datos."""
    if not datos_capturados:
        return None

    tiempos = [d["tiempo"] for d in datos_capturados]
    paquetes = [d["delta_paquetes"] for d in datos_capturados]
    estados = [d["estado_grafica"] for d in datos_capturados]

    line_chart = pygal.Line(title='Tráfico de Entrada vs Estado Administrativo f2/0', x_label_rotation=45)
    line_chart.x_labels = tiempos
    line_chart.add('Paquetes Unicast (Delta)', paquetes)
    line_chart.add('Estado Admin (100=Up, 0=Down)', estados)

    return line_chart.render()