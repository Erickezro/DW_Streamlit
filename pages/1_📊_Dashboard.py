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


def filtros_globales():

    return {
        "anio": st.session_state.get("filtro_anio", "Todos"),
        "provincias": st.session_state.get("filtro_provincias", []),
        "cantones": st.session_state.get("filtro_cantones", []),
        "clases": st.session_state.get("filtro_clases", []),
        "causas": st.session_state.get("filtro_causas", []),
    }

st.title("📊 Panorama de la Seguridad Vial en Ecuador")
st.markdown(
    """
    Bienvenido a este panel informativo. Aquí puedes explorar los datos sobre la accidentabilidad vial en Ecuador. 
    El objetivo es facilitar la comprensión de las tendencias y los factores críticos que impactan en la seguridad en nuestras vías.
    """
)

filtros = filtros_globales()

st.divider()

# ====================================================
# KPIs
# ====================================================

st.subheader("💡 Resumen del Impacto")
st.markdown("Principales indicadores de siniestralidad según los filtros seleccionados.")

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

# --- Tendencia: comparar con año anterior ---
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
    else "Seleccione un año específico en los filtros para ver la tendencia."
)

st.divider()

# ====================================================
# Tendencias
# ====================================================

st.subheader("📈 Evolución en el tiempo")

df = ejecutar_consulta(
    *query_accidentes_por_anio(
        anio=filtros["anio"],
        provincias=filtros["provincias"],
        cantones=filtros["cantones"],
        clases=filtros["clases"],
        causas=filtros["causas"],
    )
)

fig = px.bar(
    df,
    x="anio",
    y="accidentes",
    text="accidentes",
    title="¿Cómo ha cambiado la cantidad de accidentes por año?"
)

fig.update_layout(
    xaxis_title="Año",
    yaxis_title="Accidentes"
)

st.plotly_chart(fig, width="stretch")

st.divider()

# ====================================================
# Geografía y Causas
# ====================================================

st.subheader("📍 Foco Geográfico y Causas Principales")
col1, col2 = st.columns(2)

# -------------------------
# Top provincias
# -------------------------

with col1:
    df = ejecutar_consulta(
        *query_top_provincias(
            anio=filtros["anio"],
            provincias=filtros["provincias"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.bar(
        df,
        x="accidentes",
        y="provincia",
        orientation="h",
        text="accidentes",
        title="¿Dónde ocurren más accidentes?"
    )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig, width="stretch")

# -------------------------
# Top causas
# -------------------------

with col2:
    df = ejecutar_consulta(
        *query_top_causas(
            anio=filtros["anio"],
            provincias=filtros["provincias"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.bar(
        df,
        x="accidentes",
        y="causa",
        orientation="h",
        text="accidentes",
        title="¿Cuáles son las causas principales?"
    )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig, width="stretch")

# ====================================================
# Contexto adicional
# ====================================================

st.divider()
st.subheader("🧐 Detalles adicionales")

col1, col2 = st.columns(2)

# -------------------------
# Accidentes por clase
# -------------------------

with col1:
    df = ejecutar_consulta(
        *query_accidentes_por_clase(
            anio=filtros["anio"],
            provincias=filtros["provincias"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.pie(
        df,
        names="clase",
        values="accidentes",
        title="¿Qué tipo de accidentes predominan?"
    )

    st.plotly_chart(fig, width="stretch")

# -------------------------
# Accidentes por zona
# -------------------------

with col2:
    df = ejecutar_consulta(
        *query_accidentes_por_zona(
            anio=filtros["anio"],
            provincias=filtros["provincias"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.bar(
        df,
        x="zona",
        y="accidentes",
        text="accidentes",
        title="¿En qué zonas (Urbana/Rural) ocurren?"
    )

    st.plotly_chart(fig, width="stretch")
