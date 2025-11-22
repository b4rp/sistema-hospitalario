from .db import conectar

def eliminar_tratamiento(id_tratamiento):
    try:
        conn, cursor = conectar()
        # Primero verificar si hay registros relacionados
        cursor.execute("""
            SELECT COUNT(*) 
            FROM historial 
            WHERE id_tratamiento = ?
        """, (id_tratamiento,))
        if cursor.fetchone()[0] > 0:
            return False, "No se puede eliminar el tratamiento porque tiene historiales asociados"
        
        # Si no hay registros relacionados, eliminar
        cursor.execute("DELETE FROM tratamiento WHERE id = ?", (id_tratamiento,))
        cambios = cursor.rowcount
        conn.commit()
        conn.close()
        if cambios > 0:
            return True, f"Tratamiento ID {id_tratamiento} eliminado correctamente"
        return False, f"No se encontró el tratamiento con ID {id_tratamiento}"
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        return False, str(e)

def agregar_tratamiento(fecha_inicio, fecha_termino, tratamiento, id_diagnostico):
    from .db import existe_tabla_id
    
    # Validar que exista el diagnóstico
    if not existe_tabla_id("diagnostico", id_diagnostico):
        return False, "El diagnóstico especificado no existe"
    
    try:
        conn, cursor = conectar()
        cursor.execute("""
            INSERT INTO tratamiento (fecha_inicio, fecha_termino, tratamiento, id_diagnostico)
            VALUES (?, ?, ?, ?)
        """, (fecha_inicio, fecha_termino, tratamiento, id_diagnostico))
        id_generado = cursor.lastrowid
        conn.commit()
        conn.close()
        return True, f"Tratamiento ID {id_generado} agregado correctamente"
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        return False, str(e)

def obtener_tratamientos():
    try:
        conn, cursor = conectar()
        cursor.execute("""
            SELECT t.id, t.tratamiento, t.fecha_inicio, t.fecha_termino,
                   d.descripcion AS diagnostico
            FROM tratamiento t
            JOIN diagnostico d ON t.id_diagnostico = d.id
            ORDER BY t.fecha_inicio DESC
        """)
        datos = cursor.fetchall()
        conn.close()
        return datos
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        return []
