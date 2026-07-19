import streamlit as st
import plotly.express as px

from db import ejecutar_consulta

from sql.temporal import (
    ANIOS,
    query_accidentes_por_dia,
    query_accidentes_por_hora,
    query_accidentes_por_mes,
)
from utils.insights import (
    interpret_meses,
    interpret_dias,
    interpret_horas,
    sabias_que,
    recomendacion_aleatoria,
    barra_riesgo_html,
    nivel_riesgo,
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

with st.container(border=True):
    st.markdown(
        """
        El tiempo es un factor determinante en la siniestralidad vial. Hay horas, días y meses
        en los que el riesgo de sufrir un accidente aumenta significativamente.
        **Conocer estos patrones te ayuda a prevenir.**

        Analiza la distribución de accidentes por mes, día de la semana y hora del día,
        y descubre los momentos críticos en Ecuador.
        """
    )

st.divider()

filtros = filtros_globales()
anio = filtros["anio"]

# =====================================================
# ACCIDENTES POR MES
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
    title=f"Accidentes por mes — {anio if anio != 'Todos' else 'Todos los años'}",
    color_discrete_sequence=["#e74c3c"],
)

fig.update_layout(
    xaxis_title="Mes",
    yaxis_title="Accidentes",
    height=420,
)

st.plotly_chart(fig, width="stretch")

if not df_mes.empty:
    with st.container(border=True):
        st.markdown("**📝 Interpretación**")
        st.markdown(interpret_meses(df_mes))

st.divider()

# =====================================================
# SABÍAS QUE + RECOMENDACIÓN
# =====================================================
col_mid1, col_mid2 = st.columns(2)

with col_mid1:
    with st.container(border=True):
        st.markdown(f"💡 **¿Sabías que…?**  \n{sabias_que()}")

with col_mid2:
    with st.container(border=True):
        st.markdown("🛡️ **Recomendación para esta temporada**")
        st.markdown(recomendacion_aleatoria())

st.divider()

# =====================================================
# PATRONES SEMANALES Y HORARIOS
# =====================================================
col1, col2 = st.columns(2)

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
        title="¿Qué días ocurren más accidentes?",
        color_discrete_sequence=["#e67e22"],
    )

    fig.update_layout(height=400)
    st.plotly_chart(fig, width="stretch")

    if not df_dia.empty:
        with st.container(border=True):
            st.markdown("**📝 Interpretación**")
            st.markdown(interpret_dias(df_dia))

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
        title="¿En qué horas se concentran los accidentes?",
        color_discrete_sequence=["#c0392b"],
    )

    fig.update_layout(
        xaxis_title="Hora del día",
        yaxis_title="Accidentes",
        height=400,
    )

    st.plotly_chart(fig, width="stretch")

    if not df_hora.empty:
        with st.container(border=True):
            st.markdown("**📝 Interpretación**")
            st.markdown(interpret_horas(df_hora))

st.divider()

# =====================================================
# BARRAS DE RIESGO
# =====================================================
st.subheader("🔴 Niveles de riesgo por período")

if not df_mes.empty and not df_dia.empty and not df_hora.empty:
    tab_meses, tab_dias, tab_horas = st.tabs(["📅 Por mes", "🗓️ Por día", "⏰ Por hora"])

    with tab_meses:
        max_acc = df_mes["accidentes"].max()
        st.markdown("**Meses con mayor riesgo**")
        for _, r in df_mes.iterrows():
            st.markdown(barra_riesgo_html(r["accidentes"], max_acc, r["mes"]), unsafe_allow_html=True)

    with tab_dias:
        max_acc = df_dia["accidentes"].max()
        st.markdown("**Días con mayor riesgo**")
        for _, r in df_dia.iterrows():
            st.markdown(barra_riesgo_html(r["accidentes"], max_acc, r["dia"]), unsafe_allow_html=True)

    with tab_horas:
        max_acc = df_hora["accidentes"].max()
        st.markdown("**Horas con mayor riesgo**")
        horas_mostrar = df_hora[df_hora["cod_hora"].between(6, 21)]
        if horas_mostrar.empty:
            horas_mostrar = df_hora.head(12)
        for _, r in horas_mostrar.iterrows():
            hora_label = str(r.get("hora", r.get("cod_hora", "")))
            st.markdown(barra_riesgo_html(r["accidentes"], max_acc, hora_label), unsafe_allow_html=True)

st.divider()

# =====================================================
# RECOMENDACIONES SEGÚN HORARIO
# =====================================================
st.subheader("🛡️ Recomendaciones según los patrones encontrados")

df_hora_val = ejecutar_consulta(
    *query_accidentes_por_hora(
        anio=anio,
        provincias=filtros["provincias"],
        cantones=filtros["cantones"],
        clases=filtros["clases"],
        causas=filtros["causas"],
    )
)

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    with st.container(border=True):
        st.markdown("🌙 **Si conduces de noche**")
        st.markdown(
            "Reduce la velocidad, usa luces bajas y evita conducir si has consumido alcohol. "
            "La visibilidad nocturna es limitada y los riesgos aumentan."
        )

with col_r2:
    with st.container(border=True):
        st.markdown("🏙️ **En horas pico**")
        st.markdown(
            "Mantén la calma en el tráfico, respeta las distancias y evita distracciones. "
            "La congestión vehicular aumenta la probabilidad de colisiones."
        )

with col_r3:
    with st.container(border=True):
        st.markdown("🎉 **Fines de semana y feriados**")
        st.markdown(
            "Planifica con anticipación. Si vas a consumir alcohol, designa un conductor "
            "o usa transporte público. Los fines de semana concentran más accidentes."
        )

st.divider()

# =====================================================
# DATOS TABULARES
# =====================================================
st.subheader("📋 Resumen de datos")

with st.expander("Ver tabla de datos completa", expanded=False):
    st.dataframe(
        df_mes,
        width="stretch",
        hide_index=True,
    )

st.caption(
    f"Información correspondiente a {anio if anio != 'Todos' else 'todos los años'}."
    " Los patrones temporales ayudan a identificar momentos de mayor riesgo."
)
