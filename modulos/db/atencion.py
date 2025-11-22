from .db import conectar

def eliminar_atencion(id_atencion):
    try:
        conn, cursor = conectar()
        cursor.execute("DELETE FROM atencion WHERE id = ?", (id_atencion,))
        cambios = cursor.rowcount
        conn.commit()
        conn.close()
        if cambios > 0:
            return True, f"Atención ID {id_atencion} eliminada correctamente"
        return False, f"No se encontró la atención con ID {id_atencion}"
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        return False, str(e)

def agregar_atencion(id_diagnostico, id_historial, descripcion):
    from .db import existe_tabla_id
    
    # Validar que existan las referencias
    if not existe_tabla_id("diagnostico", id_diagnostico):
        return False, "El diagnóstico especificado no existe"
    if not existe_tabla_id("historial", id_historial):
        return False, "El historial especificado no existe"
    
    try:
        conn, cursor = conectar()
        cursor.execute("""
            INSERT INTO atencion (id_diagnostico, id_historial, descripcion)
            VALUES (?, ?, ?)
        """, (id_diagnostico, id_historial, descripcion))
        id_generado = cursor.lastrowid
        conn.commit()
        conn.close()
        return True, f"Atención ID {id_generado} agregada correctamente"
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        return False, str(e)

def obtener_atenciones():
    try:
        conn, cursor = conectar()
        cursor.execute("""
            SELECT a.id, a.descripcion,
                   d.descripcion AS diagnostico,
                   h.observaciones AS historial,
                   h.fecha_registro
            FROM atencion a
            JOIN diagnostico d ON a.id_diagnostico = d.id
            JOIN historial h ON a.id_historial = h.id
            ORDER BY h.fecha_registro DESC
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
