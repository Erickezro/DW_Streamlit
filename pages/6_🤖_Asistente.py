"""
Página: Asistente Inteligente (Text-to-SQL).

Flujo de la UI:
1. El usuario escribe una pregunta en lenguaje natural.
2. El LLM genera SQL de solo lectura.
3. Se valida y ejecuta en Azure SQL.
4. El LLM explica los resultados.
5. Streamlit muestra explicación + tabla + gráfico.
6. El historial de la sesión se guarda en st.session_state.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from config import DEFAULT_LLM_MODEL, LLM_MODELS
from services.charts import build_chart
from services.llm import LLMError, is_llm_configured
from services.sql_executor import dataframe_preview_for_llm, execute_readonly_sql
from services.sql_generator import generate_explanation, generate_sql, validate_sql

# ---------------------------------------------------------------------------
# Estado de sesión
# ---------------------------------------------------------------------------
HISTORY_KEY = "assistant_history"
MODEL_KEY = "assistant_model"
PENDING_KEY = "assistant_pending_question"


def _init_state() -> None:
    if HISTORY_KEY not in st.session_state:
        st.session_state[HISTORY_KEY] = []
    if MODEL_KEY not in st.session_state:
        # Resolver etiqueta a partir del id por defecto
        default_label = next(
            (label for label, mid in LLM_MODELS.items() if mid == DEFAULT_LLM_MODEL),
            next(iter(LLM_MODELS)),
        )
        st.session_state[MODEL_KEY] = default_label
    if PENDING_KEY not in st.session_state:
        st.session_state[PENDING_KEY] = None


def _selected_model_id() -> str:
    label = st.session_state.get(MODEL_KEY, next(iter(LLM_MODELS)))
    return LLM_MODELS.get(label, DEFAULT_LLM_MODEL)


def _render_result_block(entry: dict[str, Any]) -> None:
    """Renderiza explicación, SQL, tabla y gráfico de una respuesta."""
    st.markdown(entry.get("explanation") or "_Sin explicación_")

    with st.expander("Ver SQL generado", expanded=False):
        st.code(entry.get("sql") or "", language="sql")
        if entry.get("reasoning"):
            st.caption(entry["reasoning"])

    df = entry.get("dataframe")
    if df is not None and not df.empty:
        col_table, col_chart = st.columns([1, 1.2])
        with col_table:
            st.markdown("**Tabla de resultados**")
            st.dataframe(df, width="stretch", hide_index=True)
        with col_chart:
            st.markdown("**Visualización**")
            # Se reconstruye en cada rerun (los Figure de Plotly
            # no siempre se serializan bien en session_state).
            fig = build_chart(
                df,
                chart_hint=entry.get("chart_hint", "table"),
                title="Resultado",
            )
            if fig is not None:
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No se pudo generar un gráfico automático para este resultado.")
    elif entry.get("error"):
        st.error(entry["error"])
    else:
        st.warning("La consulta no devolvió filas.")


def _process_question(question: str) -> dict[str, Any]:
    """
    Pipeline completo: pregunta → SQL → validación → ejecución → explicación.
    """
    model_id = _selected_model_id()
    entry: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "question": question,
        "model": model_id,
        "sql": "",
        "chart_hint": "table",
        "reasoning": "",
        "explanation": "",
        "dataframe": None,
        "error": None,
        "success": False,
    }

    try:
        gen = generate_sql(question, model=model_id)
        entry["sql"] = gen.sql
        entry["chart_hint"] = gen.chart_hint
        entry["reasoning"] = gen.reasoning

        validation = validate_sql(gen.sql)
        if not validation.is_valid:
            entry["error"] = f"SQL rechazado por seguridad: {validation.error}"
            entry["explanation"] = (
                "No pude ejecutar la consulta porque el SQL generado "
                "no superó las validaciones de seguridad (solo se permiten SELECT)."
            )
            return entry

        execution = execute_readonly_sql(validation.sql)
        entry["sql"] = execution.sql
        entry["dataframe"] = execution.dataframe

        if not execution.success:
            entry["error"] = execution.error
            entry["explanation"] = (
                "La consulta se generó, pero falló al ejecutarse en Azure SQL. "
                f"Detalle: {execution.error}"
            )
            return entry

        preview = dataframe_preview_for_llm(execution.dataframe)
        entry["explanation"] = generate_explanation(
            question=question,
            sql=execution.sql,
            result_preview=preview,
            model=model_id,
        )
        entry["success"] = True
        return entry

    except LLMError as exc:
        entry["error"] = str(exc)
        entry["explanation"] = f"Error del modelo LLM: {exc}"
        return entry
    except Exception as exc:  # noqa: BLE001
        entry["error"] = str(exc)
        entry["explanation"] = f"Error inesperado en el asistente: {exc}"
        return entry


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
_init_state()

st.title("Asistente inteligente")
st.markdown(
    """
Pregunta en lenguaje natural sobre el Data Warehouse de accidentes de tránsito en Ecuador.
El sistema genera SQL de solo lectura, lo ejecuta en Azure SQL y te muestra una explicación,
una tabla y un gráfico automático.

**No necesitas escribir SQL.**
"""
)

# ---- Sidebar de la página (modelo + ejemplos) ----
with st.sidebar:
    st.divider()
    st.subheader("Asistente")
    st.selectbox(
        "Modelo LLM (OpenRouter)",
        options=list(LLM_MODELS.keys()),
        key=MODEL_KEY,
        help="Cambia el modelo sin tocar el código. Los IDs se definen en config.py.",
    )
    st.caption(f"ID: `{_selected_model_id()}`")

    if st.button("Limpiar historial", width="stretch"):
        st.session_state[HISTORY_KEY] = []
        st.session_state[PENDING_KEY] = None
        st.rerun()

# ---- Configuración LLM ----
if not is_llm_configured():
    st.error(
        "Falta configurar **OPENROUTER_API_KEY** en `.streamlit/secrets.toml`.\n\n"
        "Ejemplo:\n"
        "```toml\nOPENROUTER_API_KEY = \"sk-or-...\"\n"
        "LLM_MODEL = \"deepseek/deepseek-chat\"\n```"
    )
    st.stop()

# ---- Sugerencias iniciales ----
SUGGESTIONS = [
    "¿Qué provincia tuvo más accidentes en 2023?",
    "¿Cuáles son las causas más frecuentes?",
    "¿En qué meses ocurren más accidentes?",
    "¿Cuántos accidentes hubo en Quito durante 2022?",
    "Muéstrame los accidentes por clase",
    "Compara Guayas y Pichincha",
]

if not st.session_state[HISTORY_KEY]:
    st.markdown("#### Prueba con una pregunta")
    selected = st.pills(
        "Sugerencias",
        options=SUGGESTIONS,
        selection_mode="single",
        label_visibility="collapsed",
    )
    if selected:
        st.session_state[PENDING_KEY] = selected
        st.rerun()

# ---- Historial de la sesión ----
history: list[dict[str, Any]] = st.session_state[HISTORY_KEY]

for idx, entry in enumerate(history):
    with st.chat_message("user"):
        st.markdown(entry["question"])
    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        _render_result_block(entry)
        # Reconsultar esta pregunta
        if st.button(
            "Volver a consultar",
            key=f"replay_{idx}_{entry.get('timestamp', idx)}",
            help="Ejecuta de nuevo esta pregunta con el modelo actual",
        ):
            st.session_state[PENDING_KEY] = entry["question"]
            st.rerun()

# ---- Entrada de chat ----
prompt = st.chat_input(
    "Escribe tu pregunta sobre accidentes en Ecuador…",
    submit_mode="disable",
)

# Prioridad: pregunta pendiente (sugerencia o reconsulta) o chat_input
question = st.session_state[PENDING_KEY] or prompt
if st.session_state[PENDING_KEY]:
    st.session_state[PENDING_KEY] = None

if question:
    question = str(question).strip()
    if question:
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            with st.spinner("Generando SQL, consultando Azure SQL y preparando la respuesta…"):
                entry = _process_question(question)
            _render_result_block(entry)

        st.session_state[HISTORY_KEY].append(entry)
        # Evitar reprocesar el mismo prompt en el siguiente rerun accidental
        st.rerun()
