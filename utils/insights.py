"""
Motor de interpretación automática de datos para todas las páginas.

Convierte DataFrames en narrativas ciudadanas en lenguaje natural,
genera recomendaciones preventivas y datos curiosos.
"""

from __future__ import annotations

import random
from datetime import datetime

import pandas as pd


# =========================================================================
# FRASES ¿SABÍAS QUE...?
# =========================================================================

_SABIAS_QUE: list[str] = [
    "El uso del cinturón de seguridad reduce hasta un 50% el riesgo de muerte en un accidente.",
    "Conducir bajo los efectos del alcohol multiplica por 5 el riesgo de sufrir un accidente.",
    "El exceso de velocidad es una de las principales causas de accidentes en Ecuador.",
    "En Ecuador, los fines de semana concentran la mayor cantidad de accidentes de tránsito.",
    "Usar el teléfono móvil mientras conduces aumenta 4 veces el riesgo de colisión.",
    "Los accidentes de tránsito son una de las principales causas de muerte violenta en el país.",
    "El 30% de los accidentes mortales están relacionados con el alcohol.",
    "Usar casco reduce hasta un 70% el riesgo de lesiones graves en motociclistas.",
    "Respetar los límites de velocidad puede salvar hasta 10 vidas al día en Ecuador.",
    "Por cada hora que avanza la noche, el riesgo de accidente fatal aumenta significativamente.",
    "Las distracciones al volante causan más del 25% de los accidentes a nivel mundial.",
    "Un peatón tiene 90% más probabilidad de sobrevivir si el vehículo circula a 30 km/h vs 50 km/h.",
    "En Ecuador, las zonas urbanas concentran más accidentes, pero las rurales tienen mayor letalidad.",
]

_SABIAS_QUE_VIALES: list[str] = [
    "La OMS estima que 1.3 millones de personas mueren al año en accidentes de tránsito en el mundo.",
    "Ecuador tiene una tasa de mortalidad vial superior al promedio de América Latina.",
    "El horario entre las 18:00 y 21:00 es el más crítico para accidentes con víctimas.",
    "Diciembre y enero suelen ser los meses con mayor número de accidentes por desplazamientos festivos.",
    "Los conductores jóvenes (18-25 años) tienen mayor probabilidad de verse involucrados en accidentes.",
    "Las lluvias incrementan hasta un 30% el riesgo de accidentes en ciertas provincias del Ecuador.",
    "La fatiga al conducir es responsable de aproximadamente el 20% de los accidentes en carretera.",
    "Revisar la presión de los neumáticos una vez al mes reduce el riesgo de reventones.",
    "En Ecuador, el exceso de velocidad es la causa principal de accidentes en carreteras.",
    "Usar luces bajas encendidas durante el día aumenta la visibilidad del vehículo.",
]


def sabias_que() -> str:
    """Devuelve un dato curioso aleatorio sobre seguridad vial."""
    opciones = _SABIAS_QUE + _SABIAS_QUE_VIALES
    return random.choice(opciones)


# =========================================================================
# INTERPRETACIÓN DE KPIS
# =========================================================================


def interpret_kpis(
    accidentes: float,
    fallecidos: float,
    lesionados: float,
    delta_acc: str | None = None,
) -> str:
    """Interpretación narrativa de los indicadores clave."""
    text = f"Durante el período seleccionado ocurrieron **{int(accidentes):,} accidentes**"

    if delta_acc:
        text += f", lo que representa una **variación del {delta_acc}** respecto al año anterior."

    dias = 365
    if accidentes > 0 and dias > 0:
        promedio_diario = accidentes / dias
        text += f"\n\nEsto equivale a un promedio de **{promedio_diario:.0f} accidentes por día**."

    if fallecidos > 0:
        text += f"\n\nLamentablemente, **{int(fallecidos):,} personas fallecieron**"
        text += f" y **{int(lesionados):,} resultaron lesionadas**."
        text += " Cada número representa una vida y una familia afectada."

    text += "\n\nEstas cifras nos recuerdan la importancia de adoptar una conducta responsable al volante."

    return text


def interpret_kpis_provincia(
    provincia: str,
    accidentes: float,
    fallecidos: float,
    lesionados: float,
    delta_acc: str | None = None,
) -> str:
    """Interpretación de KPIs para una provincia específica."""
    text = f"En **{provincia}** se registraron **{int(accidentes):,} accidentes**"
    if delta_acc:
        text += f" ({delta_acc} vs el año anterior)."

    if fallecidos > 0:
        text += f"\n\nHubo **{int(fallecidos):,} fallecidos** y **{int(lesionados):,} lesionados**."
    else:
        text += "\n\nNo se registraron fallecidos en los datos consultados."

    return text


# =========================================================================
# INTERPRETACIÓN TEMPORAL
# =========================================================================


def interpret_meses(df_mes: pd.DataFrame) -> str:
    """Analiza la distribución mensual de accidentes."""
    if df_mes.empty or "accidentes" not in df_mes.columns:
        return "No hay datos suficientes para analizar la distribución mensual."

    total = df_mes["accidentes"].sum()
    if total == 0:
        return "No se registraron accidentes en el período consultado."

    max_row = df_mes.loc[df_mes["accidentes"].idxmax()]
    min_row = df_mes.loc[df_mes["accidentes"].idxmin()]
    mes_max = max_row.get("mes", max_row.get("cod_mes", ""))
    mes_min = min_row.get("mes", min_row.get("cod_mes", ""))
    pct_max = (max_row["accidentes"] / total) * 100
    pct_min = (min_row["accidentes"] / total) * 100

    texto = (
        f"El mes con más accidentes es **{mes_max}** con **{int(max_row['accidentes']):,}** "
        f"({pct_max:.1f}% del total), mientras que **{mes_min}** registra la menor cantidad "
        f"({pct_min:.1f}% del total)."
    )

    # Estacionalidad
    meses_nombres = df_mes["mes"].tolist() if "mes" in df_mes.columns else []
    vacaciones = {"diciembre", "enero", "julio", "agosto"}
    presentes = {m.lower() for m in meses_nombres}
    if vacaciones & presentes:
        texto += (
            " Se observa un incremento en meses de vacaciones y feriados, "
            "posiblemente asociado a mayor movilidad y desplazamientos."
        )

    texto += (
        " Esta estacionalidad ayuda a las autoridades a planificar campañas preventivas "
        "en los meses de mayor riesgo."
    )

    return texto


def interpret_dias(df_dia: pd.DataFrame) -> str:
    """Analiza la distribución por día de la semana."""
    if df_dia.empty or "accidentes" not in df_dia.columns:
        return "No hay datos suficientes para analizar los patrones semanales."

    total = df_dia["accidentes"].sum()
    if total == 0:
        return ""

    max_row = df_dia.loc[df_dia["accidentes"].idxmax()]
    dia_max = max_row.get("dia", max_row.get("cod_dia", ""))
    pct_max = (max_row["accidentes"] / total) * 100

    texto = f"**{dia_max}** es el día con mayor siniestralidad ({pct_max:.1f}% de los accidentes de la semana)."

    # Clasificar días
    dias_list = df_dia["dia"].tolist() if "dia" in df_dia.columns else []
    fines = {d.lower() for d in dias_list if d.lower() in {"sábado", "sabado", "domingo"}}
    if fines:
        acc_fin = df_dia[df_dia["dia"].str.lower().isin({"sábado", "sabado", "domingo"})]["accidentes"].sum()
        pct_fin = (acc_fin / total) * 100
        texto += (
            f"\n\nLos fines de semana concentran el **{pct_fin:.1f}%** de los accidentes, "
            "lo que sugiere una relación con actividades recreativas, consumo de alcohol "
            "y mayor flujo vehicular."
        )
        texto += (
            " **Recomendación:** si conduces en fines de semana, extrema las precauciones, "
            "especialmente durante la noche y en zonas de alta movilidad."
        )
    else:
        texto += (
            " Los días laborales concentran la mayor parte de los accidentes, "
            "posiblemente por el alto flujo vehicular durante los desplazamientos al trabajo."
        )

    return texto


def interpret_horas(df_hora: pd.DataFrame) -> str:
    """Analiza la distribución por hora del día."""
    if df_hora.empty or "accidentes" not in df_hora.columns:
        return "No hay datos suficientes para analizar los horarios críticos."

    total = df_hora["accidentes"].sum()
    if total == 0:
        return ""

    max_row = df_hora.loc[df_hora["accidentes"].idxmax()]
    hora_max = max_row.get("hora", max_row.get("cod_hora", ""))
    pct_max = (max_row["accidentes"] / total) * 100

    texto = f"La hora más crítica es **{hora_max}** con el **{pct_max:.1f}%** de los accidentes."

    # Horario nocturno
    if "cod_hora" in df_hora.columns:
        nocturno = df_hora[df_hora["cod_hora"].between(18, 23) | df_hora["cod_hora"].between(0, 5)]
    elif "hora" in df_hora.columns and df_hora["hora"].dtype.kind in "if":
        nocturno = df_hora[df_hora["hora"].between(18, 23) | df_hora["hora"].between(0, 5)]
    else:
        nocturno = pd.DataFrame()

    if not nocturno.empty:
        pct_noche = (nocturno["accidentes"].sum() / total) * 100
        texto += (
            f"\n\nEl período nocturno (18:00 a 05:00) concentra el **{pct_noche:.1f}%** "
            "de los accidentes. La menor visibilidad, la fatiga y el consumo de alcohol "
            "son factores que incrementan el riesgo durante la noche."
        )
        texto += (
            " **Recomendación:** reduce la velocidad, usa luces bajas y evita conducir "
            "si has consumido alcohol."
        )

    return texto


# =========================================================================
# INTERPRETACIÓN GEOGRÁFICA
# =========================================================================


def interpret_provincias(df_prov: pd.DataFrame) -> str:
    """Analiza el ranking de provincias."""
    if df_prov.empty or "accidentes" not in df_prov.columns:
        return "No hay datos geográficos suficientes."

    total = df_prov["accidentes"].sum()
    if total == 0:
        return ""

    top = df_prov.head(3)
    pct_top = (top["accidentes"].sum() / total) * 100

    texto = f"Las **{len(top)} provincias** con más accidentes concentran el **{pct_top:.1f}%** del total."

    items = []
    for _, r in top.iterrows():
        pct = (r["accidentes"] / total) * 100
        items.append(f"{r['provincia']} ({int(r['accidentes']):,}, {pct:.1f}%)")
    texto += "\n\n" + "\n".join(f"- {i}" for i in items)

    # Provincia con más accidentes
    primera = top.iloc[0]
    texto += (
        f"\n\n**{primera['provincia']}** lidera las estadísticas con "
        f"{int(primera['accidentes']):,} accidentes. "
        "Esto puede estar relacionado con su densidad poblacional, actividad económica "
        "y flujo vehicular."
    )

    return texto


def interpret_zonas(df_zona: pd.DataFrame) -> str:
    """Analiza la distribución urbana/rural."""
    if df_zona.empty or "accidentes" not in df_zona.columns:
        return ""

    total = df_zona["accidentes"].sum()
    if total == 0:
        return ""

    texto = ""
    for _, r in df_zona.iterrows():
        pct = (r["accidentes"] / total) * 100
        texto += f"**{r['zona']}**: {int(r['accidentes']):,} ({pct:.1f}%)  \n"

    urbana = df_zona[df_zona["zona"].str.lower().str.contains("urb")]
    rural = df_zona[df_zona["zona"].str.lower().str.contains("rur")]
    if not urbana.empty and not rural.empty:
        pct_u = (urbana["accidentes"].sum() / total) * 100
        texto += (
            f"\nLa zona **urbana** concentra el **{pct_u:.1f}%** de los accidentes, "
            "lo que refleja la alta densidad vehicular en las ciudades."
        )

    return texto


def interpret_causas(df_causas: pd.DataFrame) -> str:
    """Analiza las causas principales."""
    if df_causas.empty or "accidentes" not in df_causas.columns:
        return ""

    total = df_causas["accidentes"].sum()
    if total == 0:
        return ""

    causa_col = next((c for c in df_causas.columns if c.lower() in {"causa", "causas"}), "causa")
    max_row = df_causas.iloc[0]
    pct = (max_row["accidentes"] / total) * 100

    texto = (
        f"La principal causa de accidentes es **{max_row[causa_col]}** "
        f"con **{int(max_row['accidentes']):,} casos** ({pct:.1f}% del total)."
    )

    if len(df_causas) > 1:
        segunda = df_causas.iloc[1]
        texto += (
            f" Le sigue **{segunda[causa_col]}** "
            f"con {int(segunda['accidentes']):,} accidentes."
        )

    # Recomendación según causa
    causa_baja = max_row[causa_col].lower()
    if "velocidad" in causa_baja:
        texto += (
            " **Recomendación:** respeta siempre los límites de velocidad. "
            "A mayor velocidad, menor capacidad de reacción y más graves son las consecuencias."
        )
    elif "alcohol" in causa_baja or "embriaguez" in causa_baja or "licor" in causa_baja:
        texto += (
            " **Recomendación:** si consumes alcohol, no conduzcas. "
            "Utiliza transporte público, taxi o designa un conductor responsable."
        )
    elif "distracción" in causa_baja or "celular" in causa_baja or "teléfono" in causa_baja:
        texto += (
            " **Recomendación:** guarda el teléfono mientras conduces. "
            "Una distracción de solo 2 segundos duplica el riesgo de accidente."
        )
    elif "señal" in causa_baja or "tránsito" in causa_baja or "semáforo" in causa_baja:
        texto += (
            " **Recomendación:** respeta siempre las señales de tránsito y semáforos. "
            "Son disposiciones diseñadas para proteger tu vida y la de los demás."
        )
    elif "peatón" in causa_baja or "atropello" in causa_baja:
        texto += (
            " **Recomendación:** cede siempre el paso al peatón. "
            "En zonas urbanas, reduce la velocidad y mantén atención constante."
        )
    else:
        texto += (
            " Conocer las causas es el primer paso para prevenir. "
            "Adoptar conductas seguras al volante reduce significativamente estos riesgos."
        )

    return texto


def interpret_clases(df_clases: pd.DataFrame) -> str:
    """Analiza los tipos de accidente."""
    if df_clases.empty or "accidentes" not in df_clases.columns:
        return ""

    total = df_clases["accidentes"].sum()
    if total == 0:
        return ""

    clase_col = next((c for c in df_clases.columns if c.lower() in {"clase", "clases"}), "clase")
    max_row = df_clases.iloc[0]
    pct = (max_row["accidentes"] / total) * 100

    texto = (
        f"El tipo de accidente más frecuente es **{max_row[clase_col]}** "
        f"con **{int(max_row['accidentes']):,} casos** ({pct:.1f}% del total)."
    )

    return texto


def interpret_tendencia_anual(df_anio: pd.DataFrame) -> str:
    """Interpreta la tendencia año a año."""
    if df_anio.empty or "accidentes" not in df_anio.columns or len(df_anio) < 2:
        if len(df_anio) == 1:
            return f"En el año **{df_anio.iloc[0].get('anio', '')}** se registraron **{int(df_anio.iloc[0]['accidentes']):,} accidentes**."
        return "Se necesitan datos de al menos dos años para analizar la tendencia."

    primero = df_anio.iloc[0]
    ultimo = df_anio.iloc[-1]
    diff = ultimo["accidentes"] - primero["accidentes"]
    pct = (diff / primero["accidentes"]) * 100 if primero["accidentes"] > 0 else 0

    if pct > 0:
        texto = (
            f"La tendencia muestra un **aumento del {abs(pct):.1f}%** entre "
            f"{int(primero['anio'])} y {int(ultimo['anio'])}. "
            "Esto subraya la necesidad de reforzar las campañas de prevención."
        )
    elif pct < 0:
        texto = (
            f"Se observa una **reducción del {abs(pct):.1f}%** entre "
            f"{int(primero['anio'])} y {int(ultimo['anio'])}. "
            "Es importante mantener las estrategias que han contribuido a esta mejora."
        )
    else:
        texto = (
            f"Los accidentes se han mantenido **estables** entre "
            f"{int(primero['anio'])} y {int(ultimo['anio'])}."
        )

    return texto


# =========================================================================
# INTERPRETACIÓN OLAP (Consultas)
# =========================================================================


def interpret_olap(dimension: str, metrica: str, df: pd.DataFrame) -> str:
    """Interpreta el resultado de una consulta OLAP."""
    if df.empty or "valor" not in df.columns:
        return "La consulta no devolvió resultados. Intenta con otros filtros."

    total = df["valor"].sum()
    if total == 0:
        return f"La {metrica.lower()} es cero para todos los valores de {dimension.lower()} consultados."

    top = df.iloc[0]
    pct = (top["valor"] / total) * 100 if total > 0 else 0
    categoria = top.get("categoria", "")

    texto = (
        f"La consulta indica que **{categoria}** lidera en **{metrica.lower()}** "
        f"con **{int(top['valor']):,}** ({pct:.1f}% del total)."
    )

    if len(df) > 1:
        texto += f" Le siguen **{df.iloc[1].get('categoria', '')}** y **{df.iloc[2].get('categoria', '')}**."

    # Recomendaciones contextuales
    dim_baja = dimension.lower()
    if dim_baja == "provincia":
        texto += (
            " Esto ayuda a identificar las zonas geográficas que requieren "
            "mayor atención en campañas de seguridad vial."
        )
    elif dim_baja == "causa":
        texto += (
            " Identificar las causas principales permite diseñar campañas "
            "educativas específicas para reducir la siniestralidad."
        )
    elif dim_baja in ("mes", "hora"):
        texto += (
            " Conocer los momentos críticos ayuda a planificar controles "
            "y campañas preventivas en los horarios de mayor riesgo."
        )

    return texto


# =========================================================================
# RECOMENDACIONES PREVENTIVAS GENERALES
# =========================================================================


_RECOMENDACIONES = [
    "Respeta siempre los límites de velocidad. Llegar unos minutos antes no vale una vida.",
    "Si consumes alcohol, no conduzcas. Usa transporte público, taxi o designa un conductor.",
    "Usa siempre el cinturón de seguridad, en todos los asientos del vehículo.",
    "No uses el teléfono móvil mientras conduces. Si es urgente, estaciónate en un lugar seguro.",
    "Revisa el estado de tus neumáticos, frenos y luces antes de un viaje largo.",
    "Respeta las señales de tránsito y los semáforos. Están ahí para protegerte.",
    "Mantén una distancia prudente con el vehículo que te antecede.",
    "En carretera, adelanta solo cuando sea seguro y en los lugares permitidos.",
    "Si conduces de noche, reduce la velocidad y enciende las luces bajas.",
    "La fatiga al volante es peligrosa: si sientes sueño, descansa antes de continuar.",
    "Los peatones tienen la prioridad. Cede siempre el paso en los cruces peatonales.",
    "Respeta los pasos peatonales y no estaciones sobre ellos.",
    "Usa casco certificado si conduces motocicleta o bicicleta.",
    "No circules en sentido contrario ni invadas el carril exclusivo del bus.",
    "Mantén tu vehículo en buen estado mecánico: frenos, luces, neumáticos y suspensión.",
]


def recomendacion_aleatoria() -> str:
    """Devuelve una recomendación preventiva aleatoria."""
    return random.choice(_RECOMENDACIONES)


def recomendacion_para_provincia(provincia: str, causa_principal: str = "") -> str:
    """Genera una recomendación personalizada para una provincia."""
    texto = f"En **{provincia}**"

    if "velocidad" in causa_principal.lower():
        texto += (
            " predominan los accidentes por exceso de velocidad. "
            "Se recomienda reforzar los controles de velocidad y respetar los límites "
            "establecidos, especialmente en vías interprovinciales."
        )
    elif "alcohol" in causa_principal.lower() or "embriaguez" in causa_principal.lower():
        texto += (
            " los accidentes relacionados con alcohol son frecuentes. "
            "Se recomienda planificar con anticipación: designa un conductor, usa taxi "
            "o transporte público si has consumido bebidas alcohólicas."
        )
    elif "distracción" in causa_principal.lower():
        texto += (
            " las distracciones al volante son una causa importante de accidentes. "
            "Evita usar el teléfono y mantén toda tu atención en la vía."
        )
    elif causa_principal:
        texto += (
            f" la principal causa de accidentes es **{causa_principal}**. "
            "Conocer esta información te permite tomar precauciones específicas al conducir."
        )
    else:
        texto += (
            " la seguridad vial es responsabilidad de todos. Respeta las normas, "
            "usa el cinturón de seguridad y nunca conduzcas bajo efectos del alcohol."
        )

    return texto


# =========================================================================
# RIESGO Y ALERTAS
# =========================================================================

_NIVEL_RIESGO = {
    "bajo": ("🟢", "Riesgo bajo"),
    "medio": ("🟡", "Riesgo moderado"),
    "alto": ("🟠", "Riesgo alto"),
    "crítico": ("🔴", "Riesgo crítico"),
}


def nivel_riesgo(pct: float) -> str:
    """Clasifica el nivel de riesgo según un porcentaje."""
    if pct < 5:
        return "bajo"
    if pct < 10:
        return "medio"
    if pct < 20:
        return "alto"
    return "crítico"


def barra_riesgo_html(valor: float, max_valor: float, etiqueta: str) -> str:
    """Genera HTML para una barra de riesgo visual."""
    pct = (valor / max_valor) * 100 if max_valor > 0 else 0
    color = "#22c55e" if pct < 25 else ("#eab308" if pct < 50 else ("#f97316" if pct < 75 else "#ef4444"))
    nivel = nivel_riesgo(pct)
    icono, texto_nivel = _NIVEL_RIESGO.get(nivel, ("", ""))
    return f"""
    <div style="margin-bottom:12px">
      <div style="display:flex;justify-content:space-between;font-size:14px">
        <span>{etiqueta}</span>
        <span>{icono} {texto_nivel}</span>
      </div>
      <div style="background:#e5e7eb;border-radius:8px;height:12px;overflow:hidden">
        <div style="background:{color};width:{pct:.0f}%;height:100%;border-radius:8px;transition:width 0.5s"></div>
      </div>
      <div style="text-align:right;font-size:12px;color:#6b7280">{int(valor):,} accidentes</div>
    </div>
    """


# =========================================================================
# SUGERENCIAS DE CONSULTAS
# =========================================================================

SUGERENCIAS_CONSULTAS: list[tuple[str, str, str]] = [
    ("Accidentes por provincia", "Provincia", "Accidentes"),
    ("Fallecidos por causa", "Causa", "Fallecidos"),
    ("Lesionados por tipo de accidente", "Clase", "Lesionados"),
    ("Accidentes por mes", "Mes", "Accidentes"),
    ("Accidentes por zona (urbana/rural)", "Zona", "Accidentes"),
    ("Víctimas por provincia", "Provincia", "Víctimas"),
    ("Accidentes por hora del día", "Hora", "Accidentes"),
    ("Fallecidos por provincia", "Provincia", "Fallecidos"),
    ("Lesionados por causa", "Causa", "Lesionados"),
    ("Accidentes por año", "Año", "Accidentes"),
]

# =========================================================================
# CATEGORIZACIÓN DEL ASISTENTE
# =========================================================================

SUGERENCIAS_ASISTENTE: dict[str, list[str]] = {
    "Por provincia": [
        "¿Qué provincia tuvo más accidentes en 2023?",
        "¿Cuántos accidentes hubo en Quito durante 2022?",
        "Compara Guayas y Pichincha",
        "¿Cuál es la provincia con más fallecidos?",
    ],
    "Por tiempo": [
        "¿En qué meses ocurren más accidentes?",
        "¿Qué día de la semana hay más accidentes?",
        "¿En qué horario ocurren más accidentes?",
        "¿Cómo ha sido la tendencia de accidentes por año?",
    ],
    "Por causa y tipo": [
        "¿Cuáles son las causas más frecuentes?",
        "Muéstrame los accidentes por clase",
        "¿Qué causa produjo más fallecidos?",
        "¿Cuántos accidentes fueron por exceso de velocidad?",
    ],
    "Consultas combinadas": [
        "Accidentes en Guayas por exceso de velocidad en 2023",
        "Fallecidos en accidentes nocturnos en Pichincha",
        "Compara accidentes en zona urbana vs rural",
        "¿Cuántos lesionados hubo en accidentes de moto?",
    ],
}
