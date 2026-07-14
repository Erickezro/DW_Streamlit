import streamlit as st

from db import ejecutar_consulta


# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Acerca del DW",
    page_icon="ℹ️",
    layout="wide"
)


# =====================================================
# TÍTULO
# =====================================================

st.title("ℹ️ Acerca del Data Warehouse")

st.markdown(
    """
    ## Sistema de Análisis de Accidentes de Tránsito del Ecuador

    Esta aplicación consume información almacenada en un
    Data Warehouse diseñado bajo un modelo dimensional
    tipo estrella.

    El objetivo es facilitar el análisis histórico de los
    accidentes de tránsito mediante diferentes niveles
    de agregación y herramientas de Business Intelligence.
    """
)


st.divider()


# =====================================================
# ARQUITECTURA
# =====================================================

st.subheader("🏗️ Arquitectura de la solución")


st.code(
"""
Archivos CSV
      |
      |
      v
Apache Hop (ETL)
      |
      |
      v
SQL Server
Data Warehouse
      |
      |
      +----------------+
      |                |
      v                v
 Power BI        Streamlit
 Dashboards      Aplicación
""",
language="text"
)



# =====================================================
# MODELO ESTRELLA
# =====================================================

st.subheader("⭐ Modelo Dimensional")


col1, col2 = st.columns(2)


with col1:

    st.markdown(
    """
    ### Tabla de Hechos

    **Fact_Accidentes**

    Contiene las métricas principales:

    - Total accidentes
    - Número de fallecidos
    - Número de lesionados
    - Total víctimas

    Relaciona las dimensiones mediante claves sustitutas.
    """
    )



with col2:

    st.markdown(
    """
    ### Dimensiones

    **Dim_Tiempo**

    - Año
    - Mes
    - Día
    - Hora


    **Dim_Ubicacion**

    - Provincia
    - Cantón
    - Zona


    **Dim_Clase**

    - Tipo de accidente


    **Dim_Causa**

    - Causa del accidente
    """
    )



st.divider()



# =====================================================
# TABLAS DEL DW
# =====================================================

st.subheader("📚 Tablas del Data Warehouse")


tablas = [

    "Fact_Accidentes",

    "Dim_Tiempo",

    "Dim_Ubicacion",

    "Dim_Clase",

    "Dim_Causa"

]


for tabla in tablas:

    st.success(tabla)



st.divider()



# =====================================================
# INFORMACIÓN DEL DW
# =====================================================

st.subheader("📊 Información actual del Data Warehouse")


try:

    consulta = """

    SELECT

        COUNT(*) AS registros,

        SUM(total_accidentes) AS accidentes,

        SUM(num_fallecido) AS fallecidos,

        SUM(num_lesionado) AS lesionados

    FROM Fact_Accidentes

    """


    df = ejecutar_consulta(consulta)


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Registros",
        f"{int(df.registros[0]):,}"
    )


    col2.metric(
        "Accidentes",
        f"{int(df.accidentes[0]):,}"
    )


    col3.metric(
        "Fallecidos",
        f"{int(df.fallecidos[0]):,}"
    )


    col4.metric(
        "Lesionados",
        f"{int(df.lesionados[0]):,}"
    )


except Exception as e:

    st.warning(
        "No se pudo obtener información del Data Warehouse."
    )



st.divider()



# =====================================================
# TECNOLOGÍAS
# =====================================================

st.subheader("🛠️ Tecnologías utilizadas")


st.markdown(
"""
| Componente | Tecnología |
|---|---|
| Extracción y Transformación | Apache Hop |
| Base de datos | SQL Server |
| Modelo | Esquema estrella |
| Visualización BI | Power BI |
| Aplicación analítica | Streamlit |
| Lenguaje | Python |
"""
)



st.divider()


st.caption(
    "Data Warehouse de Accidentes de Tránsito del Ecuador"
)