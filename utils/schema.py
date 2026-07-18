"""
Esquema del Data Warehouse de accidentes de tránsito en Ecuador.

Este módulo centraliza la descripción del modelo estrella para:
- el system prompt del LLM (Text-to-SQL)
- la validación de tablas permitidas
- la documentación interna del asistente
"""

# Tablas autorizadas para consultas generadas por el LLM
TABLAS_PERMITIDAS = {
    "Fact_Accidentes",
    "Dim_Tiempo",
    "Dim_Ubicacion",
    "Dim_Clase",
    "Dim_Causa",
}

# Alias habituales usados en las consultas del proyecto
ALIAS_TABLAS = {
    "f": "Fact_Accidentes",
    "t": "Dim_Tiempo",
    "u": "Dim_Ubicacion",
    "c": "Dim_Clase",
    "ca": "Dim_Causa",
}

# Descripción textual del esquema para el prompt del modelo
SCHEMA_DESCRIPTION = """
## Modelo dimensional (estrella) — Azure SQL / SQL Server

### Tabla de hechos: Fact_Accidentes
| Columna           | Tipo / rol        | Descripción                          |
|-------------------|-------------------|--------------------------------------|
| id_tiempo         | FK → Dim_Tiempo   | Clave sustituta de tiempo            |
| id_ubicacion      | FK → Dim_Ubicacion| Clave sustituta de ubicación         |
| id_clase          | FK → Dim_Clase    | Clave sustituta de clase             |
| id_causa          | FK → Dim_Causa    | Clave sustituta de causa             |
| total_accidentes  | métrica (int)     | Cantidad de accidentes               |
| num_fallecido     | métrica (int)     | Número de fallecidos                 |
| num_lesionado     | métrica (int)     | Número de lesionados                 |
| total_victimas    | métrica (int)     | Total de víctimas                    |

### Dimensión: Dim_Tiempo
| Columna   | Descripción                                      |
|-----------|--------------------------------------------------|
| id_tiempo | PK sustituta                                     |
| anio      | Año (entero, p. ej. 2022, 2023)                  |
| mes       | Nombre del mes (texto, p. ej. 'Enero')           |
| dia       | Nombre del día de la semana (texto)              |
| hora      | Hora o franja horaria (texto / etiqueta)         |
| cod_mes   | Código numérico del mes (1-12) para ordenar      |
| cod_dia   | Código numérico del día de la semana             |
| cod_hora  | Código numérico de la hora para ordenar          |

### Dimensión: Dim_Ubicacion
| Columna      | Descripción                                      |
|--------------|--------------------------------------------------|
| id_ubicacion | PK sustituta                                     |
| provincia    | Provincia de Ecuador (texto)                     |
| canton       | Cantón (texto). Quito es un cantón de Pichincha  |
| zona         | Zona (urbana/rural u otra clasificación)         |

### Dimensión: Dim_Clase
| Columna  | Descripción                                      |
|----------|--------------------------------------------------|
| id_clase | PK sustituta                                     |
| clase    | Clase / tipo de accidente (texto)                |

### Dimensión: Dim_Causa
| Columna  | Descripción                                      |
|----------|--------------------------------------------------|
| id_causa | PK sustituta                                     |
| causa    | Causa del accidente (texto)                      |

### Relaciones (JOINs obligatorios vía llaves sustitutas)
```sql
FROM Fact_Accidentes f
INNER JOIN Dim_Tiempo t     ON f.id_tiempo = t.id_tiempo
INNER JOIN Dim_Ubicacion u  ON f.id_ubicacion = u.id_ubicacion
INNER JOIN Dim_Clase c      ON f.id_clase = c.id_clase
INNER JOIN Dim_Causa ca     ON f.id_causa = ca.id_causa
```

### Notas de negocio
- El DW cubre accidentes de tránsito en Ecuador.
- Las métricas se agregan con SUM(...).
- Para rankings usar TOP N (sintaxis SQL Server), no LIMIT.
- "Quito" suele filtrarse con u.canton (no como provincia).
- Provincias frecuentes: Guayas, Pichincha, Azuay, Manabí, etc.
- Comparaciones entre provincias: filtrar con IN o CASE.
"""


def get_schema_for_prompt() -> str:
    """Devuelve el esquema listo para inyectar en el system prompt."""
    return SCHEMA_DESCRIPTION.strip()
