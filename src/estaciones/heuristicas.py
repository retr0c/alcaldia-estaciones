def criterio_base(valor_agregado, costo):
    return valor_agregado


def criterio_eficiencia(valor_agregado, costo):
    return valor_agregado / costo


HEURISTICAS = {
    "base": criterio_base,
    "eficiencia": criterio_eficiencia,
}


def construir_propuesta(instancia, alcances, criterio):
    pesos = {tipo: datos["peso"] for tipo, datos in instancia.parametros["tipos"].items()}
    orden_tipos = {tipo: posicion for posicion, tipo in enumerate(instancia.tipos)}
    candidatas = sorted(alcances, key=lambda par: (par[0], orden_tipos[par[1]]))

    lotes_libres = {codigo for codigo, _, _ in instancia.lotes}
    presupuesto_restante = instancia.presupuesto
    cubiertos = set()
    elegidas = []

    while True:
        mejor = None
        mejor_clave = None

        for lote, tipo in candidatas:
            if lote not in lotes_libres:
                continue
            costo = alcances[(lote, tipo)]["costo"]
            if costo > presupuesto_restante:
                continue
            nuevos = [i for i in alcances[(lote, tipo)]["incidentes"] if i not in cubiertos]
            valor_agregado = len(nuevos) * pesos[tipo]
            if valor_agregado == 0:
                continue
            clave = criterio(valor_agregado, costo)
            if mejor_clave is None or clave > mejor_clave:
                mejor, mejor_clave = (lote, tipo), clave

        if mejor is None:
            break

        lote, tipo = mejor
        elegidas.append(mejor)
        lotes_libres.discard(lote)
        presupuesto_restante -= alcances[mejor]["costo"]
        cubiertos.update(alcances[mejor]["incidentes"])

    return sorted(elegidas)


def resumir_propuesta(instancia, alcances, estaciones):
    pesos = {tipo: datos["peso"] for tipo, datos in instancia.parametros["tipos"].items()}
    cubiertos = set()
    casos = {tipo: 0 for tipo in instancia.tipos}
    costo_total = 0

    for lote, tipo in sorted(estaciones):
        costo_total += alcances[(lote, tipo)]["costo"]
        for incidente in alcances[(lote, tipo)]["incidentes"]:
            if incidente not in cubiertos:
                cubiertos.add(incidente)
                casos[tipo] += 1

    valor = sum(casos[tipo] * pesos[tipo] for tipo in casos)
    return {
        "estaciones": sorted(estaciones),
        "costo_total": costo_total,
        "casos_cubiertos": casos,
        "valor": valor,
    }
