import re
from datetime import date
from .db import conectar, existe_tabla_id, cifrar_dato, descifrar_dato
from .utilidades import (
    formatear_rut,
    validar_rut,
    validar_email,
    validar_telefono,
    es_menor_de_edad
)
from .busqueda import buscar_registros_exactos


def agregar_paciente(rut, nombre, apellido, fecha_nacimiento, correo, telefono, 
                     genero, direccion, sistema_salud, nacionalidad,
                     nombre_emergencia=None, apellido_emergencia=None, telefono_emergencia=None):
    """
    Inserta un nuevo paciente en la base de datos con cifrado Fernet.
    Valida RUT, correo, teléfono, etc. y evita duplicados.
    Si el paciente es menor de 18 años, los campos de emergencia son obligatorios.
    """

    # Normalización básica
    rut = rut.strip().upper() if rut else ""
    nombre = nombre.strip().title() if nombre else ""
    apellido = apellido.strip().title() if apellido else ""
    correo = correo.strip() if correo else ""
    telefono = telefono.strip() if telefono else ""
    genero = genero.strip().capitalize() if genero else ""
    direccion = direccion.strip() if direccion else ""
    sistema_salud = sistema_salud.strip() if sistema_salud else ""
    nacionalidad = nacionalidad.strip().title() if nacionalidad else ""

    # Normalizar campos de emergencia
    nombre_emergencia = nombre_emergencia.strip().title() if nombre_emergencia else None
    apellido_emergencia = apellido_emergencia.strip().title() if apellido_emergencia else None
    telefono_emergencia = telefono_emergencia.strip() if telefono_emergencia else None

    # Validaciones básicas
    if sistema_salud not in ("Isapre", "Fonasa"):
        return False, "El sistema de salud debe ser 'Isapre' o 'Fonasa'."

    if not nacionalidad:
        return False, "La nacionalidad es obligatoria."

    rut_formateado = formatear_rut(rut)

    if not rut_formateado or not validar_rut(rut_formateado):
        return False, "RUT inválido o vacío."
    if not nombre:
        return False, "El nombre es obligatorio."
    if not apellido:
        return False, "El apellido es obligatorio."
    if not fecha_nacimiento:
        return False, "La fecha de nacimiento es obligatoria."
    if not correo or not validar_email(correo):
        return False, "El correo es obligatorio o no tiene formato válido."
    if not telefono or not validar_telefono(telefono):
        return False, "El teléfono es obligatorio o no tiene formato válido."
    if genero not in ("Masculino", "Femenino"):
        return False, "El género debe ser 'Masculino' o 'Femenino'."
    if not direccion:
        return False, "La dirección es obligatoria."

    # Validar campos de emergencia para menores de edad
    if es_menor_de_edad(fecha_nacimiento):
        if not nombre_emergencia:
            return False, "El nombre de contacto de emergencia es obligatorio para menores de 18 años."
        if not apellido_emergencia:
            return False, "El apellido de contacto de emergencia es obligatorio para menores de 18 años."
        if not telefono_emergencia or not validar_telefono(telefono_emergencia):
            return False, "El teléfono de emergencia es obligatorio y debe tener formato válido para menores de 18 años."

    # Verificar duplicados
    try:
        conexion, cursor = conectar()
        cursor.execute("SELECT id, rut, correo FROM paciente")
        filas = cursor.fetchall()
        conexion.close()

        for id_existente, rut_cifrado, correo_cifrado in filas:
            if descifrar_dato(rut_cifrado) == rut_formateado or descifrar_dato(correo_cifrado) == correo:
                return False, "Ya existe un paciente con ese RUT o correo."

    except Exception as e:
        try:
            conexion.close()
        except Exception as cerrar_error:
            print(f"No se pudo cerrar la conexión: {cerrar_error}")
        return False, f"Error al verificar duplicados: {e}"

    # Cifrar campos de emergencia si existen
    nombre_emergencia_cifrado = cifrar_dato(nombre_emergencia) if nombre_emergencia else None
    apellido_emergencia_cifrado = cifrar_dato(apellido_emergencia) if apellido_emergencia else None
    telefono_emergencia_cifrado = cifrar_dato(telefono_emergencia) if telefono_emergencia else None

    # Insertar paciente
    try:
        conexion, cursor = conectar()
        cursor.execute(
            """
            INSERT INTO paciente
            (rut, nombre, apellido, fecha_nacimiento, correo, telefono, genero, direccion, 
             sistema_salud, nacionalidad, nombre_emergencia, apellido_emergencia, telefono_emergencia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cifrar_dato(rut_formateado),
                nombre,
                apellido,
                cifrar_dato(fecha_nacimiento),
                cifrar_dato(correo),
                cifrar_dato(telefono),
                genero,
                cifrar_dato(direccion),
                sistema_salud,
                nacionalidad,
                nombre_emergencia_cifrado,
                apellido_emergencia_cifrado,
                telefono_emergencia_cifrado
            )
        )
        conexion.commit()
        id_insertado = cursor.lastrowid
        conexion.close()
        return True, f"Paciente agregado correctamente con ID {id_insertado}."
    except Exception as e:
        try:
            conexion.close()
        except Exception as cerrar_error:
            print(f"No se pudo cerrar la conexión: {cerrar_error}")
        return False, f"Error al agregar paciente: {e}"


def mostrar_pacientes():
    """
    Devuelve todos los pacientes descifrando RUT, correo, teléfono, dirección y campos de emergencia.
    """
    try:
        conexion, cursor = conectar()
        cursor.execute("SELECT * FROM paciente")
        filas = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
        conexion.close()

        resultado = []
        for fila in filas:
            registro = dict(zip(columnas, fila))
            # Descifrar campos sensibles
            registro["rut"] = descifrar_dato(registro["rut"])
            registro["fecha_nacimiento"] = descifrar_dato(registro["fecha_nacimiento"])
            registro["correo"] = descifrar_dato(registro["correo"])
            registro["telefono"] = descifrar_dato(registro["telefono"])
            registro["direccion"] = descifrar_dato(registro["direccion"])
            
            # Descifrar campos de emergencia si existen
            if registro.get("nombre_emergencia"):
                registro["nombre_emergencia"] = descifrar_dato(registro["nombre_emergencia"])
            if registro.get("apellido_emergencia"):
                registro["apellido_emergencia"] = descifrar_dato(registro["apellido_emergencia"])
            if registro.get("telefono_emergencia"):
                registro["telefono_emergencia"] = descifrar_dato(registro["telefono_emergencia"])
            
            resultado.append(registro)

        return resultado

    except Exception as e:
        try:
            conexion.close()
        except Exception as cerrar_error:
            print(f"No se pudo cerrar la conexión: {cerrar_error}")
        return []


def eliminar_paciente(id_val):
    """
    Elimina un paciente por ID.
    """
    if not isinstance(id_val, int):
        return False, "El ID debe ser un número entero."

    if not existe_tabla_id("paciente", id_val):
        return False, "No existe paciente con ese ID."

    try:
        conexion, cursor = conectar()
        cursor.execute("DELETE FROM paciente WHERE id = ?", (id_val,))
        conexion.commit()
        conexion.close()
        return True, "Paciente eliminado correctamente."
    except Exception as e:
        try:
            conexion.close()
        except Exception as cerrar_error:
            print(f"No se pudo cerrar la conexión: {cerrar_error}")
        return False, f"Error al eliminar paciente: {e}"


def actualizar_paciente(
    id_val, rut, nombre, apellido, fecha_nacimiento, correo, telefono,
    genero, direccion, sistema_salud, nacionalidad,
    nombre_emergencia=None, apellido_emergencia=None, telefono_emergencia=None
):
    """
    Actualiza un paciente cifrando los campos sensibles.
    Si el paciente es menor de 18 años, los campos de emergencia son obligatorios.
    """

    if not existe_tabla_id("paciente", id_val):
        return False, "No existe paciente con ese ID."

    # Normalizar
    rut = rut.strip().upper() if rut else ""
    nombre = nombre.strip().title() if nombre else ""
    apellido = apellido.strip().title() if apellido else ""
    correo = correo.strip() if correo else ""
    telefono = telefono.strip() if telefono else ""
    genero = genero.strip().capitalize() if genero else ""
    direccion = direccion.strip() if direccion else ""
    sistema_salud = sistema_salud.strip() if sistema_salud else ""
    nacionalidad = nacionalidad.strip().title() if nacionalidad else ""

    # Normalizar campos de emergencia
    nombre_emergencia = nombre_emergencia.strip().title() if nombre_emergencia else None
    apellido_emergencia = apellido_emergencia.strip().title() if apellido_emergencia else None
    telefono_emergencia = telefono_emergencia.strip() if telefono_emergencia else None

    if sistema_salud not in ("Isapre", "Fonasa"):
        return False, "El sistema de salud debe ser 'Isapre' o 'Fonasa'."

    if not nacionalidad:
        return False, "La nacionalidad es obligatoria."

    rut_formateado = formatear_rut(rut)

    if not rut_formateado or not validar_rut(rut_formateado):
        return False, "RUT inválido o vacío."
    if not nombre:
        return False, "El nombre es obligatorio."
    if not apellido:
        return False, "El apellido es obligatorio."
    if not fecha_nacimiento:
        return False, "La fecha de nacimiento es obligatoria."
    if not correo or not validar_email(correo):
        return False, "El correo es obligatorio o no tiene formato válido."
    if not telefono or not validar_telefono(telefono):
        return False, "El teléfono es obligatorio o no tiene formato válido."
    if genero not in ("Masculino", "Femenino"):
        return False, "El género debe ser 'Masculino' o 'Femenino'."
    if not direccion:
        return False, "La dirección es obligatoria."

    # Validar campos de emergencia para menores de edad
    if es_menor_de_edad(fecha_nacimiento):
        if not nombre_emergencia:
            return False, "El nombre de contacto de emergencia es obligatorio para menores de 18 años."
        if not apellido_emergencia:
            return False, "El apellido de contacto de emergencia es obligatorio para menores de 18 años."
        if not telefono_emergencia or not validar_telefono(telefono_emergencia):
            return False, "El teléfono de emergencia es obligatorio y debe tener formato válido para menores de 18 años."

    # Verificar conflicto con otros pacientes
    try:
        conexion, cursor = conectar()
        cursor.execute("SELECT id, rut, correo FROM paciente")
        filas = cursor.fetchall()
        conexion.close()

        for id_existente, rut_cifrado, correo_cifrado in filas:
            if id_existente != id_val:
                if descifrar_dato(rut_cifrado) == rut_formateado or descifrar_dato(correo_cifrado) == correo:
                    return False, "Ya existe otro paciente con ese RUT o correo."
    except Exception as e:
        try:
            conexion.close()
        except Exception as cerrar_error:
            print(f"No se pudo cerrar la conexión: {cerrar_error}")
        return False, f"Error al verificar duplicados antes de actualizar: {e}"

    # Cifrar campos de emergencia si existen
    nombre_emergencia_cifrado = cifrar_dato(nombre_emergencia) if nombre_emergencia else None
    apellido_emergencia_cifrado = cifrar_dato(apellido_emergencia) if apellido_emergencia else None
    telefono_emergencia_cifrado = cifrar_dato(telefono_emergencia) if telefono_emergencia else None

    # Actualizar paciente
    try:
        conexion, cursor = conectar()
        cursor.execute(
            """
            UPDATE paciente
            SET rut = ?, nombre = ?, apellido = ?, fecha_nacimiento = ?,
                correo = ?, telefono = ?, genero = ?, direccion = ?, sistema_salud = ?,
                nacionalidad = ?, nombre_emergencia = ?, apellido_emergencia = ?, telefono_emergencia = ?
            WHERE id = ?
            """,
            (
                cifrar_dato(rut_formateado),
                nombre,
                apellido,
                cifrar_dato(str(fecha_nacimiento)),
                cifrar_dato(correo),
                cifrar_dato(telefono),
                genero,
                cifrar_dato(direccion),
                sistema_salud,
                nacionalidad,
                nombre_emergencia_cifrado,
                apellido_emergencia_cifrado,
                telefono_emergencia_cifrado,
                id_val
            )
        )
        conexion.commit()
        conexion.close()
        return True, "Paciente actualizado correctamente."
    except Exception as e:
        try:
            conexion.close()
        except Exception as cerrar_error:
            print(f"No se pudo cerrar la conexión: {cerrar_error}")
        return False, f"Error al actualizar paciente: {e}"


def eliminar_paciente_por_rut(rut):
    """
    Elimina un paciente buscando por RUT cifrado.
    """
    if not rut:
        return False, "Debe proporcionar un RUT."

    rut_limpio = rut.strip().upper()
    rut_form = formatear_rut(rut_limpio)

    if not validar_rut(rut_form):
        return False, "RUT inválido."

    try:
        conexion, cursor = conectar()
        cursor.execute("SELECT id, rut FROM paciente")
        filas = cursor.fetchall()
        conexion.close()

        for id_encontrado, rut_cifrado in filas:
            if descifrar_dato(rut_cifrado) == rut_form:
                return eliminar_paciente(id_encontrado)

        return False, "No existe paciente con ese RUT."
    except Exception as e:
        try:
            conexion.close()
        except Exception as cerrar_error:
            print(f"No se pudo cerrar la conexión: {cerrar_error}")
        return False, f"Error al buscar paciente por RUT: {e}"