"""
Generación y validación de SQL a partir de lenguaje natural.

Flujo:
1. Cargar system prompt + esquema del DW
2. Pedir al LLM un JSON con {sql, chart_hint, reasoning}
3. Validar que el SQL sea solo de lectura y seguro
4. Devolver el SQL limpio o un error de validación
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from services.llm import LLMError, chat_completion
from utils.schema import TABLAS_PERMITIDAS, get_schema_for_prompt

# Ruta del system prompt (relativa a la raíz del proyecto)
_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
_SYSTEM_PROMPT_PATH = _PROMPTS_DIR / "system_prompt.txt"
_EXPLANATION_PROMPT_PATH = _PROMPTS_DIR / "explanation_prompt.txt"

# Palabras clave peligrosas (solo lectura permitida)
_FORBIDDEN_KEYWORDS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\b",
    r"\bMERGE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bDENY\b",
    r"\bBACKUP\b",
    r"\bRESTORE\b",
    r"\bSHUTDOWN\b",
    r"\bWAITFOR\b",
    r"\bOPENROWSET\b",
    r"\bOPENDATASOURCE\b",
    r"\bOPENQUERY\b",
    r"\bxp_\w+",
    r"\bsp_\w+",
    r"\bINTO\b",  # bloquea SELECT INTO / INSERT INTO
    r"\bBULK\b",
    r"\bDBCC\b",
]

# Chart hints aceptados
_VALID_HINTS = {"bar", "line", "pie", "map", "table"}


@dataclass
class SQLGenerationResult:
    """Resultado de la generación Text-to-SQL."""

    sql: str
    chart_hint: str
    reasoning: str
    raw_response: str


@dataclass
class SQLValidationResult:
    """Resultado de la validación de seguridad del SQL."""

    is_valid: bool
    sql: str
    error: Optional[str] = None


def _load_prompt(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el prompt: {path}")
    return path.read_text(encoding="utf-8")


def build_system_prompt() -> str:
    """Construye el system prompt inyectando el esquema del DW."""
    template = _load_prompt(_SYSTEM_PROMPT_PATH)
    return template.format(schema=get_schema_for_prompt())


def _strip_code_fences(text: str) -> str:
    """Elimina fences markdown ```json ... ``` o ```sql ... ```."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json|sql|JSON|SQL)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _parse_llm_json(raw: str) -> dict:
    """Extrae un objeto JSON de la respuesta del modelo."""
    cleaned = _strip_code_fences(raw)

    # Intento directo
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Buscar el primer objeto {...} en el texto
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise LLMError(f"No se pudo parsear el JSON del modelo: {exc}") from exc

    raise LLMError("El modelo no devolvió un JSON válido con la consulta SQL.")


def remove_sql_comments(sql: str) -> str:
    """Elimina comentarios -- y /* */ para validar el SQL real."""
    # Comentarios de bloque
    without_block = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    # Comentarios de línea
    without_line = re.sub(r"--.*?$", " ", without_block, flags=re.MULTILINE)
    return without_line


def validate_sql(sql: str) -> SQLValidationResult:
    """
    Valida que el SQL sea seguro y de solo lectura.

    Rechaza cualquier cosa que no sea SELECT / WITH ... SELECT,
    múltiples sentencias, o palabras clave peligrosas.
    """
    if not sql or not str(sql).strip():
        return SQLValidationResult(False, "", "SQL vacío.")

    # Limpiar fences si el modelo las dejó en el campo sql
    cleaned = _strip_code_fences(sql)
    cleaned = cleaned.strip().rstrip(";").strip()

    no_comments = remove_sql_comments(cleaned)
    compact = re.sub(r"\s+", " ", no_comments).strip()

    if not compact:
        return SQLValidationResult(False, cleaned, "SQL vacío tras limpiar comentarios.")

    # Una sola sentencia (sin ; internos)
    if ";" in compact:
        return SQLValidationResult(
            False, cleaned, "No se permiten múltiples sentencias SQL."
        )

    upper = compact.upper()

    # Debe comenzar con SELECT o WITH
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        return SQLValidationResult(
            False,
            cleaned,
            "Solo se permiten consultas SELECT (o WITH ... SELECT).",
        )

    # Palabras prohibidas
    for pattern in _FORBIDDEN_KEYWORDS:
        if re.search(pattern, upper, flags=re.IGNORECASE):
            keyword = pattern.replace(r"\b", "").replace(r"\w+", "")
            return SQLValidationResult(
                False,
                cleaned,
                f"SQL rechazado: contiene la palabra/patrón prohibido ({keyword}).",
            )

    # WITH debe terminar en SELECT
    if upper.startswith("WITH") and " SELECT " not in f" {upper} ":
        return SQLValidationResult(
            False, cleaned, "Las CTE (WITH) deben incluir un SELECT final."
        )

    # Tablas: si aparecen nombres tipo Identificador, deben ser permitidas
    # (validación best-effort; no es un parser SQL completo)
    table_refs = re.findall(
        r"\b(?:FROM|JOIN)\s+([\[\]\w\.]+)",
        compact,
        flags=re.IGNORECASE,
    )
    for ref in table_refs:
        # Quitar esquema/dbo y corchetes
        name = ref.split(".")[-1].replace("[", "").replace("]", "")
        if name.upper() in {t.upper() for t in TABLAS_PERMITIDAS}:
            continue
        # Alias simples de una letra se ignoran (ya resueltos en FROM)
        if len(name) <= 2 and name.isalpha():
            continue
        # Si parece un nombre de tabla desconocido, rechazar
        if re.match(r"^[A-Za-z_][\w]*$", name) and name[0].isupper():
            if name not in TABLAS_PERMITIDAS:
                return SQLValidationResult(
                    False,
                    cleaned,
                    f"Tabla no permitida en la consulta: {name}",
                )

    return SQLValidationResult(True, cleaned, None)


def generate_sql(
    question: str,
    model: Optional[str] = None,
) -> SQLGenerationResult:
    """
    Genera SQL a partir de una pregunta en lenguaje natural.

    No ejecuta la consulta; solo genera y parsea la respuesta del LLM.
    """
    system_prompt = build_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question.strip()},
    ]

    raw = chat_completion(messages, model=model, temperature=0.05)
    data = _parse_llm_json(raw)

    sql = str(data.get("sql", "")).strip()
    chart_hint = str(data.get("chart_hint", "table")).strip().lower()
    reasoning = str(data.get("reasoning", "")).strip()

    if chart_hint not in _VALID_HINTS:
        chart_hint = "table"

    if not sql:
        raise LLMError("El modelo no incluyó el campo 'sql' en la respuesta.")

    return SQLGenerationResult(
        sql=sql,
        chart_hint=chart_hint,
        reasoning=reasoning,
        raw_response=raw,
    )


def _is_garbled_text(text: str) -> bool:
    """
    Detecta si el texto generado por el LLM es basura ilegible.

    Heurísticas:
    - Contiene <unk> (token desconocido)
    - Contiene palabras excesivamente largas (>30 chars) sin espacios
    - La proporción de caracteres no-alfabéticos es muy alta
    """
    if "<unk>" in text:
        return True

    words = text.split()
    for w in words:
        if len(w) > 30:
            return True

    if len(text) > 0:
        alpha = sum(1 for c in text if c.isalpha() or c.isspace())
        ratio = alpha / len(text)
        if ratio < 0.5:
            return True

    return False


def _fallback_explanation(
    question: str,
    result_preview: str,
    row_count: int,
) -> str:
    """Genera una explicación de respaldo sin usar el LLM."""
    lines = [l for l in result_preview.strip().split("\n") if l.strip()]
    if not lines:
        return "No se encontraron datos para tu consulta."

    header = lines[0]
    columns = [c.strip() for c in header.split() if c.strip()]

    if row_count == 0:
        return "La consulta no devolvió filas."

    summary = (
        f"Se obtuvieron {row_count} registro(s) con los siguientes "
        f"campos: {', '.join(columns[:6])}"
        f"{' y más.' if len(columns) > 6 else '.'}"
    )

    first_row = lines[1].split() if len(lines) > 1 else []
    if first_row and len(first_row) > 0:
        summary += f" El primer valor es {first_row[0]}."

    return summary


def generate_explanation(
    question: str,
    sql: str,
    result_preview: str,
    model: Optional[str] = None,
) -> str:
    """
    Genera una explicación en lenguaje natural de los resultados.

    Si el LLM devuelve texto corrupto/ilegible, se usa una explicación
    de respaldo basada en los datos.
    """
    system_prompt = _load_prompt(_EXPLANATION_PROMPT_PATH)
    user_content = (
        f"Pregunta del usuario:\n{question}\n\n"
        f"SQL ejecutado:\n{sql}\n\n"
        f"Resultados (muestra tabular):\n{result_preview}\n"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    raw = chat_completion(messages, model=model, temperature=0.3, max_tokens=600)

    if _is_garbled_text(raw):
        row_count = len(result_preview.strip().split("\n")) - 1  # restar header
        row_count = max(row_count, 0)
        return _fallback_explanation(question, result_preview, row_count)

    return raw
