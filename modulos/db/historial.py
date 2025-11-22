from .db import conectar
from datetime import datetime

def eliminar_historial(id_historial):
    try:
        conn, cursor = conectar()
        # Primero verificar si hay registros relacionados
        cursor.execute("""
            SELECT COUNT(*) 
            FROM atencion 
            WHERE id_historial = ?
        """, (id_historial,))
        if cursor.fetchone()[0] > 0:
            return False, "No se puede eliminar el historial porque tiene atenciones asociadas"
        
        # Si no hay registros relacionados, eliminar
        cursor.execute("DELETE FROM historial WHERE id = ?", (id_historial,))
        cambios = cursor.rowcount
        conn.commit()
        conn.close()
        if cambios > 0:
            return True, f"Historial ID {id_historial} eliminado correctamente"
        return False, f"No se encontró el historial con ID {id_historial}"
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        return False, str(e)

def agregar_historial(fecha_registro, id_diagnostico, id_tratamiento, observaciones, alergias, resultado_examen, id_paciente, id_cita):
    from .db import existe_tabla_id
    
    # Validar que existan las referencias
    if not existe_tabla_id("diagnostico", id_diagnostico):
        return False, "El diagnóstico especificado no existe"
    if not existe_tabla_id("tratamiento", id_tratamiento):
        return False, "El tratamiento especificado no existe"
    if not existe_tabla_id("paciente", id_paciente):
        return False, "El paciente especificado no existe"
    if not existe_tabla_id("cita", id_cita):
        return False, "La cita especificada no existe"
    
    try:
        conn, cursor = conectar()
        cursor.execute("""
            INSERT INTO historial (fecha_registro, id_diagnostico, id_tratamiento, observaciones, alergias, resultado_examen, id_paciente, id_cita)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (fecha_registro, id_diagnostico, id_tratamiento, observaciones, alergias, resultado_examen, id_paciente, id_cita))
        id_generado = cursor.lastrowid
        conn.commit()
        conn.close()
        return True, f"Historial ID {id_generado} agregado correctamente"
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        return False, str(e)

def obtener_historiales():
    try:
        conn, cursor = conectar()
        cursor.execute("""
            SELECT h.id, h.fecha_registro,
                   p.nombre || ' ' || p.apellido AS paciente,
                   d.descripcion AS diagnostico,
                   t.tratamiento AS tratamiento,
                   h.observaciones, h.alergias, h.resultado_examen
            FROM historial h
            JOIN paciente p ON h.id_paciente = p.id
            JOIN diagnostico d ON h.id_diagnostico = d.id
            JOIN tratamiento t ON h.id_tratamiento = t.id
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
