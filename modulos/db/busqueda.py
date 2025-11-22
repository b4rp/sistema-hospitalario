from .db import conectar, TABLAS_VALIDAS

def buscar_registros_exactos(tabla, filtros=None):
    """
    Búsqueda estricta en cualquier tabla: todas las columnas deben coincidir exactamente.
    
    Args:
        tabla: Nombre de la tabla (validado contra whitelist)
        filtros: dict {"columna": valor}. Valores vacíos o None se ignoran.
    
    Returns:
        list: Lista de diccionarios con los registros encontrados
    
    Raises:
        ValueError: Si la tabla no está en TABLAS_VALIDAS
    """
    if filtros is None:
        filtros = {}
    
    # Validar tabla contra whitelist
    if tabla not in TABLAS_VALIDAS:
        raise ValueError(f"Tabla '{tabla}' no permitida. Tablas válidas: {TABLAS_VALIDAS}")

    try:
        conexion, cursor = conectar()
        # Seguro usar f-string porque tabla fue validada
        query = f"SELECT * FROM {tabla}"
        params = []
        condiciones = []

        for col, val in filtros.items():
            if val is None or (isinstance(val, str) and val.strip() == ""):
                continue
            condiciones.append(f"{col} = ?")
            params.append(val)

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        query += " ORDER BY id"
        cursor.execute(query, params)
        columnas = [desc[0] for desc in cursor.description]
        filas = cursor.fetchall()
        conexion.close()

        return [dict(zip(columnas, fila)) for fila in filas]

    except Exception as e:
        print(f"Error en buscar_registros_exactos: {e}")
        return []
