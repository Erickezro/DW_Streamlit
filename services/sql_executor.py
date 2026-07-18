"""
Ejecución segura de consultas SQL generadas por el asistente.

Solo ejecuta SQL previamente validado (SELECT de lectura).
Reutiliza el engine SQLAlchemy de db.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
from sqlalchemy import text

from config import ASSISTANT_MAX_ROWS
from db import get_connection
from services.sql_generator import SQLValidationResult, validate_sql


@dataclass
class SQLExecutionResult:
    """Resultado de la ejecución de una consulta validada."""

    success: bool
    dataframe: pd.DataFrame
    sql: str
    error: Optional[str] = None
    row_count: int = 0


def execute_readonly_sql(
    sql: str,
    max_rows: Optional[int] = None,
) -> SQLExecutionResult:
    """
    Valida y ejecuta una consulta de solo lectura contra Azure SQL.

    Parameters
    ----------
    sql : str
        Consulta generada por el LLM.
    max_rows : int, optional
        Tope de filas a devolver en el DataFrame (por defecto ASSISTANT_MAX_ROWS).
        El límite se aplica en memoria tras la ejecución para no alterar
        la semántica de ORDER BY / TOP del SQL original.
    """
    limit = max_rows if max_rows is not None else ASSISTANT_MAX_ROWS

    validation: SQLValidationResult = validate_sql(sql)
    if not validation.is_valid:
        return SQLExecutionResult(
            success=False,
            dataframe=pd.DataFrame(),
            sql=sql,
            error=validation.error or "SQL inválido.",
            row_count=0,
        )

    safe_sql = validation.sql
    engine = get_connection()

    try:
        with engine.connect() as conn:
            # Timeout de lectura para evitar consultas demasiado pesadas
            conn = conn.execution_options(timeout=30)
            result = conn.execute(text(safe_sql))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as exc:  # noqa: BLE001
        return SQLExecutionResult(
            success=False,
            dataframe=pd.DataFrame(),
            sql=safe_sql,
            error=f"Error al ejecutar la consulta en Azure SQL: {exc}",
            row_count=0,
        )

    if limit and len(df) > limit:
        df = df.head(limit).copy()

    return SQLExecutionResult(
        success=True,
        dataframe=df,
        sql=safe_sql,
        error=None,
        row_count=len(df),
    )


def dataframe_preview_for_llm(df: pd.DataFrame, max_rows: int = 15) -> str:
    """
    Serializa un DataFrame a texto compacto para el prompt de explicación.
    """
    if df is None or df.empty:
        return "(sin filas)"

    preview = df.head(max_rows).copy()
    for col in preview.select_dtypes(include="number").columns:
        preview[col] = preview[col].map(
            lambda x: f"{x:.2f}" if isinstance(x, float) else x
        )
    return preview.to_string(index=False)
