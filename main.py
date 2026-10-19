import argparse
import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from estaciones.cobertura import calcular_alcances
from estaciones.heuristicas import HEURISTICAS, construir_propuesta, resumir_propuesta
from estaciones.informe import parrafo_justificacion, tabla_estaciones
from estaciones.lectura import cargar_instancia
from estaciones.mapa import crear_mapa
from estaciones.optimo import espacio_de_busqueda, mejor_propuesta

INSTANCIAS = ["pequena", "comuna", "ciudad"]


def imprimir_resumen(resumen):
    estaciones = ", ".join(f"{lote}-{tipo}" for lote, tipo in resumen["estaciones"])
    print("  estaciones:", estaciones)
    print("  costo total:", resumen["costo_total"])
    print("  casos cubiertos:", resumen["casos_cubiertos"])
    print("  valor:", resumen["valor"])


def parte_1(nombre, detalle):
    instancia = cargar_instancia(nombre)

    inicio = time.perf_counter()
    alcances = calcular_alcances(instancia)
    segundos = time.perf_counter() - inicio

    print(f"Instancia {nombre}: {len(instancia.lotes)} lotes x {len(instancia.tipos)} tipos")
    print(f"Tiempo de cálculo: {segundos:.2f} s\n")
    print(f"{'lote':<6}{'tipo':<11}{'costo':>7}{'cubre':>7}")
    for (lote, tipo), datos in alcances.items():
        linea = f"{lote:<6}{tipo:<11}{datos['costo']:>7}{len(datos['incidentes']):>7}"
        if detalle:
            linea += f"  {datos['incidentes']}"
        print(linea)

    salida = RAIZ / "resultados" / f"{nombre}_parte1.json"
    serializable = {f"{lote}|{tipo}": datos for (lote, tipo), datos in alcances.items()}
    salida.parent.mkdir(exist_ok=True)
    with open(salida, "w", encoding="utf-8") as archivo:
        json.dump(serializable, archivo, ensure_ascii=False)


def parte_2(nombre):
    instancia = cargar_instancia(nombre)
    alcances = calcular_alcances(instancia)

    print(f"Instancia {nombre} (presupuesto {instancia.presupuesto})")
    for etiqueta, criterio in HEURISTICAS.items():
        inicio = time.perf_counter()
        estaciones = construir_propuesta(instancia, alcances, criterio)
        segundos = time.perf_counter() - inicio
        print(f"\nHeurística {etiqueta} ({segundos:.3f} s)")
        imprimir_resumen(resumir_propuesta(instancia, alcances, estaciones))


def explicar_espacio_de_busqueda(instancia):
    espacio = espacio_de_busqueda(instancia)
    print(f"Instancia {instancia.nombre}: no se reporta la mejor propuesta posible.")
    print(
        f"  Cada uno de los {espacio['lotes']} lotes admite {espacio['opciones_por_lote']} "
        "opciones (vacío, CAI, tránsito o bomberos)."
    )
    print(
        f"  Combinaciones: {espacio['opciones_por_lote']}^{espacio['lotes']} "
        f"= {espacio['combinaciones']:.2e}"
    )
    print(f"  A 1e9 propuestas por segundo: {espacio['anios']:.2e} años.")


def parte_3(nombre):
    instancia = cargar_instancia(nombre)
    if nombre == "ciudad":
        explicar_espacio_de_busqueda(instancia)
        return

    alcances = calcular_alcances(instancia)
    inicio = time.perf_counter()
    estaciones, nodos = mejor_propuesta(instancia, alcances)
    segundos = time.perf_counter() - inicio

    print(f"Instancia {nombre} (presupuesto {instancia.presupuesto})")
    print(f"Mejor propuesta posible ({segundos:.2f} s, {nodos} nodos explorados)")
    imprimir_resumen(resumir_propuesta(instancia, alcances, estaciones))


def entregar_propuesta(instancia, alcances, resumenes, elegida, es_optima, nombre_archivo, titulo):
    resumen = resumenes[elegida]
    carpeta = RAIZ / "resultados"

    ruta_mapa = crear_mapa(
        instancia, alcances, resumen["estaciones"], carpeta / f"mapa_{nombre_archivo}.html", titulo
    )
    tabla = tabla_estaciones(instancia, alcances, resumen)
    parrafo = parrafo_justificacion(instancia, resumenes, elegida, es_optima)

    contenido = f"# {titulo}\n\n## Estaciones construidas\n\n{tabla}\n\n## Justificación\n\n{parrafo}\n"
    ruta_informe = carpeta / f"propuesta_{nombre_archivo}.md"
    ruta_informe.write_text(contenido, encoding="utf-8")

    print(contenido)
    print(f"Mapa: {ruta_mapa}")
    print(f"Informe: {ruta_informe}\n")


def parte_4():
    instancia = cargar_instancia("ciudad")
    alcances = calcular_alcances(instancia)
    resumenes = {}
    for etiqueta, criterio in HEURISTICAS.items():
        estaciones = construir_propuesta(instancia, alcances, criterio)
        resumenes[etiqueta] = resumir_propuesta(instancia, alcances, estaciones)
    elegida = max(resumenes, key=lambda etiqueta: resumenes[etiqueta]["valor"])
    entregar_propuesta(
        instancia, alcances, resumenes, elegida, False, "ciudad",
        "Propuesta para la instancia ciudad",
    )

    instancia = cargar_instancia("comuna")
    alcances = calcular_alcances(instancia)
    resumenes = {}
    for etiqueta, criterio in HEURISTICAS.items():
        estaciones = construir_propuesta(instancia, alcances, criterio)
        resumenes[etiqueta] = resumir_propuesta(instancia, alcances, estaciones)
    estaciones, _ = mejor_propuesta(instancia, alcances)
    resumenes["optima"] = resumir_propuesta(instancia, alcances, estaciones)
    entregar_propuesta(
        instancia, alcances, resumenes, "optima", True, "comuna_optima",
        "Mejor propuesta posible para la instancia comuna",
    )


def tabla_comparativa():
    filas = []
    for nombre in INSTANCIAS:
        instancia = cargar_instancia(nombre)
        alcances = calcular_alcances(instancia)
        fila = {"instancia": nombre}

        for etiqueta, criterio in HEURISTICAS.items():
            inicio = time.perf_counter()
            estaciones = construir_propuesta(instancia, alcances, criterio)
            fila[etiqueta] = (
                resumir_propuesta(instancia, alcances, estaciones)["valor"],
                time.perf_counter() - inicio,
            )

        if nombre == "ciudad":
            fila["optimo"] = None
        else:
            inicio = time.perf_counter()
            estaciones, _ = mejor_propuesta(instancia, alcances)
            fila["optimo"] = (
                resumir_propuesta(instancia, alcances, estaciones)["valor"],
                time.perf_counter() - inicio,
            )
        filas.append(fila)

    lineas = [
        "| Instancia | Base: valor | Base: tiempo (s) | Eficiencia: valor | Eficiencia: tiempo (s) "
        "| Óptimo: valor | Óptimo: tiempo (s) |",
        "|---|---|---|---|---|---|---|",
    ]
    for fila in filas:
        optimo = "no calculado" if fila["optimo"] is None else f"{fila['optimo'][0]}"
        tiempo_optimo = "-" if fila["optimo"] is None else f"{fila['optimo'][1]:.2f}"
        lineas.append(
            f"| {fila['instancia']} | {fila['base'][0]} | {fila['base'][1]:.4f} "
            f"| {fila['eficiencia'][0]} | {fila['eficiencia'][1]:.4f} "
            f"| {optimo} | {tiempo_optimo} |"
        )
    tabla = "\n".join(lineas)
    print(tabla)
    print("\nLos tiempos no incluyen el cálculo de alcances de la Parte 1.")

    salida = RAIZ / "resultados" / "tabla_comparativa.md"
    salida.parent.mkdir(exist_ok=True)
    salida.write_text(tabla + "\n", encoding="utf-8")


def main():
    lector = argparse.ArgumentParser()
    lector.add_argument("instancia", nargs="?", choices=INSTANCIAS)
    lector.add_argument("--parte", type=int, choices=[1, 2, 3, 4], default=1)
    lector.add_argument("--detalle", action="store_true")
    lector.add_argument("--tabla", action="store_true")
    argumentos = lector.parse_args()

    if argumentos.tabla:
        tabla_comparativa()
        return
    if argumentos.parte == 4:
        parte_4()
        return
    if argumentos.instancia is None:
        lector.error("indica la instancia (pequena, comuna o ciudad) o usa --tabla")

    if argumentos.parte == 1:
        parte_1(argumentos.instancia, argumentos.detalle)
    elif argumentos.parte == 2:
        parte_2(argumentos.instancia)
    else:
        parte_3(argumentos.instancia)


if __name__ == "__main__":
    main()