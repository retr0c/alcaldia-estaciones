import argparse
import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from estaciones.cobertura import calcular_alcances
from estaciones.lectura import cargar_instancia


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
    serializable = {
        f"{lote}|{tipo}": datos for (lote, tipo), datos in alcances.items()
    }
    salida.parent.mkdir(exist_ok=True)
    with open(salida, "w", encoding="utf-8") as archivo:
        json.dump(serializable, archivo, ensure_ascii=False)


def main():
    lector = argparse.ArgumentParser()
    lector.add_argument("instancia", choices=["pequena", "comuna", "ciudad"])
    lector.add_argument("--detalle", action="store_true")
    argumentos = lector.parse_args()
    parte_1(argumentos.instancia, argumentos.detalle)


if __name__ == "__main__":
    main()