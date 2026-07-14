import pyodbc
import pandas as pd
import streamlit as st

from config import *


def get_connection():

    conn = pyodbc.connect(
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        "TrustServerCertificate=yes;"
    )

    return conn


@st.cache_data(ttl=300, max_entries=128, show_spinner=False)
def ejecutar_consulta(sql, params=None):

    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params or ()))

        if cursor.description is None:
            return pd.DataFrame()

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        return pd.DataFrame.from_records(rows, columns=columns)
    finally:
        conn.close()