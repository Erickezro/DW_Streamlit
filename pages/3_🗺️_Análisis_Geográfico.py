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
from sql.temporal import query_accidentes_por_mes
from utils.insights import (
    interpret_kpis_provincia,
    interpret_causas,
    interpret_zonas,
    interpret_meses,
    sabias_que,
    recomendacion_para_provincia,
    recomendacion_aleatoria,
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


@st.cache_data(ttl=300)
def _causas_por_provincia(provincia, anio=None, cantones=None, clases=None, causas=None):
    from sql.dashboard import query_top_causas
    return ejecutar_consulta(
        *query_top_causas(
            anio=anio,
            provincias=[provincia],
            cantones=cantones,
            clases=clases,
            causas=causas,
        )
    )


def filtros_globales():
    return {
        "anio": st.session_state.get("filtro_anio", "Todos"),
        "provincias": st.session_state.get("filtro_provincias", []),
        "cantones": st.session_state.get("filtro_cantones", []),
        "clases": st.session_state.get("filtro_clases", []),
        "causas": st.session_state.get("filtro_causas", []),
    }


st.title("🗺️ Análisis del Impacto Geográfico")

with st.container(border=True):
    st.markdown(
        """
        La geografía influye en la siniestralidad vial. Cada provincia tiene características
        distintas: densidad de tráfico, tipo de vías, condiciones climáticas y factores culturales
        que determinan los patrones de accidentes.

        **Selecciona una provincia en los filtros de la barra lateral** para explorar su perfil
        completo de seguridad vial.
        """
    )

st.divider()

filtros = filtros_globales()

if not filtros["provincias"]:
    st.info(
        "👈 Para comenzar, selecciona al menos una provincia en los filtros "
        "**Provincia** de la barra lateral. Luego podrás ver su análisis detallado."
    )

    # Mapa general
    st.subheader("🌐 Distribución nacional")
    df_todas = ejecutar_consulta(
        *query_accidentes_por_provincia(
            anio=filtros["anio"],
            provincias=[],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )
    if not df_todas.empty:
        geojson_ec = obtener_geojson_mapa(df_todas)
        fig = px.choropleth_mapbox(
            df_todas,
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
            title="Distribución nacional de accidentes — selecciona una provincia",
        )
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(fig, width="stretch")
    st.stop()

provincia = filtros["provincias"][0]

# ======================================================
# TARJETA DE RESUMEN DE LA PROVINCIA
# ======================================================
st.subheader(f"📍 Perfil de Seguridad Vial: {provincia}")

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

c1.metric("🚗 Accidentes", f"{int(fila_kpi['accidentes']):,}", delta=delta_accidentes, delta_color="inverse")
c2.metric("☠️ Fallecidos", f"{int(fila_kpi['fallecidos']):,}", delta=delta_fallecidos, delta_color="inverse")
c3.metric("🩹 Lesionados", f"{int(fila_kpi['lesionados']):,}", delta=delta_lesionados, delta_color="inverse")
c4.metric("👥 Víctimas", f"{int(fila_kpi['victimas']):,}", delta=delta_victimas, delta_color="inverse")

st.caption(
    "Los deltas muestran la variación porcentual respecto al año anterior."
    if delta_accidentes is not None
    else "Selecciona un año específico para ver la tendencia."
)

if fila_kpi.get("accidentes", 0) > 0:
    with st.container(border=True):
        st.markdown("**📝 Interpretación**")
        st.markdown(
            interpret_kpis_provincia(
                provincia=provincia,
                accidentes=fila_kpi["accidentes"],
                fallecidos=fila_kpi["fallecidos"],
                lesionados=fila_kpi["lesionados"],
                delta_acc=delta_accidentes,
            )
        )

st.divider()

# ======================================================
# MAPA + DISTRIBUCIÓN ESTACIONAL
# ======================================================
st.subheader("🌐 Distribución y estacionalidad")

col_mapa, col_meses = st.columns([1.5, 1])

with col_mapa:
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
        zoom=5.5,
        center={"lat": -1.5, "lon": -78.5},
        opacity=0.7,
        labels={"accidentes": "Accidentes", "provincia": "Provincia"},
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=400)
    st.plotly_chart(fig, width="stretch")

with col_meses:
    st.markdown("**📅 Accidentes por mes**")
    df_mes_prov = ejecutar_consulta(
        *query_accidentes_por_mes(
            anio=filtros["anio"],
            provincias=[provincia],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )
    if not df_mes_prov.empty:
        fig_mes = px.line(
            df_mes_prov,
            x="mes",
            y="accidentes",
            markers=True,
            color_discrete_sequence=["#e74c3c"],
        )
        fig_mes.update_layout(height=300, margin={"r": 0, "t": 20, "l": 0, "b": 0})
        st.plotly_chart(fig_mes, width="stretch")

        with st.container(border=True):
            st.markdown("**📝 Interpretación**")
            st.markdown(interpret_meses(df_mes_prov))
    else:
        st.info("No hay datos mensuales para esta provincia.")

st.divider()

# ======================================================
# CAUSAS PRINCIPALES DE LA PROVINCIA
# ======================================================
st.subheader(f"⚠️ Principales causas en {provincia}")

df_causas_prov = _causas_por_provincia(
    provincia=provincia,
    anio=filtros["anio"],
    cantones=filtros["cantones"],
    clases=filtros["clases"],
    causas=filtros["causas"],
)

if not df_causas_prov.empty:
    fig = px.bar(
        df_causas_prov.head(8),
        x="accidentes",
        y="causa",
        orientation="h",
        text="accidentes",
        title=f"Causas más frecuentes en {provincia}",
        color_discrete_sequence=["#c0392b"],
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=350)
    st.plotly_chart(fig, width="stretch")

    with st.container(border=True):
        st.markdown("**📝 Interpretación**")
        st.markdown(interpret_causas(df_causas_prov))

    causa_principal = df_causas_prov.iloc[0].get("causa", "")

    # Recomendación específica para la provincia
    with st.container(border=True):
        st.markdown(f"🛡️ **Recomendación para {provincia}**")
        st.markdown(recomendacion_para_provincia(provincia, causa_principal))
else:
    st.info(f"No hay datos de causas disponibles para {provincia}.")

st.divider()

# ======================================================
# CANTONES Y ZONAS
# ======================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏙️ Cantones con mayor riesgo")

    df_cantones = ejecutar_consulta(
        *query_accidentes_por_canton(
            provincia=provincia,
            anio=filtros["anio"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    if not df_cantones.empty:
        fig = px.bar(
            df_cantones.head(10),
            x="accidentes",
            y="canton",
            orientation="h",
            text="accidentes",
            title=f"Cantones con más accidentes en {provincia}",
            color_discrete_sequence=["#e67e22"],
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
        st.plotly_chart(fig, width="stretch")

        top_canton = df_cantones.iloc[0]
        st.info(
            f"🏙️ **{top_canton['canton']}** es el cantón con más accidentes en {provincia} "
            f"({int(top_canton['accidentes']):,} casos)."
        )

with col2:
    st.subheader("🛣️ Zona urbana vs rural")

    df_zona = ejecutar_consulta(
        *query_accidentes_por_zona(
            provincia=provincia,
            anio=filtros["anio"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    if not df_zona.empty:
        fig = px.pie(
            df_zona,
            names="zona",
            values="accidentes",
            title=f"Distribución urbana/rural en {provincia}",
            hole=0.4,
            color_discrete_sequence=["#3498db", "#2ecc71"],
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, width="stretch")

        with st.container(border=True):
            st.markdown("**📝 Interpretación**")
            st.markdown(interpret_zonas(df_zona))

st.divider()

# ======================================================
# CURIOSIDADES + SABÍAS QUE
# ======================================================
col_c1, col_c2 = st.columns(2)

with col_c1:
    with st.container(border=True):
        st.markdown(f"💡 **¿Sabías que…?**  \n{sabias_que()}")

with col_c2:
    with st.container(border=True):
        st.markdown("🛡️ **Recomendación general**")
        st.markdown(recomendacion_aleatoria())

st.divider()

# ======================================================
# DATOS TABULARES
# ======================================================
st.subheader("📋 Detalle por cantón")

with st.expander("Ver tabla completa", expanded=False):
    if not df_cantones.empty:
        st.dataframe(df_cantones, width="stretch", hide_index=True)

st.caption(f"Información geográfica correspondiente a {provincia}.")
