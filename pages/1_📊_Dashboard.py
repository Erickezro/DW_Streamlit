import streamlit as st
import plotly.express as px

from db import ejecutar_consulta

from sql.dashboard import (
    ANIOS_DISPONIBLES,
    CAUSAS_DISPONIBLES,
    CLASES_DISPONIBLES,
    PROVINCIAS_DISPONIBLES,
    query_cantones_disponibles,
    query_accidentes_por_anio,
    query_accidentes_por_clase,
    query_accidentes_por_zona,
    query_kpis,
    query_top_causas,
    query_top_provincias,
)
from utils.insights import (
    interpret_kpis,
    interpret_tendencia_anual,
    interpret_provincias,
    interpret_causas,
    interpret_clases,
    interpret_zonas,
    sabias_que,
    recomendacion_aleatoria,
)


def filtros_globales():
    return {
        "anio": st.session_state.get("filtro_anio", "Todos"),
        "provincias": st.session_state.get("filtro_provincias", []),
        "cantones": st.session_state.get("filtro_cantones", []),
        "clases": st.session_state.get("filtro_clases", []),
        "causas": st.session_state.get("filtro_causas", []),
    }


# ====================================================
# HERO
# ====================================================
st.title("📊 Panorama de la Seguridad Vial en Ecuador")

with st.container(border=True):
    st.markdown(
        """
        ### La seguridad vial es un compromiso de todos

        Bienvenido al observatorio ciudadano de siniestralidad vial del Ecuador.
        Aquí puedes explorar los datos reales de accidentes de tránsito registrados en el país,
        entender las causas, identificar los patrones de riesgo y, sobre todo,
        **tomar conciencia para prevenir**.

        Los datos presentados provienen del Data Warehouse de Accidentes de Tránsito del Ecuador
        y se actualizan periódicamente. Utiliza los filtros de la barra lateral para personalizar
        tu análisis.
        """
    )

st.divider()

filtros = filtros_globales()

# ====================================================
# ¿SABÍAS QUE...?
# ====================================================
with st.container(border=True):
    col_sq, _ = st.columns([6, 2])
    with col_sq:
        st.markdown(f"💡 **¿Sabías que…?**  \n{sabias_que()}")

st.divider()

# ====================================================
# KPIs + INTERPRETACIÓN
# ====================================================
st.subheader("💡 Resumen del Impacto")

kpi = ejecutar_consulta(
    *query_kpis(
        anio=filtros["anio"],
        provincias=filtros["provincias"],
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
        *query_kpis(
            anio=str(anio_comparacion),
            provincias=filtros["provincias"],
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

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🚗 Accidentes",
        f"{int(fila_kpi['accidentes']):,}",
        delta=delta_accidentes,
        delta_color="inverse"
    )

with col2:
    st.metric(
        "☠️ Fallecidos",
        f"{int(fila_kpi['fallecidos']):,}",
        delta=delta_fallecidos,
        delta_color="inverse"
    )

with col3:
    st.metric(
        "🩹 Lesionados",
        f"{int(fila_kpi['lesionados']):,}",
        delta=delta_lesionados,
        delta_color="inverse"
    )

with col4:
    st.metric(
        "👥 Víctimas",
        f"{int(fila_kpi['victimas']):,}",
        delta=delta_victimas,
        delta_color="inverse"
    )

st.caption(
    f"Los deltas muestran la variación porcentual respecto al año anterior."
    if delta_accidentes is not None
    else "Selecciona un año específico en los filtros para ver la tendencia."
)

# Interpretación de KPIs
if fila_kpi.get("accidentes", 0) > 0:
    with st.container(border=True):
        st.markdown("**📝 Interpretación**")
        st.markdown(
            interpret_kpis(
                accidentes=fila_kpi["accidentes"],
                fallecidos=fila_kpi["fallecidos"],
                lesionados=fila_kpi["lesionados"],
                delta_acc=delta_accidentes,
            )
        )

st.divider()

# ====================================================
# TENDENCIA ANUAL
# ====================================================
st.subheader("📈 Evolución en el tiempo")

df_anio = ejecutar_consulta(
    *query_accidentes_por_anio(
        anio=filtros["anio"],
        provincias=filtros["provincias"],
        cantones=filtros["cantones"],
        clases=filtros["clases"],
        causas=filtros["causas"],
    )
)

fig = px.bar(
    df_anio,
    x="anio",
    y="accidentes",
    text="accidentes",
    title="¿Cómo ha cambiado la cantidad de accidentes por año?",
    color_discrete_sequence=["#e74c3c"],
)

fig.update_layout(
    xaxis_title="Año",
    yaxis_title="Accidentes",
)

st.plotly_chart(fig, width="stretch")

if not df_anio.empty:
    with st.container(border=True):
        st.markdown("**📝 Interpretación**")
        st.markdown(interpret_tendencia_anual(df_anio))

st.divider()

# ====================================================
# ¿Sabías que...? (segundo)
# ====================================================
with st.container(border=True):
    col_sq2, _ = st.columns([6, 2])
    with col_sq2:
        st.markdown(f"💡 **¿Sabías que…?**  \n{sabias_que()}")

st.divider()

# ====================================================
# FOCO GEOGRÁFICO Y CAUSAS
# ====================================================
st.subheader("📍 Foco Geográfico y Causas Principales")
col1, col2 = st.columns(2)

with col1:
    df_prov = ejecutar_consulta(
        *query_top_provincias(
            anio=filtros["anio"],
            provincias=filtros["provincias"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.bar(
        df_prov,
        x="accidentes",
        y="provincia",
        orientation="h",
        text="accidentes",
        title="¿Dónde ocurren más accidentes?",
        color_discrete_sequence=["#e67e22"],
    )

    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, width="stretch")

    if not df_prov.empty:
        with st.container(border=True):
            st.markdown("**📝 Interpretación**")
            st.markdown(interpret_provincias(df_prov))

with col2:
    df_causas = ejecutar_consulta(
        *query_top_causas(
            anio=filtros["anio"],
            provincias=filtros["provincias"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.bar(
        df_causas,
        x="accidentes",
        y="causa",
        orientation="h",
        text="accidentes",
        title="¿Cuáles son las causas principales?",
        color_discrete_sequence=["#c0392b"],
    )

    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, width="stretch")

    if not df_causas.empty:
        with st.container(border=True):
            st.markdown("**📝 Interpretación**")
            st.markdown(interpret_causas(df_causas))

st.divider()

# ====================================================
# DETALLES ADICIONALES
# ====================================================
st.subheader("🧐 Detalles adicionales")

col1, col2 = st.columns(2)

with col1:
    df_clase = ejecutar_consulta(
        *query_accidentes_por_clase(
            anio=filtros["anio"],
            provincias=filtros["provincias"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.pie(
        df_clase,
        names="clase",
        values="accidentes",
        title="¿Qué tipo de accidentes predominan?",
        hole=0.35,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    st.plotly_chart(fig, width="stretch")

    if not df_clase.empty:
        with st.container(border=True):
            st.markdown("**📝 Interpretación**")
            st.markdown(interpret_clases(df_clase))

with col2:
    df_zona = ejecutar_consulta(
        *query_accidentes_por_zona(
            anio=filtros["anio"],
            provincias=filtros["provincias"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.bar(
        df_zona,
        x="zona",
        y="accidentes",
        text="accidentes",
        title="¿En qué zonas (Urbana/Rural) ocurren?",
        color_discrete_sequence=["#3498db", "#2ecc71"],
    )

    st.plotly_chart(fig, width="stretch")

    if not df_zona.empty:
        with st.container(border=True):
            st.markdown("**📝 Interpretación**")
            st.markdown(interpret_zonas(df_zona))

st.divider()

# ====================================================
# RECOMENDACIÓN PREVENTIVA
# ====================================================
with st.container(border=True):
    col_rec, _ = st.columns([5, 1])
    with col_rec:
        st.markdown("🛡️ **Recomendación para hoy**")
        st.markdown(recomendacion_aleatoria())

st.caption(
    "Fuente: Data Warehouse de Accidentes de Tránsito del Ecuador. "
    "Los datos reflejan la información disponible en el sistema."
)
