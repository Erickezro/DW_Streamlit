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

# Modelos GRATUITOS de OpenRouter (pricing $0 — id con sufijo :free).
# Catálogo actualizado desde https://openrouter.ai/models?max_price=0
# Para agregar o quitar, edita este diccionario (solo IDs con :free o openrouter/free).
LLM_MODELS = {
    "OpenRouter Free Router": "openrouter/free",
    "Qwen3 Coder (free)": "qwen/qwen3-coder:free",
    "Qwen3 Next 80B (free)": "qwen/qwen3-next-80b-a3b-instruct:free",
    "Llama 3.3 70B (free)": "meta-llama/llama-3.3-70b-instruct:free",
    "Gemma 4 31B (free)": "google/gemma-4-31b-it:free",
    "GPT-OSS 20B (free)": "openai/gpt-oss-20b:free",
    "Nemotron Nano 30B (free)": "nvidia/nemotron-3-nano-30b-a3b:free",
}

# Modelo por defecto (gratuito). Puede sobreescribirse en secrets con LLM_MODEL.
DEFAULT_LLM_MODEL = st.secrets.get("LLM_MODEL", "openrouter/free")

# Parámetros de generación
LLM_TEMPERATURE = float(st.secrets.get("LLM_TEMPERATURE", 0.1))
LLM_MAX_TOKENS = int(st.secrets.get("LLM_MAX_TOKENS", 1500))

# Límite de filas al ejecutar SQL del asistente
ASSISTANT_MAX_ROWS = int(st.secrets.get("ASSISTANT_MAX_ROWS", 200))
