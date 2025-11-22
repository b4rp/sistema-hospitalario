import os
import sqlite3
from cryptography.fernet import Fernet

# ======================================================
# RUTAS
# ======================================================
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # carpeta raíz del proyecto
DB_PATH = os.path.join(BASE_PATH, "hospital.db")
SQL_PATH = os.path.join(BASE_PATH, "hospital.sql")
KEY_PATH = os.path.join(BASE_PATH, "clave.key")

# ======================================================
# WHITELIST DE TABLAS VÁLIDAS (Prevención SQL Injection)
# ======================================================
TABLAS_VALIDAS = {
    'especialidad', 'medico', 'paciente', 'cita', 'diagnostico',
    'tratamiento', 'historial', 'atencion', 'horario_medico'
}

# ======================================================
# GESTIÓN DE CLAVE DE CIFRADO
# ======================================================
def obtener_fernet():
    if not os.path.exists(KEY_PATH):
        print("No se encontró 'clave.key'. Creando una nueva clave de cifrado...")
        clave = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(clave)
        print(f"🔑 Clave generada y guardada en: {KEY_PATH}")
    else:
        print(f"🔑 Clave de cifrado ya existe en: {KEY_PATH}")
        with open(KEY_PATH, "rb") as f:
            clave = f.read()
        try:
            Fernet(clave)
        except Exception:
            raise ValueError("El archivo 'clave.key' está dañado o no es una clave válida.")
    return Fernet(clave)

fernet = obtener_fernet()

# ======================================================
# CREACIÓN DE BASE DE DATOS
# ======================================================
if not os.path.exists(DB_PATH):
    print("Base de datos no existe. Creando desde hospital.sql...")
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    if not os.path.exists(SQL_PATH):
        raise FileNotFoundError(f"No se encontró hospital.sql en: {SQL_PATH}")

    with open(SQL_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    cursor.executescript(sql_script)
    conexion.commit()
    conexion.close()
    print(f"✅ Base de datos creada correctamente en: {DB_PATH}")
else:
    print(f"✅ Base de datos ya existe en: {DB_PATH}")

# ======================================================
# FUNCIONES DE CONEXIÓN Y UTILIDAD
# ======================================================
def conectar():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    return conexion, cursor

def existe_tabla_id(tabla, id_val):
    """Verifica si existe un registro con el ID dado en la tabla.
    
    Args:
        tabla: Nombre de la tabla (validado contra whitelist)
        id_val: ID a verificar
    
    Returns:
        bool: True si existe el registro
    
    Raises:
        ValueError: Si la tabla no está en TABLAS_VALIDAS
    """
    if tabla not in TABLAS_VALIDAS:
        raise ValueError(f"Tabla '{tabla}' no permitida. Tablas válidas: {TABLAS_VALIDAS}")
    
    conexion, cursor = conectar()
    # Seguro usar f-string porque tabla fue validada
    cursor.execute(f"SELECT 1 FROM {tabla} WHERE id = ?", (id_val,))
    existe = cursor.fetchone() is not None
    conexion.close()
    return existe

# ======================================================
# FUNCIONES DE CIFRADO Y DESCIFRADO
# ======================================================
def cifrar_dato(texto):
    """Cifra cualquier dato convirtiéndolo a cadena previamente.
    Acepta None, str, date, datetime, int, etc. Retorna str cifrado.
    """
    if texto is None:
        return None
    if not isinstance(texto, str):
        texto = str(texto)
    return fernet.encrypt(texto.encode()).decode()

def descifrar_dato(texto_cifrado):
    if texto_cifrado is None:
        return None
    return fernet.decrypt(texto_cifrado.encode()).decode()

# ======================================================
# ASEGURAR TABLA HORARIO_MEDICO (migración ligera)
# ======================================================
def asegurar_tabla_horario():
    try:
        conexion, cursor = conectar()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='horario_medico'")
        existe = cursor.fetchone() is not None
        if not existe:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS horario_medico (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_medico INTEGER NOT NULL,
                    dia_semana INTEGER NOT NULL CHECK(dia_semana BETWEEN 0 AND 6),
                    hora_inicio TIME NOT NULL,
                    hora_fin TIME NOT NULL,
                    tipo TEXT,
                    FOREIGN KEY (id_medico) REFERENCES medico(id)
                        ON UPDATE NO ACTION ON DELETE CASCADE
                );
                """
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_horario_medico_medico_dia ON horario_medico(id_medico, dia_semana);")
            conexion.commit()
        conexion.close()
    except Exception as e:
        try:
            conexion.close()
        except Exception:
            pass
        print(f"[WARN] No se pudo asegurar la tabla horario_medico: {e}")

asegurar_tabla_horario()
