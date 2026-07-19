import streamlit as st
import plotly.express as px

from db import ejecutar_consulta

from sql.common_filters import BASE_FROM, construir_filtros
from sql.consultas import CONSULTA_OLAP
from utils.insights import interpret_olap, sabias_que, SUGERENCIAS_CONSULTAS


def filtros_globales():
    return {
        "anio": st.session_state.get("filtro_anio", "Todos"),
        "provincias": st.session_state.get("filtro_provincias", []),
        "cantones": st.session_state.get("filtro_cantones", []),
        "clases": st.session_state.get("filtro_clases", []),
        "causas": st.session_state.get("filtro_causas", []),
    }


st.title("🔎 Explorador de Datos")

with st.container(border=True):
    st.markdown(
        """
        Esta herramienta te permite **explorar los datos por tu cuenta**.
        Selecciona una dimensión (por ejemplo, provincia, causa o mes) y una métrica
        (accidentes, fallecidos, lesionados o víctimas) para generar tablas y gráficos personalizados.

        **No necesitas saber SQL.** Solo elige qué quieres ver y la aplicación se encarga del resto.
        """
    )

st.divider()

# =====================================================
# SUGERENCIAS DE CONSULTA
# =====================================================
st.subheader("💡 Prueba con un ejemplo")

# Mostrar sugerencias como pills
sugerencia_labels = [s[0] for s in SUGERENCIAS_CONSULTAS[:6]]
selected_suggestion = st.pills(
    "Selecciona una consulta de ejemplo",
    options=sugerencia_labels,
    selection_mode="single",
    label_visibility="collapsed",
)

dimension_sugerida = None
metrica_sugerida = None

if selected_suggestion:
    for label, dim, met in SUGERENCIAS_CONSULTAS:
        if label == selected_suggestion:
            dimension_sugerida = dim
            metrica_sugerida = met
            break

st.divider()

# =====================================================
# OPCIONES DE ANÁLISIS
# =====================================================
dimensiones = {
    "Provincia": "u.provincia",
    "Cantón": "u.canton",
    "Zona": "u.zona",
    "Causa": "ca.causa",
    "Clase": "c.clase",
    "Año": "t.anio",
    "Mes": "t.mes",
    "Hora": "t.hora",
}

metricas = {
    "Accidentes": "total_accidentes",
    "Fallecidos": "num_fallecido",
    "Lesionados": "num_lesionado",
    "Víctimas": "total_victimas",
}

col1, col2 = st.columns(2)

with col1:
    dimension_nombre = st.selectbox(
        "📌 Agrupar información por",
        dimensiones.keys(),
        index=list(dimensiones.keys()).index(dimension_sugerida) if dimension_sugerida else 0,
    )

with col2:
    metrica_nombre = st.selectbox(
        "📊 Métrica a analizar",
        metricas.keys(),
        index=list(metricas.keys()).index(metrica_sugerida) if metrica_sugerida else 0,
    )

st.divider()

# =====================================================
# CONSTRUIR CONSULTA
# =====================================================
filtros = filtros_globales()

where_clause, parametros = construir_filtros(
    anio=filtros["anio"],
    provincias=filtros["provincias"],
    cantones=filtros["cantones"],
    clases=filtros["clases"],
    causas=filtros["causas"],
)

sql = CONSULTA_OLAP.format(
    dimension=dimensiones[dimension_nombre],
    metrica=metricas[metrica_nombre],
    base_from=BASE_FROM,
    where_clause=where_clause,
)

df = ejecutar_consulta(sql, parametros)

# =====================================================
# RESULTADOS
# =====================================================
st.subheader(f"{metrica_nombre} por {dimension_nombre}")

if df.empty:
    st.warning(
        "No existen datos para los filtros seleccionados. "
        "Prueba cambiando los filtros o seleccionando otra combinación."
    )
else:
    col_table, col_chart = st.columns([1, 2])

    with col_table:
        st.dataframe(df, width="stretch", hide_index=True)

    with col_chart:
        if len(df) > 12:
            plot_df = df.head(15)
        else:
            plot_df = df

        fig = px.bar(
            plot_df,
            x="categoria",
            y="valor",
            text="valor",
            title=f"Top {dimension_nombre} por {metrica_nombre}",
            color_discrete_sequence=["#e74c3c"],
        )
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, width="stretch")

    # Interpretación automática
    with st.container(border=True):
        st.markdown("**📝 Interpretación**")
        st.markdown(interpret_olap(dimension_nombre, metrica_nombre, df))

    st.divider()

    # =====================================================
    # SUGERENCIAS RELACIONADAS
    # =====================================================
    st.subheader("🔗 Consultas relacionadas que podrían interesarte")

    relacionadas = [
        (label, dim, met)
        for label, dim, met in SUGERENCIAS_CONSULTAS
        if dim != dimension_nombre or met != metrica_nombre
    ]

    cols_rel = st.columns(3)
    for i, (label, dim, met) in enumerate(relacionadas[:6]):
        with cols_rel[i % 3]:
            if st.button(
                f"{label}",
                key=f"sug_rel_{i}",
                use_container_width=True,
                type="tertiary",
            ):
                dimension_sugerida = dim
                metrica_sugerida = met
                st.rerun()

    st.divider()

    # =====================================================
    # EXPORTAR
    # =====================================================
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar resultado como CSV",
        data=csv,
        file_name=f"consulta_{metrica_nombre.lower()}_por_{dimension_nombre.lower()}.csv",
        mime="text/csv",
    )

st.divider()

with st.container(border=True):
    st.markdown(f"💡 **¿Sabías que…?**  \n{sabias_que()}")
