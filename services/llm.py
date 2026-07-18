"""
Cliente LLM vía OpenRouter (API compatible con OpenAI).

Responsabilidades:
- Crear el cliente HTTP hacia OpenRouter
- Enviar mensajes chat (system + user)
- Devolver el texto de respuesta del modelo

El modelo NO está fijo: se recibe como parámetro o se toma de config.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from openai import OpenAI

from config import (
    DEFAULT_LLM_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    OPENROUTER_API_KEY,
    OPENROUTER_APP_NAME,
    OPENROUTER_BASE_URL,
    OPENROUTER_SITE_URL,
)


class LLMError(Exception):
    """Error controlado al invocar el proveedor LLM."""


@lru_cache(maxsize=1)
def get_openrouter_client() -> OpenAI:
    """
    Devuelve un cliente OpenAI apuntando a OpenRouter.

    Se cachea a nivel de proceso; Streamlit también puede
    envolverlo con st.cache_resource en la página si se desea.
    """
    if not OPENROUTER_API_KEY:
        raise LLMError(
            "Falta OPENROUTER_API_KEY en .streamlit/secrets.toml. "
            "Obtén una clave en https://openrouter.ai/keys"
        )

    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": OPENROUTER_SITE_URL,
            "X-Title": OPENROUTER_APP_NAME,
        },
    )


def chat_completion(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Ejecuta una completación de chat y devuelve el contenido textual.

    Parameters
    ----------
    messages : list[dict]
        Lista de mensajes con roles 'system', 'user', 'assistant'.
    model : str, optional
        ID del modelo en OpenRouter (ej. 'qwen/qwen3-coder:free').
    temperature : float, optional
        Creatividad del modelo (bajo = más determinista para SQL).
    max_tokens : int, optional
        Tope de tokens de salida.
    """
    client = get_openrouter_client()
    selected_model = model or DEFAULT_LLM_MODEL

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=messages,
            temperature=LLM_TEMPERATURE if temperature is None else temperature,
            max_tokens=LLM_MAX_TOKENS if max_tokens is None else max_tokens,
        )
    except Exception as exc:  # noqa: BLE001 — se reempaqueta como LLMError
        raise LLMError(f"Error al llamar a OpenRouter ({selected_model}): {exc}") from exc

    if not response.choices:
        raise LLMError("OpenRouter no devolvió ninguna respuesta (choices vacío).")

    content = response.choices[0].message.content
    if content is None or not str(content).strip():
        raise LLMError("El modelo devolvió una respuesta vacía.")

    return str(content).strip()


def is_llm_configured() -> bool:
    """Indica si hay API key configurada para OpenRouter."""
    return bool(OPENROUTER_API_KEY)
