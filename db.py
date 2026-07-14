import pandas as pd
import streamlit as st

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

from config import SERVER, DATABASE, USERNAME, PASSWORD


@st.cache_resource
def get_connection():

    connection_string = (
        f"mssql+pymssql://{USERNAME}:{quote_plus(PASSWORD)}"
        f"@{SERVER}:1433/{DATABASE}"
    )

    engine = create_engine(
        connection_string,
        pool_pre_ping=True
    )

    return engine


@st.cache_data(ttl=300, max_entries=128, show_spinner=False)
def ejecutar_consulta(sql, params=None):

    engine = get_connection()

    try:
        with engine.connect() as conn:

            if params:
                result = conn.execute(
                    text(sql),
                    params
                )
            else:
                result = conn.execute(
                    text(sql)
                )

            return pd.DataFrame(
                result.fetchall(),
                columns=result.keys()
            )

    except Exception as e:
        st.error(f"Error de conexión a la base de datos: {e}")
        return pd.DataFrame()