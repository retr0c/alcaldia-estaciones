from estaciones.heuristicas import HEURISTICAS, construir_propuesta, resumir_propuesta

PROPUESTAS_POR_SEGUNDO = 1e9
SEGUNDOS_POR_ANIO = 365.25 * 24 * 3600


def espacio_de_busqueda(instancia):
    opciones_por_lote = len(instancia.tipos) + 1
    combinaciones = opciones_por_lote ** len(instancia.lotes)
    segundos = combinaciones / PROPUESTAS_POR_SEGUNDO
    return {
        "lotes": len(instancia.lotes),
        "opciones_por_lote": opciones_por_lote,
        "combinaciones": combinaciones,
        "anios": segundos / SEGUNDOS_POR_ANIO,
    }


def _opciones_por_lote(instancia, alcances):
    pesos = {tipo: datos["peso"] for tipo, datos in instancia.parametros["tipos"].items()}

    posicion = {tipo: {} for tipo in instancia.tipos}
    for id_incidente, _, tipo in sorted(instancia.incidentes):
        posicion[tipo][id_incidente] = len(posicion[tipo])

    por_lote = {}
    for (lote, tipo), datos in alcances.items():
        if datos["costo"] > instancia.presupuesto or not datos["incidentes"]:
            continue
        mascara = 0
        for incidente in datos["incidentes"]:
            mascara |= 1 << posicion[tipo][incidente]
        por_lote.setdefault(lote, []).append(
            {"lote": lote, "tipo": tipo, "costo": datos["costo"],
             "mascara": mascara, "peso": pesos[tipo]}
        )

    lotes = sorted(por_lote)
    return [por_lote[lote] for lote in lotes]


def _ganancia(opcion, cubiertos):
    nuevos = opcion["mascara"] & ~cubiertos[opcion["tipo"]]
    return nuevos.bit_count() * opcion["peso"]


def _cota_superior(grupos, desde, presupuesto, cubiertos):
    items = []
    for grupo in grupos[desde:]:
        for opcion in grupo:
            if opcion["costo"] > presupuesto:
                continue
            ganancia = _ganancia(opcion, cubiertos)
            if ganancia > 0:
                items.append((ganancia / opcion["costo"], ganancia, opcion["costo"]))

    items.sort(reverse=True)
    total = 0.0
    restante = presupuesto
    for _, ganancia, costo in items:
        if costo <= restante:
            total += ganancia
            restante -= costo
        else:
            total += ganancia * restante / costo
            break
    return total


def mejor_propuesta(instancia, alcances):
    grupos = _opciones_por_lote(instancia, alcances)

    mejor = {"valor": -1, "estaciones": []}
    for criterio in HEURISTICAS.values():
        estaciones = construir_propuesta(instancia, alcances, criterio)
        valor = resumir_propuesta(instancia, alcances, estaciones)["valor"]
        if valor > mejor["valor"]:
            mejor = {"valor": valor, "estaciones": estaciones}

    nodos = [0]

    def buscar(indice, presupuesto, cubiertos, valor, elegidas):
        nodos[0] += 1
        if valor > mejor["valor"]:
            mejor["valor"] = valor
            mejor["estaciones"] = sorted((o["lote"], o["tipo"]) for o in elegidas)

        if indice == len(grupos):
            return
        if valor + _cota_superior(grupos, indice, presupuesto, cubiertos) <= mejor["valor"]:
            return

        opciones = [o for o in grupos[indice] if o["costo"] <= presupuesto]
        opciones.sort(key=lambda o: _ganancia(o, cubiertos), reverse=True)
        for opcion in opciones:
            ganancia = _ganancia(opcion, cubiertos)
            if ganancia == 0:
                continue
            nuevos_cubiertos = dict(cubiertos)
            nuevos_cubiertos[opcion["tipo"]] |= opcion["mascara"]
            elegidas.append(opcion)
            buscar(indice + 1, presupuesto - opcion["costo"], nuevos_cubiertos,
                   valor + ganancia, elegidas)
            elegidas.pop()

        buscar(indice + 1, presupuesto, cubiertos, valor, elegidas)

    buscar(0, instancia.presupuesto, {tipo: 0 for tipo in instancia.tipos}, 0, [])
    return mejor["estaciones"], nodos[0]