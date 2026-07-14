import streamlit as st

from db import ejecutar_consulta
from sql.dashboard import (
    ANIOS_DISPONIBLES,
    CAUSAS_DISPONIBLES,
    CLASES_DISPONIBLES,
    PROVINCIAS_DISPONIBLES,
    query_cantones_disponibles,
)

st.set_page_config(
    page_title="DW Accidentes Ecuador",
    page_icon="🚗",
    layout="wide",
)

page = st.navigation(
    [
        st.Page("pages/1_📊_Dashboard.py", title="Panorama de la Seguridad Vial en Ecuador", icon="📊"),
        st.Page("pages/2_📈_Análisis_Temporal.py", title="Análisis de Accidentes en el Tiempo", icon="📈"),
        st.Page("pages/3_🗺️_Análisis_Geográfico.py", title="Análisis Geográfico", icon="🗺️"),
        st.Page("pages/4_🔎_Consultas.py", title="Consultas", icon="🔎"),
        st.Page("pages/5_ℹ️_Acerca_del_DW.py", title="Acerca del DW", icon="ℹ️")
    ],
    position="sidebar",
)

st.sidebar.header("Filtros globales")

anios = ejecutar_consulta(ANIOS_DISPONIBLES)["anio"].dropna().astype(int).tolist()
provincias = ejecutar_consulta(PROVINCIAS_DISPONIBLES)["provincia"].dropna().tolist()
clases = ejecutar_consulta(CLASES_DISPONIBLES)["clase"].dropna().tolist()
causas = ejecutar_consulta(CAUSAS_DISPONIBLES)["causa"].dropna().tolist()

if "filtro_anio" not in st.session_state:
    st.session_state.filtro_anio = "Todos"

if "filtro_provincias" not in st.session_state:
    st.session_state.filtro_provincias = []

if "filtro_cantones" not in st.session_state:
    st.session_state.filtro_cantones = []

if "filtro_clases" not in st.session_state:
    st.session_state.filtro_clases = []

if "filtro_causas" not in st.session_state:
    st.session_state.filtro_causas = []

st.sidebar.selectbox("📅 Año", options=["Todos"] + anios, key="filtro_anio")
st.sidebar.multiselect("🗺️ Provincia", options=provincias, key="filtro_provincias")

cantones = ejecutar_consulta(
    *query_cantones_disponibles(provincias=st.session_state.filtro_provincias)
)["canton"].dropna().tolist()

st.session_state.filtro_cantones = [
    canton for canton in st.session_state.filtro_cantones
    if canton in cantones
]

st.sidebar.multiselect("🏙️ Cantón", options=cantones, key="filtro_cantones")
st.sidebar.multiselect("🚧 Clase", options=clases, key="filtro_clases")
st.sidebar.multiselect("⚠️ Causa", options=causas, key="filtro_causas")

page.run()