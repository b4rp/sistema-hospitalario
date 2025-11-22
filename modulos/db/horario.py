from datetime import time
from .db import conectar, existe_tabla_id, cifrar_dato, descifrar_dato

# Días: 0=Lunes ... 6=Domingo
DIAS_LABEL = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

def _validar_intervalos(bloques):
    """Valida que no haya solapamientos y hora_inicio < hora_fin.
    bloques: lista de ("HH:MM","HH:MM")
    """
    normalizados = []
    for ini, fin in bloques:
        if ini >= fin:
            return False, f"Intervalo inválido {ini}-{fin}: inicio no puede ser >= fin"
        normalizados.append((ini, fin))
    # ordenar
    normalizados.sort(key=lambda x: x[0])
    for i in range(1, len(normalizados)):
        prev_fin = normalizados[i-1][1]
        cur_ini = normalizados[i][0]
        if cur_ini < prev_fin:
            return False, f"Solapamiento entre {normalizados[i-1][0]}-{prev_fin} y {cur_ini}-{normalizados[i][1]}"
    return True, "OK"

def obtener_horarios_medico(id_medico):
    conexion, cursor = conectar()
    cursor.execute("SELECT dia_semana, hora_inicio, hora_fin, tipo FROM horario_medico WHERE id_medico=? ORDER BY dia_semana, hora_inicio", (id_medico,))
    filas = cursor.fetchall()
    conexion.close()
    resultado = {d: [] for d in range(7)}
    for dia, ini, fin, tipo in filas:
        resultado[dia].append((ini, fin, tipo))
    return resultado

def obtener_horario_resumido(id_medico):
    horarios = obtener_horarios_medico(id_medico)
    partes = []
    for dia, bloques in horarios.items():
        if bloques:
            bloques_txt = ", ".join([f"{ini}-{fin}" for ini, fin, _ in bloques])
            partes.append(f"{DIAS_LABEL[dia]}: {bloques_txt}")
    return " | ".join(partes) if partes else "Sin horario"

def reemplazar_horarios_dia(id_medico, dia_semana, bloques, tipo=None):
    """Reemplaza completamente los bloques de un día.
    bloques: lista de ("HH:MM","HH:MM")
    """
    if not existe_tabla_id("medico", id_medico):
        return False, "No existe médico"
    if dia_semana < 0 or dia_semana > 6:
        return False, "Día inválido"
    ok, msg = _validar_intervalos(bloques)
    if not ok:
        return False, msg
    try:
        conexion, cursor = conectar()
        cursor.execute("DELETE FROM horario_medico WHERE id_medico=? AND dia_semana=?", (id_medico, dia_semana))
        for ini, fin in bloques:
            cursor.execute(
                "INSERT INTO horario_medico (id_medico, dia_semana, hora_inicio, hora_fin, tipo) VALUES (?,?,?,?,?)",
                (id_medico, dia_semana, ini, fin, tipo)
            )
        conexion.commit()
        conexion.close()
        return True, "Horarios reemplazados"
    except Exception as e:
        try:
            conexion.close()
        except Exception:
            pass
        return False, f"Error al guardar horarios: {e}"

def eliminar_horarios_dia(id_medico, dia_semana):
    if not existe_tabla_id("medico", id_medico):
        return False, "No existe médico"
    try:
        conexion, cursor = conectar()
        cursor.execute("DELETE FROM horario_medico WHERE id_medico=? AND dia_semana=?", (id_medico, dia_semana))
        cambios = cursor.rowcount
        conexion.commit()
        conexion.close()
        return True, f"{cambios} bloque(s) eliminados"
    except Exception as e:
        return False, str(e)

def medicos_disponibles(dia_semana, hora_str):
    conexion, cursor = conectar()
    cursor.execute(
        """
        SELECT DISTINCT m.id, m.nombre, m.apellido
        FROM horario_medico h
        JOIN medico m ON h.id_medico = m.id
        WHERE h.dia_semana=? AND h.hora_inicio <= ? AND h.hora_fin > ?
        ORDER BY m.nombre
        """,
        (dia_semana, hora_str, hora_str)
    )
    filas = cursor.fetchall()
    conexion.close()
    return filas
