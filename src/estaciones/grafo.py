import heapq

TOLERANCIA = 1e-9


def distancias_desde(adyacencia, origen, radio_max):
    distancias = {origen: 0.0}
    cola = [(0.0, origen)]

    while cola:
        distancia, nodo = heapq.heappop(cola)
        if distancia > distancias[nodo]:
            continue
        for vecino, longitud in adyacencia.get(nodo, ()):
            nueva = distancia + longitud
            if nueva > radio_max + TOLERANCIA:
                continue
            if nueva < distancias.get(vecino, float("inf")):
                distancias[vecino] = nueva
                heapq.heappush(cola, (nueva, vecino))

    return distancias
