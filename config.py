import streamlit as st

# ---------------------------------------------------------------------------
# Conexión Azure SQL (Data Warehouse)
# ---------------------------------------------------------------------------
SERVER = st.secrets["SERVER"]
DATABASE = st.secrets["DATABASE"]
USERNAME = st.secrets["USERNAME"]
PASSWORD = st.secrets["PASSWORD"]

# ---------------------------------------------------------------------------
# OpenRouter (LLM para el Asistente Inteligente)
# ---------------------------------------------------------------------------
# Clave: agregar OPENROUTER_API_KEY en .streamlit/secrets.toml
# Documentación: https://openrouter.ai/docs
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Identificadores opcionales para rankings de OpenRouter
OPENROUTER_SITE_URL = st.secrets.get("OPENROUTER_SITE_URL", "http://localhost:8501")
OPENROUTER_APP_NAME = st.secrets.get("OPENROUTER_APP_NAME", "DW Accidentes Ecuador")

# Modelos disponibles (etiqueta visible → id OpenRouter).
# Para cambiar el modelo por defecto o agregar uno nuevo, edita este diccionario.
LLM_MODELS = {
    "DeepSeek Chat": "deepseek/deepseek-chat",
    "DeepSeek R1": "deepseek/deepseek-r1",
    "Qwen 2.5 72B": "qwen/qwen-2.5-72b-instruct",
    "Llama 3.3 70B": "meta-llama/llama-3.3-70b-instruct",
    "GPT-4o mini": "openai/gpt-4o-mini",
    "Gemma 2 9B": "google/gemma-2-9b-it",
}

# Modelo por defecto (puede sobreescribirse en secrets con LLM_MODEL)
DEFAULT_LLM_MODEL = st.secrets.get("LLM_MODEL", "deepseek/deepseek-chat")

# Parámetros de generación
LLM_TEMPERATURE = float(st.secrets.get("LLM_TEMPERATURE", 0.1))
LLM_MAX_TOKENS = int(st.secrets.get("LLM_MAX_TOKENS", 1500))

# Límite de filas al ejecutar SQL del asistente
ASSISTANT_MAX_ROWS = int(st.secrets.get("ASSISTANT_MAX_ROWS", 200))
