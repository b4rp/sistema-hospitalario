import sqlite3
from .db import conectar, existe_tabla_id
from .busqueda import buscar_registros_exactos

def agregar_especialidad(nombre, descripcion=""):
    if not nombre.strip():
        return False, "El nombre es obligatorio"
    if not descripcion:
        descripcion = "(Sin descripción)"
    try:
        conexion, cursor = conectar()
        # Evitar duplicados por nombre (insensible a mayúsculas/minúsculas)
        cursor.execute("SELECT id FROM especialidad WHERE lower(nombre) = lower(?)", (nombre.strip(),))
        if cursor.fetchone():
            conexion.close()
            return False, "Ya existe una especialidad con ese nombre"

        cursor.execute(
            "INSERT INTO especialidad (nombre, descripcion) VALUES (?, ?)",
            (nombre.strip().title(), descripcion.strip())
        )
        conexion.commit()
        id_insertado = cursor.lastrowid
        conexion.close()
        return True, f"Especialidad '{nombre.strip().title()}' agregada correctamente con ID {id_insertado}"
    except Exception as e:
        try:
            conexion.close()
        except Exception:
            pass
        return False, str(e)

def mostrar_especialidades():
    """Devuelve todas las especialidades como lista de diccionarios con nombres de columnas reales."""
    conexion, cursor = conectar()
    cursor.execute("SELECT * FROM especialidad")
    filas = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    conexion.close()
    return [dict(zip(columnas, fila)) for fila in filas]

def eliminar_especialidad(id_esp):
    if not existe_tabla_id("especialidad", id_esp):
        return False, "No existe especialidad con ese ID"
    try:
        conexion, cursor = conectar()
        cursor.execute("DELETE FROM especialidad WHERE id = ?", (id_esp,))
        conexion.commit()
        conexion.close()
        return True, f"Especialidad ID {id_esp} eliminada correctamente"
    except sqlite3.IntegrityError:
        try:
            conexion.close()
        except Exception:
            pass
        return False, "No se puede eliminar: existen médicos u otros registros que la referencian"
    except Exception as e:
        try:
            conexion.close()
        except Exception:
            pass
        return False, str(e)

def actualizar_especialidad(id_esp, nombre, descripcion):
    """Actualiza nombre y descripción de una especialidad por ID"""
    if not existe_tabla_id("especialidad", id_esp):
        return False, "No existe especialidad con ese ID"
    if not nombre.strip():
        return False, "El nombre es obligatorio"
    try:
        conexion, cursor = conectar()
        # Evitar duplicado de nombre con otro ID
        cursor.execute(
            "SELECT id FROM especialidad WHERE lower(nombre) = lower(?) AND id <> ?",
            (nombre.strip(), id_esp)
        )
        if cursor.fetchone():
            conexion.close()
            return False, "Ya existe otra especialidad con ese nombre"

        cursor.execute(
            "UPDATE especialidad SET nombre = ?, descripcion = ? WHERE id = ?",
            (nombre.strip().title(), descripcion.strip(), id_esp)
        )
        conexion.commit()
        conexion.close()
        return True, f"Especialidad ID {id_esp} actualizada correctamente"
    except Exception as e:
        try:
            conexion.close()
        except Exception:
            pass
        return False, str(e)

def buscar_especialidades(nombre=None, id_especialidad=None):
    """
    Busca especialidades filtrando por nombre o ID.
    """
    filtros = {}
    if nombre:
        filtros["nombre"] = nombre.strip().title()
    if id_especialidad:
        filtros["id"] = id_especialidad

    return buscar_registros_exactos("especialidad", filtros)


