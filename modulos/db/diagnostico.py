from .db import conectar

def eliminar_diagnostico(id_diagnostico):
    try:
        conn, cursor = conectar()
        # Primero verificar si hay registros relacionados
        cursor.execute("""
            SELECT COUNT(*) 
            FROM tratamiento 
            WHERE id_diagnostico = ?
        """, (id_diagnostico,))
        if cursor.fetchone()[0] > 0:
            return False, "No se puede eliminar el diagnóstico porque tiene tratamientos asociados"
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM historial 
            WHERE id_diagnostico = ?
        """, (id_diagnostico,))
        if cursor.fetchone()[0] > 0:
            return False, "No se puede eliminar el diagnóstico porque tiene historiales asociados"
            
        cursor.execute("""
            SELECT COUNT(*) 
            FROM atencion 
            WHERE id_diagnostico = ?
        """, (id_diagnostico,))
        if cursor.fetchone()[0] > 0:
            return False, "No se puede eliminar el diagnóstico porque tiene atenciones asociadas"
        
        # Si no hay registros relacionados, eliminar
        cursor.execute("DELETE FROM diagnostico WHERE id = ?", (id_diagnostico,))
        cambios = cursor.rowcount
        conn.commit()
        conn.close()
        if cambios > 0:
            return True, f"Diagnóstico ID {id_diagnostico} eliminado correctamente"
        return False, f"No se encontró el diagnóstico con ID {id_diagnostico}"
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        return False, str(e)

def agregar_diagnostico(fecha, descripcion, id_medico, id_cita):
    from .db import existe_tabla_id
    
    # Validar que existan las referencias
    if not existe_tabla_id("medico", id_medico):
        return False, "El médico especificado no existe"
    if not existe_tabla_id("cita", id_cita):
        return False, "La cita especificada no existe"
    
    try:
        conn, cursor = conectar()
        cursor.execute("""
            INSERT INTO diagnostico (fecha, descripcion, id_medico, id_cita)
            VALUES (?, ?, ?, ?)
        """, (fecha, descripcion, id_medico, id_cita))
        id_generado = cursor.lastrowid
        conn.commit()
        conn.close()
        return True, f"Diagnóstico ID {id_generado} agregado correctamente"
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        return False, str(e)

def obtener_diagnosticos():
    try:
        conn, cursor = conectar()
        cursor.execute("""
            SELECT d.id, d.fecha, d.descripcion,
                   m.nombre || ' ' || m.apellido AS medico,
                   c.fecha AS fecha_cita,
                   c.motivo AS motivo_cita
            FROM diagnostico d
            JOIN medico m ON d.id_medico = m.id
            JOIN cita c ON d.id_cita = c.id
            ORDER BY d.fecha DESC
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
