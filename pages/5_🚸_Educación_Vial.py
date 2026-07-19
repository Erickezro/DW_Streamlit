import streamlit as st

from db import ejecutar_consulta
from utils.insights import sabias_que


st.set_page_config(
    page_title="Educación Vial",
    page_icon="🚸",
    layout="wide",
)

# ---- Helper: consultas ----
@st.cache_data(ttl=300)
def _cifras_totales():
    return ejecutar_consulta("""
        SELECT
            SUM(total_accidentes) AS accidentes,
            SUM(num_fallecido) AS fallecidos,
            SUM(num_lesionado) AS lesionados
        FROM Fact_Accidentes
    """)

@st.cache_data(ttl=300)
def _causas_top():
    return ejecutar_consulta("""
        SELECT TOP 3 ca.causa, SUM(f.total_accidentes) AS accidentes
        FROM Fact_Accidentes f
        INNER JOIN Dim_Causa ca ON f.id_causa = ca.id_causa
        GROUP BY ca.causa
        ORDER BY accidentes DESC
    """)


try:
    df_total = _cifras_totales()
    TOTAL_ACC = int(df_total.iloc[0].accidentes) if not df_total.empty else 0
    TOTAL_FAL = int(df_total.iloc[0].fallecidos) if not df_total.empty else 0
    TOTAL_LES = int(df_total.iloc[0].lesionados) if not df_total.empty else 0
except Exception:
    TOTAL_ACC = TOTAL_FAL = TOTAL_LES = 0

CAUSA_TOP = ""
try:
    df_causas = _causas_top()
    if not df_causas.empty:
        CAUSA_TOP = df_causas.iloc[0].causa
except Exception:
    pass


# =====================================================
# HERO
# =====================================================
st.title("🚸 Educación y Seguridad Vial")

with st.container(border=True):
    st.markdown(
        """
        ### Conciencia, datos y prevención para reducir los accidentes de tránsito en el Ecuador

        Esta aplicación nace con un propósito claro: **transformar los datos en conocimiento**
        para educar a la ciudadanía sobre la realidad de la siniestralidad vial en el país.
        """
    )

st.divider()

# =====================================================
# CONTEXTO DESDE LOS DATOS
# =====================================================
st.subheader("📊 La realidad en cifras")

col_ctx1, col_ctx2, col_ctx3 = st.columns(3)
col_ctx1.metric("🚗 Accidentes registrados", f"{TOTAL_ACC:,}")
col_ctx2.metric("💔 Fallecidos", f"{TOTAL_FAL:,}")
col_ctx3.metric("🏥 Lesionados", f"{TOTAL_LES:,}")

with st.container(border=True):
    st.markdown(
        f"En Ecuador se han registrado **{TOTAL_ACC:,} accidentes de tránsito**, "
        f"que dejaron **{TOTAL_FAL:,} fallecidos** y **{TOTAL_LES:,} lesionados**. "
        "Detrás de cada número hay una familia y una historia. "
        "La mayoría de estos accidentes **se pueden prevenir** con educación y responsabilidad."
    )

if CAUSA_TOP:
    with st.container(border=True):
        st.markdown(
            f"⚠️ La principal causa de accidentes en el país es **{CAUSA_TOP}**. "
            "Conocer esta información nos ayuda a tomar medidas específicas para evitarlo."
        )

st.divider()

# =====================================================
# EDUCACIÓN POR CATEGORÍA (TABS)
# =====================================================
st.subheader("🧠 Educación vial para todos")

tab_conductor, tab_moto, tab_peatones, tab_ciclistas = st.tabs(
    ["🚗 Conductores", "🛵 Motociclistas", "🚶 Peatones", "🚲 Ciclistas"]
)

with tab_conductor:
    col_tips, col_data = st.columns([3, 2])

    with col_tips:
        st.markdown("**Consejos prácticos**")
        st.markdown(
            """
            - Respeta los límites de velocidad. A mayor velocidad, menor control y más graves son las consecuencias.
            - Usa siempre el cinturón de seguridad, incluidos los pasajeros traseros.
            - Nunca conduzcas bajo efectos del alcohol o drogas.
            - No uses el teléfono móvil mientras conduces. Una distracción de 2 segundos duplica el riesgo de accidente.
            - Mantén una distancia prudente con el vehículo de adelante (regla de los 3 segundos).
            - Respeta las señales de tránsito y los semáforos.
            - Revisa periódicamente frenos, neumáticos, luces y niveles del vehículo.
            - Si sientes fatiga o sueño, detente y descansa. La fatiga causa el 20% de los accidentes en carretera.
            """
        )

    with col_data:
        st.markdown("**Datos que deberías saber**")
        st.markdown(
            f"""
            - En Ecuador se registran **{TOTAL_ACC:,} accidentes** en total.
            - El exceso de velocidad es una de las causas principales.
            - Los fines de semana concentran más accidentes, especialmente en la noche.
            - Las zonas urbanas tienen más accidentes, pero las rurales tienen mayor letalidad.
            """
        )
        if CAUSA_TOP:
            st.warning(
                f"⚠️ Recuerda: la principal causa de accidentes en Ecuador es "
                f"**{CAUSA_TOP}**. Conduce con responsabilidad."
            )

    st.divider()

    st.markdown("**❌ Errores frecuentes que debes evitar**")
    col_err1, col_err2 = st.columns(2)
    with col_err1:
        st.markdown(
            """
            - ❌ **"Me tomo solo una cerveza, no pasa nada"** → El alcohol afecta tus reflejos incluso en pequeñas cantidades.
            - ❌ **"Conozco la ruta, no necesito el cinturón"** → El 80% de las muertes en accidentes ocurren a menos de 40 km/h sin cinturón.
            - ❌ **"Voy rápido, pero controlo"** → El exceso de velocidad reduce tu capacidad de reacción y aumenta la distancia de frenado.
            """
        )
    with col_err2:
        st.markdown(
            """
            - ❌ **"Solo miro el celular un segundo"** → A 60 km/h, 2 segundos de distracción equivalen a 33 metros sin mirar la vía.
            - ❌ **"Los peatones tienen que cuidarse"** → El conductor es el responsable de la seguridad de todos en la vía.
            """
        )

with tab_moto:
    col_tips, col_data = st.columns([3, 2])

    with col_tips:
        st.markdown("**Consejos prácticos**")
        st.markdown(
            """
            - Usa siempre casco homologado y bien ajustado. El casco reduce hasta 70% el riesgo de lesiones graves.
            - Usa ropa reflectiva, especialmente en la noche o en condiciones de baja visibilidad.
            - Respeta las normas de tránsito. No circules entre vehículos en movimiento.
            - Mantén las luces encendidas durante el día para ser más visible.
            - Revisa frenos, neumáticos, luces y cadena antes de cada salida.
            - No circules por la acera ni en sentido contrario.
            - Evita conducir bajo la lluvia; el asfalto mojado reduce el agarre.
            """
        )

    with col_data:
        st.markdown("**Datos que deberías saber**")
        st.markdown(
            """
            - Los motociclistas tienen **16 veces más riesgo** de morir en un accidente que los ocupantes de autos.
            - El casco es el elemento de seguridad más importante para un motociclista.
            - La mayoría de accidentes de moto ocurren en intersecciones y en horas de la tarde.
            - Las lesiones en piernas y cabeza son las más frecuentes en accidentes de moto.
            """
        )

    st.divider()

    st.markdown("**❌ Errores frecuentes**")
    st.markdown(
        """
        - ❌ **"El casco es incomodo, mejor no lo uso"** → Sin casco, una caída a 30 km/h puede ser mortal.
        - ❌ **"La moto es pequeña, puedo pasar entre los carros"** → Circular entre vehículos en movimiento es peligroso y está prohibido.
        - ❌ **"En la noche no me ven, pero yo sí veo"** → Usa ropa reflectiva y luces encendidas para ser visible.
        """
    )

with tab_peatones:
    col_tips, col_data = st.columns([3, 2])

    with col_tips:
        st.markdown("**Consejos prácticos**")
        st.markdown(
            """
            - Cruza siempre por los pasos peatonales, puentes peatonales o esquinas.
            - Mira a ambos lados antes de cruzar, incluso en calles de un solo sentido.
            - No cruces entre vehículos estacionados; los conductores pueden no verte.
            - Evita usar auriculares o mirar el teléfono mientras cruzas la calle.
            - Camina por las aceras siempre que sea posible.
            - Si no hay acera, camina de frente al tráfico para ver los vehículos que se aproximan.
            - De noche, usa ropa clara o reflectiva para ser visible.
            """
        )

    with col_data:
        st.markdown("**Datos que deberías saber**")
        st.markdown(
            """
            - Un peatón tiene **90% más probabilidad de sobrevivir** si es impactado a 30 km/h vs 50 km/h.
            - En Ecuador, los atropellos son una causa frecuente de accidentes en zonas urbanas.
            - La mayoría de atropellos ocurren en la noche y en zonas sin iluminación adecuada.
            - Cruzar por lugares no habilitados aumenta hasta 3 veces el riesgo de ser atropellado.
            """
        )

    st.divider()

    st.markdown("**❌ Errores frecuentes**")
    st.markdown(
        """
        - ❌ **"No viene ningún carro, puedo cruzar rápido"** → Un vehículo a 60 km/h recorre 16 metros por segundo. Calcula bien.
        - ❌ **"El semáforo peatonal está en rojo, pero no viene nadie"** -> Respeta siempre las señales; los conductores también confían en ellas.
        """
    )

with tab_ciclistas:
    col_tips, col_data = st.columns([3, 2])

    with col_tips:
        st.markdown("**Consejos prácticos**")
        st.markdown(
            """
            - Usa casco certificado y adáptalo correctamente.
            - Utiliza luces delantera (blanca) y trasera (roja) al circular de noche.
            - Usa ropa reflectiva y colores vivos para ser visible.
            - Respeta todas las señales de tránsito: semáforos, stops y cedas.
            - Circula por la derecha, en el sentido del tráfico.
            - Señaliza tus giros con anticipación usando tus brazos.
            - Revisa frenos, cadena, neumáticos y luces antes de cada salida.
            - En lo posible, usa ciclovías o rutas designadas para bicicletas.
            """
        )

    with col_data:
        st.markdown("**Datos que deberías saber**")
        st.markdown(
            """
            - El casco reduce hasta un **70% el riesgo de lesiones graves** en la cabeza.
            - La mayoría de accidentes de ciclistas ocurren en intersecciones.
            - Circular sin luces en la noche aumenta significativamente el riesgo de colisión.
            - Las lesiones más comunes en ciclistas son fracturas de clavícula, muñeca y lesiones en la cabeza.
            """
        )

    st.divider()

    st.markdown("**❌ Errores frecuentes**")
    st.markdown(
        """
        - ❌ **"La bicicleta no necesita mantenimiento"** → Frenos desgastados o cadena suelta pueden causar accidentes graves.
        - ❌ **"Como voy en bici, no tengo que respetar semáforos"** → Los ciclistas son vehículos y deben cumplir las mismas normas.
        """
    )

st.divider()

# =====================================================
# MITOS Y REALIDADES
# =====================================================
st.subheader("🤔 Mitos y realidades de la seguridad vial")

mitos = [
    (
        '❌ **"Los accidentes pasan porque sí, es cuestión de suerte"**',
        '✅ **Realidad:** Más del 90% de los accidentes son causados por error humano y se pueden prevenir con conductas responsables.'
    ),
    (
        '❌ **"Si manejo despacio, no necesito cinturón"**',
        '✅ **Realidad:** Un choque a 30 km/h equivale a caer desde un tercer piso. El cinturón salva vidas a cualquier velocidad.'
    ),
    (
        '❌ **"Un traguito no afecta mi conducción"**',
        '✅ **Realidad:** El alcohol afecta los reflejos, la coordinación y el juicio incluso en bajas cantidades. Es mejor no tomar nada si vas a conducir.'
    ),
    (
        '❌ **"Las mujeres conducen peor que los hombres"**',
        '✅ **Realidad:** Los estudios muestran que los hombres tienen más accidentes graves y cometen más infracciones de tránsito que las mujeres.'
    ),
]

for mito, realidad in mitos:
    with st.container(border=True):
        col_m, col_r = st.columns([1, 3])
        with col_m:
            st.markdown(mito)
        with col_r:
            st.markdown(realidad)

st.divider()

# =====================================================
# PREGUNTAS FRECUENTES
# =====================================================
st.subheader("❓ Preguntas frecuentes sobre seguridad vial")

faqs = [
    (
        "¿Cuál es la velocidad máxima permitida en zonas urbanas?",
        "En Ecuador, la velocidad máxima en zonas urbanas es de **50 km/h**. En zonas escolares y residenciales puede ser menor (25-30 km/h)."
    ),
    (
        "¿Cada cuánto debo revisar mi vehículo?",
        "Se recomienda una revisión básica cada **5,000 km o 3 meses** (neumáticos, frenos, luces, niveles). Una revisión completa cada **10,000 km o 6 meses**."
    ),
    (
        "¿Qué hago si me detienen en un control de alcohol?",
        "Coopera con la autoridad. Si has consumido alcohol, acepta las consecuencias. Conducir en estado de embriaguez es un delito penado con prisión en Ecuador."
    ),
    (
        "¿Es obligatorio el SOAT?",
        "Sí. Todo vehículo motorizado que circule en Ecuador debe tener el SOAT (Seguro Obligatorio de Accidentes de Tránsito) vigente."
    ),
    (
        "¿Qué debo llevar en mi vehículo por seguridad?",
        "Extintor, botiquín de primeros auxilios, triángulos de seguridad, llanta de repuesto, gato y herramienta básica."
    ),
]

for pregunta, respuesta in faqs:
    with st.expander(pregunta):
        st.markdown(respuesta)

st.divider()

# =====================================================
# SEÑALES DE TRÁNSITO
# =====================================================
st.subheader("🛑 Señales de tránsito básicas")

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    with st.container(border=True):
        st.markdown("🔴 **Señales Reglamentarias**")
        st.markdown("Indican obligación o prohibición. Ignorarlas es una infracción.")
        st.markdown("- **PARE** (Octogonal roja): Detención total obligatoria.")
        st.markdown("- **CEDEA EL PASO** (Triangular): Reduce y cede si es necesario.")
        st.markdown("- **VELOCIDAD MÁXIMA**: No excedas el límite indicado.")
        st.markdown("- **NO ESTACIONAR**: Prohibido estacionar en ese lugar.")

with col_s2:
    with st.container(border=True):
        st.markdown("🟡 **Señales Preventivas**")
        st.markdown("Advierten sobre peligros o condiciones especiales en la vía.")
        st.markdown("- **CURVA PELIGROSA**: Reduce la velocidad antes de entrar.")
        st.markdown("- **RESALTO / REDUCTOR DE VELOCIDAD**: Disminuye la marcha.")
        st.markdown("- **PASO PEATONAL**: Los peatones tienen prioridad.")
        st.markdown("- **ZONA ESCOLAR**: Extrema precauciones, hay niños.")

with col_s3:
    with st.container(border=True):
        st.markdown("🟢 **Señales Informativas**")
        st.markdown("Orientan al conductor sobre destinos, servicios y distancias.")
        st.markdown("- **RUTA PANAMERICANA**: Identificación de vías principales.")
        st.markdown("- **HOSPITAL**: Indica la cercanía de un centro de salud.")
        st.markdown("- **GASOLINERA**: Próxima estación de servicio.")
        st.markdown("- **DISTANCIA A POBLACIONES**: Kilometraje hasta el destino.")

st.divider()

# =====================================================
# RECURSOS
# =====================================================
st.subheader("📚 Recursos de seguridad vial en Ecuador")

st.markdown(
    """
    | Organización | Descripción | Enlace |
    |---|---|---|
    | **ANT** – Agencia Nacional de Tránsito | Normativa, licencias y estadísticas oficiales | [ant.gob.ec](https://www.ant.gob.ec) |
    | **ECU911** | Servicio integrado de emergencias | [ecu911.gob.ec](https://www.ecu911.gob.ec) |
    | **MTOP** – Ministerio de Transporte y Obras Públicas | Planes de seguridad vial | [obraspublicas.gob.ec](https://www.obraspublicas.gob.ec) |
    | **Agencia de Seguridad Vial (ASONEC)** | Observatorio de seguridad vial | [asonec.org](https://asonec.org) |
    | **OMS – Seguridad Vial** | Datos y campañas mundiales | [who.int/roadsafety](https://www.who.int/roadsafety) |
    """
)

st.divider()

# =====================================================
# CIERRE
# =====================================================
col_quote, _ = st.columns([3, 1])

with col_quote:
    st.markdown(
        """
        > *"La seguridad vial no es accidental, es una decisión."*

        Los datos mostrados en esta aplicación provienen del Data Warehouse de Accidentes
        de Tránsito del Ecuador. Úsalos para informarte, educar a otros y contribuir
        a un Ecuador con menos víctimas viales.
        """
    )

st.caption("Construido con datos abiertos y Streamlit · Educación vial basada en evidencias")
