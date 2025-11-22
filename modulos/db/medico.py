from .db import conectar, existe_tabla_id, cifrar_dato, descifrar_dato
from .busqueda import buscar_registros_exactos
from .utilidades import formatear_rut, validar_rut, validar_email, validar_telefono
import re

def crear_medico(rut, nombre, apellido, correo, telefono, id_especialidad, horario=None):
    """
    Inserta un médico nuevo en la tabla 'medico' incluyendo horario de atención.
    Retorna (True, mensaje_ok) o (False, mensaje_error).
    """
    # Validación de campos obligatorios
    if not rut or not rut.strip():
        return False, "El RUT es obligatorio."
    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio."
    if not apellido or not apellido.strip():
        return False, "El apellido es obligatorio."
    if not correo or not correo.strip():
        return False, "El correo es obligatorio."
    if not telefono or not telefono.strip():
        return False, "El teléfono es obligatorio."

    # Validación de RUT
    if not validar_rut(rut):
        return False, "RUT inválido. Formato esperado: 12.345.678-9"

    # Normalizamos el RUT al formato estándar (xx.xxx.xxx-x)
    rut_formateado = formatear_rut(rut)

    # Validación de correo
    if not validar_email(correo):
        return False, "Correo inválido. Ejemplo válido: usuario@dominio.cl"

    # Validación de teléfono
    if not validar_telefono(telefono):
        return False, "Teléfono inválido. Usa solo dígitos o formato +56..."

    # Validación de la especialidad
    if not existe_tabla_id("especialidad", id_especialidad):
        return False, "La especialidad indicada no existe."

    # Validación opcional de horario (permite texto descriptivo)
    if horario is not None:
        horario = horario.strip()
        if not horario:
            return False, "Si se ingresa horario, no puede estar vacío."

    try:
        conexion, cursor = conectar()

        # Cargar todos para verificar duplicados descifrando (porque algunos pueden estar cifrados y otros no)
        cursor.execute("SELECT id, rut, correo, telefono FROM medico")
        filas = cursor.fetchall()
        for _id, rut_db, correo_db, tel_db in filas:
            # Intentar descifrar; si falla asumimos texto plano
            try:
                rut_dec = descifrar_dato(rut_db)
            except Exception:
                rut_dec = rut_db
            try:
                correo_dec = descifrar_dato(correo_db)
            except Exception:
                correo_dec = correo_db
            try:
                tel_dec = descifrar_dato(tel_db)
            except Exception:
                tel_dec = tel_db
            if rut_dec == rut_formateado:
                conexion.close()
                return False, f"Ya existe un médico registrado con el RUT {rut_formateado}"
            if correo_dec == correo.strip():
                conexion.close()
                return False, f"Ya existe un médico registrado con el correo {correo.strip()}"
            if tel_dec == telefono.strip():
                conexion.close()
                return False, f"Ya existe un médico registrado con el teléfono {telefono.strip()}"

        # Insertar cifrando campos sensibles
        cursor.execute(
            """
            INSERT INTO medico (rut, nombre, apellido, correo, telefono, id_especialidad, horario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cifrar_dato(rut_formateado),
                nombre.strip().title(),
                apellido.strip().title(),
                cifrar_dato(correo.strip()),
                cifrar_dato(telefono.strip()),
                id_especialidad,
                horario if horario else None
            )
        )

        conexion.commit()
        id_insertado = cursor.lastrowid
        conexion.close()

        mensaje_ok = f"Médico '{nombre.strip().title()} {apellido.strip().title()}' agregado correctamente con ID {id_insertado}"
        return True, mensaje_ok

    except Exception as e:
        try:
            conexion.close()
        except Exception:
            pass
        return False, f"Error inesperado al crear médico: {str(e)}"


def mostrar_medicos():
    """
    Devuelve todos los médicos como lista de diccionarios con nombres de columnas reales.
    SELECT explícito para asegurar el orden de columnas y que incluimos 'rut'.
    """
    try:
        conexion, cursor = conectar()

        cursor.execute(
            """
            SELECT m.id, m.rut, m.nombre, m.apellido, m.correo, m.telefono, 
                   m.id_especialidad, m.horario, e.nombre as especialidad
            FROM medico m
            LEFT JOIN especialidad e ON m.id_especialidad = e.id
            ORDER BY m.id
            """
        )

        filas = cursor.fetchall()
        
        # Obtener nombres de columnas
        columnas = [desc[0] for desc in cursor.description]

        conexion.close()

        # Convertir a lista de diccionarios y descifrar campos sensibles
        lista_resultado = []
        for fila in filas:
            fila_dict = dict(zip(columnas, fila))
            for campo in ["rut", "correo", "telefono"]:
                if campo in fila_dict and fila_dict[campo] is not None:
                    try:
                        fila_dict[campo] = descifrar_dato(fila_dict[campo])
                    except Exception:
                        # Ya está en texto plano
                        pass
            lista_resultado.append(fila_dict)

        return lista_resultado

    except Exception as e:
        try:
            conexion.close()
        except:
            pass
        return []


def borrar_medico(id_med):
    """
    Elimina un médico por ID.
    Retorna (True, msg_ok) o (False, msg_error).
    """

    # Verificar que el médico exista
    if not existe_tabla_id("medico", id_med):
        return False, "No existe médico con ese ID."

    try:
        conexion, cursor = conectar()

        cursor.execute(
            "DELETE FROM medico WHERE id = ?",
            (id_med,)
        )

        conexion.commit()
        conexion.close()

        msg_ok = "Médico ID " + str(id_med) + " eliminado correctamente"
        return True, msg_ok

    except Exception as e:
        return False, "Error al eliminar médico. Verifique que no esté referenciado en otra tabla (por ejemplo en citas)."


def actualizar_medico(id_med, rut, nombre, apellido, correo, telefono, id_especialidad, horario=None):
    """
    Actualiza los datos completos de un médico existente.
    Retorna (True, msg_ok) o (False, msg_error).
    """

    # Verificar que exista el médico
    if not existe_tabla_id("medico", id_med):
        return False, "No existe médico con ese ID."

    # Validaciones similares a crear_medico
    if not rut or not rut.strip():
        return False, "El RUT es obligatorio."
    if not validar_rut(rut):
        return False, "RUT inválido. Formato esperado: 12.345.678-9"

    rut_formateado = formatear_rut(rut)

    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio."
    if not apellido or not apellido.strip():
        return False, "El apellido es obligatorio."
    if not correo or not correo.strip():
        return False, "El correo es obligatorio."
    if not telefono or not telefono.strip():
        return False, "El teléfono es obligatorio."

    if not validar_email(correo):
        return False, "Correo inválido. Ejemplo válido: usuario@dominio.cl"
    if not validar_telefono(telefono):
        return False, "Teléfono inválido. Usa solo dígitos o formato +56..."
    if not existe_tabla_id("especialidad", id_especialidad):
        return False, "La especialidad indicada no existe."

    # Validación opcional de horario (permite texto descriptivo)
    if horario is not None:
        horario = horario.strip()
        if not horario:
            return False, "Si se ingresa horario, no puede estar vacío."

    try:
        conexion, cursor = conectar()

        # Verificar duplicados contra otros registros (descifrando si corresponde)
        cursor.execute("SELECT id, rut, correo, telefono FROM medico")
        filas = cursor.fetchall()
        for _id, rut_db, correo_db, tel_db in filas:
            if _id == id_med:
                continue
            try:
                rut_dec = descifrar_dato(rut_db)
            except Exception:
                rut_dec = rut_db
            try:
                correo_dec = descifrar_dato(correo_db)
            except Exception:
                correo_dec = correo_db
            try:
                tel_dec = descifrar_dato(tel_db)
            except Exception:
                tel_dec = tel_db
            if rut_dec == rut_formateado:
                conexion.close()
                return False, "Ya existe otro médico con ese RUT"
            if correo_dec == correo.strip():
                conexion.close()
                return False, "Ya existe otro médico con ese correo"
            if tel_dec == telefono.strip():
                conexion.close()
                return False, "Ya existe otro médico con ese teléfono"

        cursor.execute(
            """
            UPDATE medico
            SET rut = ?,
                nombre = ?,
                apellido = ?,
                correo = ?,
                telefono = ?,
                id_especialidad = ?,
                horario = ?
            WHERE id = ?
            """,
            (
                cifrar_dato(rut_formateado),
                nombre.strip().title(),
                apellido.strip().title(),
                cifrar_dato(correo.strip()),
                cifrar_dato(telefono.strip()),
                id_especialidad,
                horario if horario else None,
                id_med
            )
        )

        conexion.commit()
        conexion.close()

        msg_ok = "Médico ID " + str(id_med) + " actualizado correctamente"
        return True, msg_ok

    except Exception as e:
        try:
            conexion.close()
        except Exception:
            pass
        return False, "Error al actualizar médico. Verifique datos y duplicados."


def buscar_medicos(nombre=None, apellido=None, id_especialidad=None, id_medico=None, rut=None):
    """
    Búsqueda exacta de médicos por uno o más campos.
    Usa buscar_registros_exactos, que asumo hace SELECT ... WHERE campo = valor AND ...
    """
    # Debido a que rut, correo y telefono están cifrados, buscar por RUT requiere
    # una comparación después de descifrar. Otros filtros pueden ir directos.
    filtros = {}
    if nombre:
        filtros["nombre"] = nombre.strip().title()
    if apellido:
        filtros["apellido"] = apellido.strip().title()
    if id_especialidad:
        filtros["id_especialidad"] = id_especialidad
    if id_medico:
        filtros["id"] = id_medico

    # Ejecutar búsqueda base sin rut primero
    base = buscar_registros_exactos("medico", filtros)

    # Descifrar campos sensibles para consistencia con mostrar_medicos
    for fila in base:
        for campo in ["rut", "correo", "telefono"]:
            val = fila.get(campo)
            if val is not None:
                try:
                    fila[campo] = descifrar_dato(val)
                except Exception:
                    # ya podría estar plano
                    pass

    if rut and validar_rut(rut):
        rut_normalizado = formatear_rut(rut)
        filtrados = []
        for fila in base:
            valor_rut = fila.get("rut")
            if valor_rut == rut_normalizado:
                filtrados.append(fila)
        return filtrados
    return base
