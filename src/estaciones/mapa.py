from pathlib import Path

import folium

COLOR_ESTACION = {"hurto": "blue", "accidente": "orange", "incendio": "red"}
COLOR_LEYENDA = {"hurto": "#38a9dc", "accidente": "#f69730", "incendio": "#d43e2a"}
ICONO_ESTACION = {"hurto": "shield", "accidente": "car", "incendio": "fire"}
FONDO_URL = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
)
COLOR_CUBIERTO = "#1a9850"
COLOR_NO_CUBIERTO = "#333333"


def incidentes_cubiertos(alcances, estaciones):
    cubiertos = set()
    for estacion in estaciones:
        cubiertos.update(alcances[estacion]["incidentes"])
    return cubiertos


def _leyenda(titulo, instancia, estaciones_construidas, cubiertos):
    tipos = instancia.parametros["tipos"]
    filas = []
    for tipo, datos in tipos.items():
        color = COLOR_LEYENDA.get(tipo, "#888888")
        filas.append(
            f'<div><span style="background:{color};display:inline-block;width:12px;'
            f'height:12px;border-radius:50%;margin-right:6px"></span>{datos["estacion"]}</div>'
        )
    filas.append(
        f'<div><span style="background:{COLOR_CUBIERTO};display:inline-block;width:10px;'
        f'height:10px;border-radius:50%;margin-right:8px"></span>Incidente cubierto</div>'
    )
    filas.append(
        f'<div><span style="background:{COLOR_NO_CUBIERTO};display:inline-block;width:10px;'
        f'height:10px;border-radius:50%;margin-right:8px"></span>Incidente no cubierto</div>'
    )
    filas.append(
        '<div><span style="background:#fff;border:2px solid #777;display:inline-block;'
        'width:10px;height:10px;border-radius:50%;margin-right:8px"></span>Lote no usado</div>'
    )
    total = len(instancia.incidentes)
    resumen = (
        f"{len(estaciones_construidas)} estaciones &middot; "
        f"{len(cubiertos)} de {total} incidentes cubiertos"
    )
    html = (
        '<div style="position:fixed;bottom:24px;left:24px;z-index:9999;background:#fff;'
        'color:#222;padding:10px 14px;border:1px solid #999;border-radius:6px;'
        'font:13px/1.5 sans-serif;box-shadow:0 1px 4px rgba(0,0,0,.3)">'
        f'<b>{titulo}</b><div style="margin-bottom:6px">{resumen}</div>'
        + "".join(filas)
        + "</div>"
    )
    return folium.Element(html)


def crear_mapa(instancia, alcances, estaciones, ruta_salida, titulo):
    cubiertos = incidentes_cubiertos(alcances, estaciones)
    nodo_de_lote = {codigo: nodo for codigo, nodo, _ in instancia.lotes}
    lotes_usados = {lote for lote, _ in estaciones}

    latitudes = [lat for lat, _ in instancia.coordenadas.values()]
    longitudes = [lon for _, lon in instancia.coordenadas.values()]
    mapa = folium.Map(
    location=[sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)],
    tiles=None,
    )
    folium.TileLayer(
        tiles=FONDO_URL,
        attr="Tiles &copy; Esri",
        name="Mapa de calles",
        max_zoom=19,
    ).add_to(mapa)
    mapa.fit_bounds([[min(latitudes), min(longitudes)], [max(latitudes), max(longitudes)]])

    grupo_no_cubiertos = folium.FeatureGroup(name="Incidentes no cubiertos")
    grupo_cubiertos = folium.FeatureGroup(name="Incidentes cubiertos")
    grupo_lotes = folium.FeatureGroup(name="Lotes no usados")
    grupo_estaciones = folium.FeatureGroup(name="Estaciones construidas")

    for id_incidente, nodo, tipo in instancia.incidentes:
        cubierto = id_incidente in cubiertos
        folium.CircleMarker(
            location=instancia.coordenadas[nodo],
            radius=3,
            color=COLOR_CUBIERTO if cubierto else COLOR_NO_CUBIERTO,
            weight=1,
            fill=True,
            fill_color=COLOR_CUBIERTO if cubierto else COLOR_NO_CUBIERTO,
            fill_opacity=0.7,
            tooltip=f"Incidente {id_incidente} ({tipo}): {'cubierto' if cubierto else 'no cubierto'}",
        ).add_to(grupo_cubiertos if cubierto else grupo_no_cubiertos)

    for codigo, nodo, factor in instancia.lotes:
        if codigo in lotes_usados:
            continue
        folium.CircleMarker(
            location=instancia.coordenadas[nodo],
            radius=6,
            color="#777777",
            weight=2,
            fill=True,
            fill_color="#ffffff",
            fill_opacity=1,
            tooltip=f"Lote {codigo} (no usado, factor de zona {factor})",
        ).add_to(grupo_lotes)

    for lote, tipo in sorted(estaciones):
        datos = alcances[(lote, tipo)]
        nombre = instancia.parametros["tipos"][tipo]["estacion"]
        folium.Marker(
            location=instancia.coordenadas[nodo_de_lote[lote]],
            icon=folium.Icon(
                color=COLOR_ESTACION.get(tipo, "gray"),
                icon=ICONO_ESTACION.get(tipo, "info-sign"),
                prefix="fa",
            ),
            tooltip=f"{lote}: {nombre}",
            popup=folium.Popup(
                f"<b>{lote}</b><br>{nombre}<br>Costo: {datos['costo']} millones"
                f"<br>Cubre {len(datos['incidentes'])} incidentes",
                max_width=260,
            ),
        ).add_to(grupo_estaciones)

    for grupo in (grupo_no_cubiertos, grupo_cubiertos, grupo_lotes, grupo_estaciones):
        grupo.add_to(mapa)
    folium.LayerControl(collapsed=False).add_to(mapa)
    mapa.get_root().html.add_child(_leyenda(titulo, instancia, estaciones, cubiertos))

    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    mapa.save(str(ruta))
    return ruta