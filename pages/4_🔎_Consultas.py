import streamlit as st
import plotly.express as px

from db import ejecutar_consulta

from sql.common_filters import BASE_FROM, construir_filtros

from sql.consultas import CONSULTA_OLAP


def filtros_globales():
    return {
        "anio": st.session_state.get("filtro_anio", "Todos"),
        "provincias": st.session_state.get("filtro_provincias", []),
        "cantones": st.session_state.get("filtro_cantones", []),
        "clases": st.session_state.get("filtro_clases", []),
        "causas": st.session_state.get("filtro_causas", []),
    }


st.title("🔎 Consultas Analíticas OLAP")

st.markdown(
    """
    Realiza análisis dinámicos sobre el Data Warehouse.

    Selecciona una dimensión para agrupar la información
    y una métrica para analizar los accidentes.
    """
)

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


# =====================================================
# SELECCIÓN OLAP
# =====================================================

col1, col2 = st.columns(2)

with col1:
    dimension_nombre = st.selectbox(
        "📌 Agrupar información por",
        dimensiones.keys()
    )

with col2:
    metrica_nombre = st.selectbox(
        "📊 Métrica a analizar",
        metricas.keys()
    )

st.divider()


# =====================================================
# CONSTRUIR FILTROS SQL
# =====================================================

filtros = filtros_globales()

where_clause, parametros = construir_filtros(
    anio=filtros["anio"],
    provincias=filtros["provincias"],
    cantones=filtros["cantones"],
    clases=filtros["clases"],
    causas=filtros["causas"],
)


# =====================================================
# GENERAR CONSULTA DINÁMICA
# =====================================================

sql = CONSULTA_OLAP.format(
    dimension=dimensiones[dimension_nombre],
    metrica=metricas[metrica_nombre],
    base_from=BASE_FROM,
    where_clause=where_clause
)


# =====================================================
# EJECUTAR
# =====================================================

df = ejecutar_consulta(sql, parametros)


# =====================================================
# RESULTADOS
# =====================================================

st.subheader(f"{metrica_nombre} por {dimension_nombre}")

if df.empty:
    st.warning("No existen datos para los filtros seleccionados.")
else:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

    with col2:
        fig = px.bar(
            df.head(15),
            x="categoria",
            y="valor",
            text="valor",
            title=f"Top {dimension_nombre}"
        )

        fig.update_layout(xaxis_tickangle=-45)

        st.plotly_chart(fig, width="stretch")


# =====================================================
# EXPORTAR
# =====================================================

st.divider()

if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Descargar resultado CSV",
        data=csv,
        file_name="consulta_olap_accidentes.csv",
        mime="text/csv"
    )
