from .db import conectar, existe_tabla_id
from .busqueda import buscar_registros_exactos

def agregar_cita(fecha, hora, motivo, id_paciente, id_medico, estado="PENDIENTE"):
    if not existe_tabla_id("paciente", id_paciente):
        return False, "El paciente indicado no existe"
    if not existe_tabla_id("medico", id_medico):
        return False, "El médico indicado no existe"

    try:
        conexion, cursor = conectar()
        cursor.execute(
            """INSERT INTO cita (fecha, hora, estado, motivo, id_paciente, id_medico)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (str(fecha), hora.strftime("%H:%M:%S"), estado.strip().upper(), motivo.strip(), id_paciente, id_medico)
        )
        conexion.commit()
        id_insertado = cursor.lastrowid
        conexion.close()
        return True, f"Cita agregada correctamente con ID {id_insertado}"
    except Exception as e:
        return False, f"Error al agregar cita: {e}"


def mostrar_citas():
    """Devuelve todas las citas como lista de diccionarios con nombres de columnas reales."""
    conexion, cursor = conectar()
    cursor.execute("SELECT * FROM cita")
    filas = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    conexion.close()
    return [dict(zip(columnas, fila)) for fila in filas]

def eliminar_cita(id_cita):
    if not existe_tabla_id("cita", id_cita):
        return False, "No existe cita con ese ID"
    try:
        conexion, cursor = conectar()
        cursor.execute("DELETE FROM cita WHERE id=?", (id_cita,))
        conexion.commit()
        conexion.close()
        return True, f"Cita ID {id_cita} eliminada correctamente"
    except Exception as e:
        return False, f"Error al eliminar cita."

def actualizar_cita(id_cita, fecha, hora, estado, motivo, id_paciente, id_medico):
    if not existe_tabla_id("cita", id_cita):
        return False, "No existe cita con ese ID"
    if not existe_tabla_id("paciente", id_paciente):
        return False, "Paciente no existe"
    if not existe_tabla_id("medico", id_medico):
        return False, "Médico no existe"
    try:
        conexion, cursor = conectar()

        hora_str = hora.strftime("%H:%M:%S") if hasattr(hora, "strftime") else str(hora)
        estado_str = estado.strip().upper()
        motivo_str = motivo.strip()
        id_paciente = int(id_paciente)
        id_medico = int(id_medico)

        cursor.execute(
            """UPDATE cita
               SET fecha=?, hora=?, estado=?, motivo=?, id_paciente=?, id_medico=?
               WHERE id=?""",
            (str(fecha), hora_str, estado_str, motivo_str, id_paciente, id_medico, int(id_cita))
        )
        conexion.commit()
        conexion.close()
        return True, f"Cita ID {id_cita} actualizada correctamente"
    except Exception as e:
        import traceback
        print("[ERROR actualizar_cita]:", e)
        traceback.print_exc()
        return False, f"Error al actualizar cita: {e}"

def buscar_citas(id_paciente=None, id_medico=None, fecha=None, estado=None, rut=None, id_cita=None):
    """
    Busca citas filtrando por paciente, médico, fecha, estado, rut de paciente o id de cita.
    """
    filtros = {}
    if id_cita:
        filtros["id"] = id_cita
    if id_paciente:
        filtros["id_paciente"] = id_paciente
    if id_medico:
        filtros["id_medico"] = id_medico
    if fecha:
        filtros["fecha"] = fecha
    if estado:
        filtros["estado"] = estado

    # Búsqueda base (sin rut porque cita no tiene ese campo)
    base = buscar_registros_exactos("cita", filtros)

    if rut:
        # Filtrar por rut del paciente descifrándolo
        from .db import descifrar_dato
        filtradas = []
        # map id_paciente -> rut descifrado (cache)
        cache_rut = {}
        for cita in base:
            pid = cita.get("id_paciente")
            if pid is None:
                continue
            if pid not in cache_rut:
                conexion, cursor = conectar()
                cursor.execute("SELECT rut FROM paciente WHERE id=?", (pid,))
                fila = cursor.fetchone()
                conexion.close()
                if fila and fila[0]:
                    try:
                        cache_rut[pid] = descifrar_dato(fila[0])
                    except Exception:
                        cache_rut[pid] = fila[0]
                else:
                    cache_rut[pid] = None
            if cache_rut[pid] == rut:
                filtradas.append(cita)
        return filtradas
    return base


def mostrar_paciente_nombre(id_paciente):
    # Consulta a la base de datos para obtener el nombre del paciente con el ID proporcionado
    conexion, cursor = conectar()
    cursor.execute("SELECT nombre, apellido FROM paciente WHERE id=?", (id_paciente,))
    paciente = cursor.fetchone()
    conexion.close()
    return f"{paciente[0]} {paciente[1]}" if paciente else "Desconocido"

def mostrar_paciente_rut(id_paciente):
    # Consulta a la base de datos para obtener el RUT del paciente con el ID proporcionado
    from .db import descifrar_dato
    conexion, cursor = conectar()
    cursor.execute("SELECT rut FROM paciente WHERE id=?", (id_paciente,))
    paciente = cursor.fetchone()
    conexion.close()
    if paciente and paciente[0]:
        return descifrar_dato(paciente[0])  # Descifrar el RUT antes de mostrarlo
    return "Desconocido"
