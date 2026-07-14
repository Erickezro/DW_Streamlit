import streamlit as st
import plotly.express as px

from db import ejecutar_consulta

from sql.temporal import (
    ANIOS,
    query_accidentes_por_dia,
    query_accidentes_por_hora,
    query_accidentes_por_mes,
)

def filtros_globales():
    return {
        "anio": st.session_state.get("filtro_anio", "Todos"),
        "provincias": st.session_state.get("filtro_provincias", []),
        "cantones": st.session_state.get("filtro_cantones", []),
        "clases": st.session_state.get("filtro_clases", []),
        "causas": st.session_state.get("filtro_causas", []),
    }

st.title("📈 Análisis de Accidentes en el Tiempo")

st.markdown(
    "Entiende cómo varían los accidentes a lo largo del año, mes, día de la semana y hora del día. Identificar estos patrones es clave para la prevención."
)

st.divider()

filtros = filtros_globales()
anio = filtros["anio"]

# =====================================================
# Accidentes por mes
# =====================================================

st.subheader("📅 Distribución Estacional")

df_mes = ejecutar_consulta(
    *query_accidentes_por_mes(
        anio=anio,
        provincias=filtros["provincias"],
        cantones=filtros["cantones"],
        clases=filtros["clases"],
        causas=filtros["causas"],
    )
)

fig = px.line(
    df_mes,
    x="mes",
    y="accidentes",
    markers=True,
    title=f"¿Cómo se distribuyen los accidentes a lo largo del año? - {anio if anio != 'Todos' else 'Todos los años'}"
)

st.plotly_chart(fig, width="stretch")

# =====================================================
# Segunda fila
# =====================================================

col1, col2 = st.columns(2)

# -------------------------
# Accidentes por día
# -------------------------

with col1:
    st.subheader("🗓️ Patrones Semanales")

    df_dia = ejecutar_consulta(
        *query_accidentes_por_dia(
            anio=anio,
            provincias=filtros["provincias"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.bar(
        df_dia,
        x="dia",
        y="accidentes",
        text="accidentes",
        title="¿Qué días ocurren más accidentes?"
    )

    st.plotly_chart(fig, width="stretch")

# -------------------------
# Accidentes por hora
# -------------------------

with col2:
    st.subheader("⏰ Horarios Críticos")

    df_hora = ejecutar_consulta(
        *query_accidentes_por_hora(
            anio=anio,
            provincias=filtros["provincias"],
            cantones=filtros["cantones"],
            clases=filtros["clases"],
            causas=filtros["causas"],
        )
    )

    fig = px.line(
        df_hora,
        x="hora",
        y="accidentes",
        markers=True,
        title="¿En qué horas se concentran los accidentes?"
    )

    st.plotly_chart(fig, width="stretch")

st.divider()

st.subheader("Resumen de Datos")

st.dataframe(
    df_mes,
    width="stretch",
    hide_index=True
)

st.caption(
    f"Información correspondiente al año {anio if anio != 'Todos' else 'Todos los años'}"
)
