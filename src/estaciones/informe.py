def tabla_estaciones(instancia, alcances, resumen):
    lineas = [
        "| Lote | Tipo | Estación | Costo (millones) | Casos que cubre |",
        "|---|---|---|---|---|",
    ]
    for lote, tipo in resumen["estaciones"]:
        datos = alcances[(lote, tipo)]
        nombre = instancia.parametros["tipos"][tipo]["estacion"]
        lineas.append(
            f"| {lote} | {tipo} | {nombre} | {datos['costo']} | {len(datos['incidentes'])} |"
        )

    casos = resumen["casos_cubiertos"]
    lineas.append("")
    lineas.append(
        f"- Costo total: {resumen['costo_total']} millones, frente a un presupuesto de "
        f"{instancia.presupuesto} millones."
    )
    lineas.append(
        f"- Casos cubiertos: {casos['hurto']} hurtos, {casos['accidente']} accidentes "
        f"y {casos['incendio']} incendios."
    )
    lineas.append(f"- Valor de la propuesta: {resumen['valor']}.")
    return "\n".join(lineas)


def _diferencia_de_casos(elegida, otra):
    return ", ".join(
        f"{tipo} {elegida['casos_cubiertos'][tipo] - otra['casos_cubiertos'][tipo]:+d}"
        for tipo in elegida["casos_cubiertos"]
    )


NOMBRES_PROPUESTA = {
    "base": "la propuesta de la heurística base",
    "eficiencia": "la propuesta de la heurística de eficiencia",
    "optima": "la mejor propuesta posible",
}


def _nombre(etiqueta):
    return NOMBRES_PROPUESTA.get(etiqueta, f"la propuesta «{etiqueta}»")


def parrafo_justificacion(instancia, resumenes, elegida, es_optima=False):
    resumen = resumenes[elegida]
    casos = resumen["casos_cubiertos"]
    uso = 100 * resumen["costo_total"] / instancia.presupuesto

    texto = (
        f"Para la instancia {instancia.nombre} se recomienda {_nombre(elegida)}: "
        f"alcanza un valor de {resumen['valor']}, el más alto entre las alternativas obtenidas, "
        f"con un costo de {resumen['costo_total']} millones sobre un presupuesto de "
        f"{instancia.presupuesto} ({uso:.1f} % utilizado), y cubre {casos['hurto']} hurtos, "
        f"{casos['accidente']} accidentes y {casos['incendio']} incendios."
    )

    for etiqueta, otra in resumenes.items():
        if etiqueta == elegida:
            continue
        texto += (
            f" Frente a {_nombre(etiqueta)} (valor {otra['valor']}) suma "
            f"{resumen['valor'] - otra['valor']} puntos, con esta diferencia en casos cubiertos: "
            f"{_diferencia_de_casos(resumen, otra)}."
        )

    if es_optima:
        texto += (
            " Además, la búsqueda exacta garantiza que ninguna propuesta que respete "
            "el presupuesto alcanza un valor mayor."
        )
    else:
        texto += (
            " No se garantiza que sea la mejor propuesta posible: en esta instancia el espacio "
            "de búsqueda es demasiado grande para recorrerlo por completo."
        )
    return texto