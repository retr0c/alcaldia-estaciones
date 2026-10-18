import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

CARPETA_DATOS = Path(__file__).resolve().parents[2] / "datos"


@dataclass
class Instancia:
    nombre: str
    coordenadas: dict
    adyacencia: dict
    lotes: list
    incidentes: list
    parametros: dict

    @property
    def tipos(self):
        return list(self.parametros["tipos"])

    @property
    def presupuesto(self):
        return self.parametros["presupuesto_millones"]


def _leer_csv(ruta):
    with open(ruta, newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def cargar_instancia(nombre, carpeta_datos=CARPETA_DATOS):
    carpeta = Path(carpeta_datos) / nombre

    coordenadas = {}
    for fila in _leer_csv(carpeta / "nodos.csv"):
        coordenadas[int(fila["id"])] = (float(fila["lat"]), float(fila["lon"]))

    adyacencia = defaultdict(list)
    for fila in _leer_csv(carpeta / "aristas.csv"):
        adyacencia[int(fila["origen"])].append(
            (int(fila["destino"]), float(fila["longitud_m"]))
        )

    lotes = [
        (fila["lote"], int(fila["nodo"]), float(fila["factor_zona"]))
        for fila in _leer_csv(carpeta / "lotes.csv")
    ]

    incidentes = [
        (int(fila["id"]), int(fila["nodo"]), fila["tipo"])
        for fila in _leer_csv(carpeta / "incidentes.csv")
    ]

    with open(carpeta / "parametros.json", encoding="utf-8") as archivo:
        parametros = json.load(archivo)

    return Instancia(
        nombre=nombre,
        coordenadas=coordenadas,
        adyacencia=adyacencia,
        lotes=lotes,
        incidentes=incidentes,
        parametros=parametros,
    )