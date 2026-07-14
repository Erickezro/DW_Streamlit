import json
import unicodedata
from pathlib import Path

import streamlit as st
import plotly.express as px

from db import ejecutar_consulta

from sql.geografico import (
    query_accidentes_por_provincia,
    query_resumen_provincia,
    query_accidentes_por_canton,
    query_accidentes_por_zona,
)


@st.cache_data
def cargar_geojson():
    ruta = Path("data/ecuador_provincias.geojson")
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def normalizar_nombre(nombre):
    nombre = nombre.upper().strip()
    return unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii")


@st.cache_data
def obtener_geojson_mapa(df_provincias):
    geojson = cargar_geojson()

    nombres_db = {normalizar_nombre(p): p for p in df_provincias["provincia"]}

    features_filtrados = []
    for f in geojson["features"]:
        nombre_geo = f["properties"]["shapeName"]
        clave = normalizar_nombre(nombre_geo)
        if clave in nombres_db:
            f["properties"]["shapeName_db"] = nombres_db[clave]
            features_filtrados.append(f)

    return {"type": "FeatureCollection", "features": features_filtrados}


def filtros_globales():
    return {
        "anio": st.session_state.get("filtro_anio", "Todos"),
        "provincias": st.session_state.get("filtro_provincias", []),
        "cantones": st.session_state.get("filtro_cantones", []),
        "clases": st.session_state.get("filtro_clases", []),
        "causas": st.session_state.get("filtro_causas", []),
    }


st.title("🗺️ Análisis del Impacto Geográfico")

st.markdown(
    "Analiza cómo se distribuyen los accidentes a nivel geográfico. Esta vista te permite identificar las provincias, cantones y zonas con mayor siniestralidad para enfocar los esfuerzos de prevención."
)

st.divider()

filtros = filtros_globales()

if not filtros["provincias"]:
    st.warning("Seleccione al menos una provincia en los filtros globales de la barra lateral.")
    st.stop()

provincia = filtros["provincias"][0]

st.subheader(f"📊 Resumen de Impacto: {provincia}")
st.divider()

# ======================================================
# KPIs
# ======================================================

kpi = ejecutar_consulta(
    *query_resumen_provincia(
        provincia=provincia,
        anio=filtros["anio"],
        cantones=filtros["cantones"],
        clases=filtros["clases"],
        causas=filtros["causas"],
    )
).fillna(0)

fila_kpi = kpi.iloc[0] if not kpi.empty else {"accidentes": 0, "fallecidos": 0, "lesionados": 0, "victimas": 0}

anio_comparacion = None
if filtros["anio"] != "Todos":
    anio_comparacion = int(filtros["anio"]) - 1

kpi_prev = None
fila_prev = None
if anio_comparacion is not None:
    kpi_prev = ejecutar_consulta(
        *query_resumen_provincia(
            provincia=provincia,
            anio=str(anio_comparacion),
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    ).fillna(0)
    fila_prev = kpi_prev.iloc[0] if not kpi_prev.empty else {}


def formatear_delta(actual, prev):
    if prev is None or prev == 0:
        return None
    pct = ((actual - prev) / prev) * 100
    return f"{pct:+.1f}%"


delta_accidentes = formatear_delta(
    fila_kpi.get("accidentes", 0),
    fila_prev.get("accidentes") if fila_prev is not None else None
)
delta_fallecidos = formatear_delta(
    fila_kpi.get("fallecidos", 0),
    fila_prev.get("fallecidos") if fila_prev is not None else None
)
delta_lesionados = formatear_delta(
    fila_kpi.get("lesionados", 0),
    fila_prev.get("lesionados") if fila_prev is not None else None
)
delta_victimas = formatear_delta(
    fila_kpi.get("victimas", 0),
    fila_prev.get("victimas") if fila_prev is not None else None
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🚗 Accidentes",
    f"{int(fila_kpi['accidentes']):,}",
    delta=delta_accidentes,
    delta_color="inverse"
)

c2.metric(
    "☠️ Fallecidos",
    f"{int(fila_kpi['fallecidos']):,}",
    delta=delta_fallecidos,
    delta_color="inverse"
)

c3.metric(
    "🩹 Lesionados",
    f"{int(fila_kpi['lesionados']):,}",
    delta=delta_lesionados,
    delta_color="inverse"
)

c4.metric(
    "👥 Víctimas",
    f"{int(fila_kpi['victimas']):,}",
    delta=delta_victimas,
    delta_color="inverse"
)

st.caption(
    "Los deltas muestran la variación porcentual respecto al año anterior."
    if delta_accidentes is not None
    else "Seleccione un año específico en los filtros para ver la tendencia."
)

st.divider()

# ======================================================
# Provincias (Gráfico general filtrado)
# ======================================================

st.subheader("🌐 Visión General")

df_provincias_filtrado = ejecutar_consulta(
    *query_accidentes_por_provincia(
        anio=filtros["anio"],
        provincias=filtros["provincias"],
        cantones=filtros["cantones"],
        clases=filtros["clases"],
        causas=filtros["causas"],
    )
)

geojson_ec = obtener_geojson_mapa(df_provincias_filtrado)

fig = px.choropleth_mapbox(
    df_provincias_filtrado,
    geojson=geojson_ec,
    locations="provincia",
    featureidkey="properties.shapeName_db",
    color="accidentes",
    color_continuous_scale="OrRd",
    mapbox_style="carto-positron",
    zoom=5,
    center={"lat": -1.5, "lon": -78.5},
    opacity=0.7,
    labels={"accidentes": "Accidentes", "provincia": "Provincia"},
    title="Distribución geográfica de los accidentes"
)

fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

st.plotly_chart(fig, width="stretch")

# ======================================================
# Segunda fila (Cantones y Zonas de la provincia seleccionada)
# ======================================================

col1, col2 = st.columns(2)

# ---------------------
# Cantones
# ---------------------

with col1:
    st.subheader("🏙️ Análisis por Cantón")

    df_cantones = ejecutar_consulta(
        *query_accidentes_por_canton(
            provincia=provincia,
            anio=filtros["anio"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.bar(
        df_cantones,
        x="accidentes",
        y="canton",
        orientation="h",
        text="accidentes",
        title=f"¿Qué cantones presentan mayor siniestralidad en {provincia}?"
    )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

# ---------------------
# Zona
# ---------------------

with col2:
    st.subheader("🛣️ Análisis por Zona")

    df_zona = ejecutar_consulta(
        *query_accidentes_por_zona(
            provincia=provincia,
            anio=filtros["anio"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.pie(
        df_zona,
        names="zona",
        values="accidentes",
        title=f"¿Qué zonas (Urbana/Rural) tienen más accidentes en {provincia}?"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

st.divider()

st.subheader("Detalle por Cantón")

st.dataframe(
    df_cantones,
    width="stretch",
    hide_index=True
)

st.caption(
    f"Información geográfica correspondiente a {provincia}"
)
