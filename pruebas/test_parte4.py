import re

from estaciones.cobertura import calcular_alcances
from estaciones.heuristicas import HEURISTICAS, construir_propuesta, resumir_propuesta
from estaciones.informe import parrafo_justificacion, tabla_estaciones
from estaciones.lectura import cargar_instancia
from estaciones.mapa import crear_mapa, incidentes_cubiertos
from estaciones.optimo import mejor_propuesta


def propuesta_optima_pequena():
    instancia = cargar_instancia("pequena")
    alcances = calcular_alcances(instancia)
    estaciones, _ = mejor_propuesta(instancia, alcances)
    return instancia, alcances, estaciones, resumir_propuesta(instancia, alcances, estaciones)


def test_parte_4_mapa_dibuja_cada_elemento(tmp_path):
    instancia, alcances, estaciones, _ = propuesta_optima_pequena()
    ruta = crear_mapa(instancia, alcances, estaciones, tmp_path / "mapa.html", "Prueba")
    html = ruta.read_text(encoding="utf-8")

    lotes_usados = {lote for lote, _ in estaciones}
    lotes_libres = [c for c, _, _ in instancia.lotes if c not in lotes_usados]

    assert html.count("L.marker(") == len(estaciones)
    assert html.count("L.circleMarker(") == len(instancia.incidentes) + len(lotes_libres)


def test_parte_4_incidentes_cubiertos_coinciden_con_el_resumen():
    instancia, alcances, estaciones, resumen = propuesta_optima_pequena()
    cubiertos = incidentes_cubiertos(alcances, estaciones)
    assert len(cubiertos) == sum(resumen["casos_cubiertos"].values())


def test_parte_4_tabla_incluye_totales():
    instancia, alcances, _, resumen = propuesta_optima_pequena()
    tabla = tabla_estaciones(instancia, alcances, resumen)
    assert f"Costo total: {resumen['costo_total']} millones" in tabla
    assert f"Valor de la propuesta: {resumen['valor']}" in tabla
    assert len(re.findall(r"^\| L\d", tabla, re.MULTILINE)) == len(resumen["estaciones"])


def test_parte_4_parrafo_menciona_las_cifras_de_la_propuesta():
    instancia, alcances, _, resumen_optimo = propuesta_optima_pequena()
    resumenes = {"optima": resumen_optimo}
    for etiqueta, criterio in HEURISTICAS.items():
        estaciones = construir_propuesta(instancia, alcances, criterio)
        resumenes[etiqueta] = resumir_propuesta(instancia, alcances, estaciones)

    parrafo = parrafo_justificacion(instancia, resumenes, "optima", es_optima=True)
    assert str(resumen_optimo["valor"]) in parrafo
    assert str(resumen_optimo["costo_total"]) in parrafo
    assert "garantiza" in parrafo