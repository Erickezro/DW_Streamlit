"""Shared SQL helpers for fact-level filters."""

BASE_FROM = """
FROM Fact_Accidentes f
INNER JOIN Dim_Tiempo t
    ON f.id_tiempo = t.id_tiempo
INNER JOIN Dim_Ubicacion u
    ON f.id_ubicacion = u.id_ubicacion
INNER JOIN Dim_Clase c
    ON f.id_clase = c.id_clase
INNER JOIN Dim_Causa ca
    ON f.id_causa = ca.id_causa
"""


def construir_filtros(
    anio=None,
    provincias=None,
    cantones=None,
    clases=None,
    causas=None
):

    filtros = []
    parametros = {}


    # ======================
    # Año
    # ======================

    if anio not in (None, "Todos"):

        filtros.append(
            "t.anio = :anio"
        )

        parametros["anio"] = int(anio)


    # ======================
    # Provincias
    # ======================

    if provincias:

        nombres = []

        for i, provincia in enumerate(provincias):

            nombre = f"provincia_{i}"

            nombres.append(
                f":{nombre}"
            )

            parametros[nombre] = provincia


        filtros.append(
            f"u.provincia IN ({','.join(nombres)})"
        )


    # ======================
    # Cantones
    # ======================

    if cantones:

        nombres = []

        for i, canton in enumerate(cantones):

            nombre = f"canton_{i}"

            nombres.append(
                f":{nombre}"
            )

            parametros[nombre] = canton


        filtros.append(
            f"u.canton IN ({','.join(nombres)})"
        )


    # ======================
    # Clases
    # ======================

    if clases:

        nombres = []

        for i, clase in enumerate(clases):

            nombre = f"clase_{i}"

            nombres.append(
                f":{nombre}"
            )

            parametros[nombre] = clase


        filtros.append(
            f"c.clase IN ({','.join(nombres)})"
        )


    # ======================
    # Causas
    # ======================

    if causas:

        nombres = []

        for i, causa in enumerate(causas):

            nombre = f"causa_{i}"

            nombres.append(
                f":{nombre}"
            )

            parametros[nombre] = causa


        filtros.append(
            f"ca.causa IN ({','.join(nombres)})"
        )


    if filtros:

        return (
            "WHERE " + " AND ".join(filtros),
            parametros
        )


    return "", parametros