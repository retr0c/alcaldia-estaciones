import time

import pytest

from estaciones.cobertura import calcular_alcances
from estaciones.lectura import cargar_instancia

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