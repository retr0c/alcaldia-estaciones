import random
import time
from pathlib import Path

import pytest

from estaciones.cobertura import calcular_alcances
from estaciones.heuristicas import HEURISTICAS, construir_propuesta, resumir_propuesta
from estaciones.lectura import Instancia, cargar_instancia
from estaciones.optimo import mejor_propuesta

CARPETA_MANUALES = Path(__file__).resolve().parents[1] / "instancias_manuales"

CASOS_PARTE_1 = [
    {
        "entrada": {"instancia": "pequena", "lote": "L3", "tipo": "accidente"},
        "salida": {"costo": 2800, "incidentes_cubiertos": [1, 2, 4, 6]},
    },
    {
        "entrada": {"instancia": "pequena", "lote": "L2", "tipo": "hurto"},
        "salida": {"costo": 1500, "incidentes_cubiertos": [9, 10, 11, 12, 13]},
    },
]

CASOS_PARTE_2 = [
    {
        "entrada": {"instancia": "pequena", "heuristica": "base"},
        "salida": {
            "estaciones": [("L1", "incendio")],
            "costo_total": 5500,
            "casos_cubiertos": {"hurto": 0, "accidente": 0, "incendio": 3},
            "valor": 15,
        },
    },
    {
        "entrada": {"instancia": "comuna", "heuristica": "base"},
        "salida": {
            "estaciones": [
                ("L05", "accidente"), ("L06", "hurto"), ("L08", "accidente"),
                ("L09", "incendio"), ("L13", "hurto"), ("L14", "hurto"),
                ("L15", "accidente"),
            ],
            "costo_total": 11950,
            "casos_cubiertos": {"hurto": 486, "accidente": 296, "incendio": 31},
            "valor": 1529,
        },
    },
]

CASO_PARTE_3 = {
    "entrada": {"instancia": "pequena"},
    "salida": {
        "estaciones": [("L1", "hurto"), ("L3", "accidente"), ("L4", "hurto")],
        "costo_total": 5400,
        "casos_cubiertos": {"hurto": 8, "accidente": 4, "incendio": 0},
        "valor": 20,
    },
}

TIPOS = ["hurto", "accidente", "incendio"]
COSTOS_BASE = {"hurto": 1000, "accidente": 2000, "incendio": 5000}


def resolver(nombre, heuristica, carpeta=None):
    instancia = (
        cargar_instancia(nombre) if carpeta is None
        else cargar_instancia(nombre, carpeta_datos=carpeta)
    )
    alcances = calcular_alcances(instancia)
    estaciones = construir_propuesta(instancia, alcances, HEURISTICAS[heuristica])
    return instancia, alcances, resumir_propuesta(instancia, alcances, estaciones)


def valor_por_fuerza_bruta(instancia, alcances):
    lotes = [codigo for codigo, _, _ in instancia.lotes]
    mejor = [0]

    def recorrer(posicion, elegidas, gastado):
        if posicion == len(lotes):
            valor = resumir_propuesta(instancia, alcances, elegidas)["valor"]
            mejor[0] = max(mejor[0], valor)
            return
        recorrer(posicion + 1, elegidas, gastado)
        for tipo in instancia.tipos:
            costo = alcances[(lotes[posicion], tipo)]["costo"]
            if gastado + costo <= instancia.presupuesto:
                elegidas.append((lotes[posicion], tipo))
                recorrer(posicion + 1, elegidas, gastado + costo)
                elegidas.pop()

    recorrer(0, [], 0)
    return mejor[0]


def instancia_aleatoria(generador):
    incidentes = [
        (i + 1, 0, generador.choice(TIPOS)) for i in range(generador.randint(3, 25))
    ]
    lotes = [
        (f"L{j + 1}", 0, generador.choice([0.8, 1.0, 1.2, 1.5]))
        for j in range(generador.randint(2, 7))
    ]
    parametros = {
        "presupuesto_millones": generador.choice([2000, 3000, 4000, 6000, 8000, 12000]),
        "tipos": {
            "hurto": {"costo_base": 1000, "radio_m": 1000, "peso": 1},
            "accidente": {"costo_base": 2000, "radio_m": 2000, "peso": 3},
            "incendio": {"costo_base": 5000, "radio_m": 3000, "peso": 5},
        },
    }
    instancia = Instancia("aleatoria", {}, {}, lotes, incidentes, parametros)

    alcances = {}
    for lote, _, factor in lotes:
        for tipo in TIPOS:
            cubiertos = [
                i for i, _, t in incidentes if t == tipo and generador.random() < 0.4
            ]
            alcances[(lote, tipo)] = {
                "costo": round(COSTOS_BASE[tipo] * factor),
                "incidentes": cubiertos,
            }
    return instancia, alcances


@pytest.mark.parametrize("caso", CASOS_PARTE_1)
def test_parte_1_casos_del_enunciado(caso):
    entrada = caso["entrada"]
    alcances = calcular_alcances(cargar_instancia(entrada["instancia"]))
    resultado = alcances[(entrada["lote"], entrada["tipo"])]
    assert resultado["costo"] == caso["salida"]["costo"]
    assert resultado["incidentes"] == caso["salida"]["incidentes_cubiertos"]


def test_parte_1_ciudad_en_menos_de_un_minuto():
    instancia = cargar_instancia("ciudad")
    inicio = time.perf_counter()
    alcances = calcular_alcances(instancia)
    assert time.perf_counter() - inicio < 60
    assert len(alcances) == len(instancia.lotes) * len(instancia.tipos)


@pytest.mark.parametrize("caso", CASOS_PARTE_2)
def test_parte_2_heuristica_base_casos_del_enunciado(caso):
    entrada = caso["entrada"]
    _, _, resumen = resolver(entrada["instancia"], entrada["heuristica"])
    assert resumen == caso["salida"]


def test_parte_2_heuristica_propia_supera_a_la_base_en_alguna_instancia():
    mejoras = 0
    for nombre in ("pequena", "comuna", "ciudad"):
        valor_base = resolver(nombre, "base")[2]["valor"]
        valor_propia = resolver(nombre, "eficiencia")[2]["valor"]
        if valor_propia > valor_base:
            mejoras += 1
    assert mejoras >= 1


def test_parte_2_contraejemplo_de_la_base():
    instancia, alcances, resumen = resolver(
        "contraejemplo_base", "base", CARPETA_MANUALES
    )
    assert resumen["valor"] == 15
    mejor = resumir_propuesta(
        instancia, alcances, [("L1", "accidente"), ("L2", "accidente"), ("L3", "accidente")]
    )
    assert mejor["costo_total"] <= instancia.presupuesto
    assert mejor["valor"] == 18


def test_parte_2_contraejemplo_de_la_eficiencia():
    instancia, alcances, resumen = resolver(
        "contraejemplo_eficiencia", "eficiencia", CARPETA_MANUALES
    )
    assert resumen["valor"] == 4
    mejor = resumir_propuesta(instancia, alcances, [("L2", "accidente")])
    assert mejor["costo_total"] <= instancia.presupuesto
    assert mejor["valor"] == 6


def test_parte_3_caso_del_enunciado():
    instancia = cargar_instancia("pequena")
    alcances = calcular_alcances(instancia)
    estaciones, _ = mejor_propuesta(instancia, alcances)
    assert resumir_propuesta(instancia, alcances, estaciones) == CASO_PARTE_3["salida"]


@pytest.mark.parametrize(
    "nombre, carpeta",
    [
        ("pequena", None),
        ("contraejemplo_base", CARPETA_MANUALES),
        ("contraejemplo_eficiencia", CARPETA_MANUALES),
    ],
)
def test_parte_3_optimo_coincide_con_fuerza_bruta(nombre, carpeta):
    instancia = (
        cargar_instancia(nombre) if carpeta is None
        else cargar_instancia(nombre, carpeta_datos=carpeta)
    )
    alcances = calcular_alcances(instancia)
    estaciones, _ = mejor_propuesta(instancia, alcances)
    resumen = resumir_propuesta(instancia, alcances, estaciones)
    assert resumen["costo_total"] <= instancia.presupuesto
    assert resumen["valor"] == valor_por_fuerza_bruta(instancia, alcances)


def test_parte_3_optimo_coincide_con_fuerza_bruta_en_instancias_aleatorias():
    generador = random.Random(7)
    for _ in range(100):
        instancia, alcances = instancia_aleatoria(generador)
        estaciones, _ = mejor_propuesta(instancia, alcances)
        resumen = resumir_propuesta(instancia, alcances, estaciones)
        assert resumen["costo_total"] <= instancia.presupuesto
        assert resumen["valor"] == valor_por_fuerza_bruta(instancia, alcances)


def test_parte_3_comuna_supera_a_las_heuristicas():
    instancia = cargar_instancia("comuna")
    alcances = calcular_alcances(instancia)
    estaciones, _ = mejor_propuesta(instancia, alcances)
    resumen = resumir_propuesta(instancia, alcances, estaciones)
    assert resumen["costo_total"] <= instancia.presupuesto
    assert resumen["valor"] == 1574
    for criterio in HEURISTICAS.values():
        propuesta = construir_propuesta(instancia, alcances, criterio)
        assert resumen["valor"] >= resumir_propuesta(instancia, alcances, propuesta)["valor"]