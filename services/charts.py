"""
Generación automática de visualizaciones a partir del resultado SQL.

Heurísticas:
- provincias → mapa coroplético (si hay geojson)
- fechas / año / mes / hora → línea
- categorías con pocas filas → pie o barras
- dos columnas (categoría + valor) → barras
- fallback → barras o tabla
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Columnas que sugieren geografía provincial
_PROVINCIA_COLS = {"provincia", "provincias", "province"}

# Columnas temporales
_TIME_COLS = {
    "anio",
    "año",
    "year",
    "mes",
    "month",
    "dia",
    "día",
    "day",
    "hora",
    "hour",
    "fecha",
    "date",
    "cod_mes",
    "cod_dia",
    "cod_hora",
}

_GEOJSON_PATH = Path("data/ecuador_provincias.geojson")


def _normalize_name(nombre: str) -> str:
    nombre = str(nombre).upper().strip()
    return (
        unicodedata.normalize("NFKD", nombre)
        .encode("ascii", "ignore")
        .decode("ascii")
    )


def _find_column(df: pd.DataFrame, candidates: set[str]) -> Optional[str]:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lower_map:
            return lower_map[cand]
    return None


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    return list(df.select_dtypes(include="number").columns)


def _categorical_columns(df: pd.DataFrame) -> list[str]:
    nums = set(_numeric_columns(df))
    return [c for c in df.columns if c not in nums]


def _load_geojson_for_df(df: pd.DataFrame, provincia_col: str) -> Optional[dict]:
    if not _GEOJSON_PATH.exists():
        return None

    with open(_GEOJSON_PATH, encoding="utf-8") as f:
        geojson = json.load(f)

    nombres_db = {
        _normalize_name(p): p for p in df[provincia_col].dropna().astype(str)
    }

    features = []
    for feat in geojson.get("features", []):
        nombre_geo = feat.get("properties", {}).get("shapeName", "")
        clave = _normalize_name(nombre_geo)
        if clave in nombres_db:
            feat = dict(feat)
            props = dict(feat.get("properties", {}))
            props["shapeName_db"] = nombres_db[clave]
            feat["properties"] = props
            features.append(feat)

    if not features:
        return None

    return {"type": "FeatureCollection", "features": features}


def infer_chart_type(df: pd.DataFrame, chart_hint: str = "table") -> str:
    """
    Decide el tipo de gráfico a partir de los datos y la pista del LLM.
    """
    if df is None or df.empty:
        return "table"

    if len(df) == 1 and len(df.columns) <= 3:
        # Un solo registro: a veces conviene solo tabla/métricas
        if chart_hint in {"bar", "pie", "line", "map"}:
            return chart_hint
        return "table"

    provincia_col = _find_column(df, _PROVINCIA_COLS)
    if chart_hint == "map" and provincia_col and _numeric_columns(df):
        return "map"
    if provincia_col and _numeric_columns(df) and chart_hint != "bar":
        # Si hay provincias y valor, preferir mapa cuando hay varias filas
        if len(df) >= 3:
            return "map"

    time_col = _find_column(df, _TIME_COLS)
    if chart_hint == "line" or (time_col and _numeric_columns(df)):
        if time_col:
            return "line"

    if chart_hint == "pie" and len(df) <= 12:
        return "pie"

    if chart_hint in {"bar", "line", "pie", "map"}:
        return chart_hint

    cats = _categorical_columns(df)
    nums = _numeric_columns(df)
    if cats and nums:
        return "bar" if len(df) > 8 else "pie"
    if len(nums) >= 2 and len(df.columns) == 2:
        return "bar"

    return "bar" if nums else "table"


def build_chart(
    df: pd.DataFrame,
    chart_hint: str = "table",
    title: str = "Resultado de la consulta",
) -> Optional[go.Figure]:
    """
    Construye un gráfico Plotly según el tipo inferido.

    Returns
    -------
    plotly.graph_objects.Figure o None si no es graficable.
    """
    if df is None or df.empty:
        return None

    chart_type = infer_chart_type(df, chart_hint)
    if chart_type == "table":
        return None

    nums = _numeric_columns(df)
    cats = _categorical_columns(df)

    if not nums:
        return None

    y_col = nums[0]
    x_col = cats[0] if cats else (df.columns[0] if df.columns[0] != y_col else None)

    # ---------- Mapa por provincia ----------
    if chart_type == "map":
        provincia_col = _find_column(df, _PROVINCIA_COLS) or x_col
        if provincia_col is None:
            chart_type = "bar"
        else:
            geojson = _load_geojson_for_df(df, provincia_col)
            if geojson is None:
                chart_type = "bar"
            else:
                fig = px.choropleth_mapbox(
                    df,
                    geojson=geojson,
                    locations=provincia_col,
                    featureidkey="properties.shapeName_db",
                    color=y_col,
                    color_continuous_scale="OrRd",
                    mapbox_style="carto-positron",
                    zoom=5,
                    center={"lat": -1.5, "lon": -78.5},
                    opacity=0.75,
                    title=title,
                    labels={y_col: y_col, provincia_col: "Provincia"},
                )
                fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=480)
                return fig

    # ---------- Línea temporal ----------
    if chart_type == "line":
        time_col = _find_column(df, _TIME_COLS) or x_col
        if time_col is None:
            chart_type = "bar"
        else:
            plot_df = df.sort_values(by=time_col) if time_col in df.columns else df
            fig = px.line(
                plot_df,
                x=time_col,
                y=y_col,
                markers=True,
                title=title,
            )
            fig.update_layout(height=420)
            return fig

    # ---------- Pie ----------
    if chart_type == "pie" and x_col is not None:
        fig = px.pie(
            df.head(12),
            names=x_col,
            values=y_col,
            title=title,
            hole=0.35,
        )
        fig.update_layout(height=420)
        return fig

    # ---------- Barras (default graficable) ----------
    if x_col is None:
        # Dos columnas numéricas: usar índice o primera numérica como x
        if len(nums) >= 2:
            fig = px.bar(df, x=nums[0], y=nums[1], title=title, text=nums[1])
            fig.update_layout(height=420)
            return fig
        return None

    plot_df = df.head(25)
    fig = px.bar(
        plot_df,
        x=x_col,
        y=y_col,
        text=y_col,
        title=title,
    )
    fig.update_layout(xaxis_tickangle=-35, height=420)
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    return fig
