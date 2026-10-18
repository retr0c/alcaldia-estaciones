from collections import defaultdict

from estaciones.grafo import TOLERANCIA, distancias_desde


def costo_estacion(costo_base, factor_zona):
    return round(costo_base * factor_zona)


def incidentes_por_tipo_y_nodo(instancia):
    indice = {tipo: defaultdict(list) for tipo in instancia.tipos}
    for id_incidente, nodo, tipo in instancia.incidentes:
        indice[tipo][nodo].append(id_incidente)
    return indice


def calcular_alcances(instancia):
    tipos = instancia.parametros["tipos"]
    radio_max = max(datos["radio_m"] for datos in tipos.values())
    indice = incidentes_por_tipo_y_nodo(instancia)

    alcances = {}
    for codigo, nodo, factor in instancia.lotes:
        distancias = distancias_desde(instancia.adyacencia, nodo, radio_max)
        for tipo, datos in tipos.items():
            limite = datos["radio_m"] + TOLERANCIA
            cubiertos = []
            for nodo_alcanzado, distancia in distancias.items():
                if distancia <= limite:
                    cubiertos.extend(indice[tipo].get(nodo_alcanzado, ()))
            alcances[(codigo, tipo)] = {
                "costo": costo_estacion(datos["costo_base"], factor),
                "incidentes": sorted(cubiertos),
            }
    return alcances