# Instancias manuales de la Parte 2

Cada instancia usa los mismos parámetros del enunciado (costos, radios y pesos) y cambia solo el presupuesto.

## Heurística base: `contraejemplo_base`

Red de 4 nodos en línea con tramos de 2100 m. Lotes L1, L2 y L3 en los nodos 0, 1 y 2, con factor de zona 1.0. Presupuesto: 6.000.

Incidentes: 2 accidentes en cada uno de los nodos 0, 1 y 2, y 3 incendios en el nodo 3.

Como los tramos miden 2100 m, un CAI o una estación de tránsito solo cubre el nodo donde está. Solo el lote L3 alcanza el nodo 3 con una estación de bomberos (radio de 3000 m).

- La base elige primero L3-incendio: cubre 3 incendios y agrega 15, frente a 6 de cualquier estación de tránsito. Cuesta 5.000 y deja 1.000, que no alcanzan para otra estación que cubra algo. Valor final: 15.
- La mejor propuesta es L1, L2 y L3 con estación de tránsito: cuesta 6.000 y cubre 6 accidentes. Valor: 18.

La decisión que la lleva por mal camino es mirar solo el valor que agrega la estación en ese paso y no lo que cuesta. Gasta casi todo el presupuesto en una sola estación y pierde la combinación de tres estaciones más baratas que juntas valen más.

## Heurística de eficiencia: `contraejemplo_eficiencia`

Red de 2 nodos con un tramo de 2100 m. Lotes L1 y L2 en los nodos 0 y 1, con factor de zona 1.0. Presupuesto: 2.000.

Incidentes: 4 hurtos en el nodo 0 y 2 accidentes en el nodo 1.

- La eficiencia elige primero L1-hurto: agrega 4 y cuesta 1.000, es decir 0,004 por millón, frente a 0,003 de L2-accidente (agrega 6 y cuesta 2.000). Quedan 1.000, que no alcanzan para L2-accidente ni cubren nada más. Valor final: 4.
- La mejor propuesta es L2-accidente: cuesta 2.000 y cubre 2 accidentes. Valor: 6.

La decisión que la lleva por mal camino es preferir la estación con mejor valor por millón aunque sea pequeña. La compra barata deja un presupuesto sobrante que ya no sirve para la estación grande que valía más.