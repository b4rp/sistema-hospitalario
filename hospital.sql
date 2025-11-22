-- ===========================================================
-- PROYECTO: SISTEMA DE GESTIÓN HOSPITAL
-- Autores: Matías Bórquz y Benjamín Rivera
-- Fecha: 21/10/2025
-- ===========================================================

-- ===========================================================
-- 1. CREACIÓN DE TABLAS BASE
-- ===========================================================

-- Tabla de especialidades médicas
CREATE TABLE IF NOT EXISTS especialidad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR NOT NULL,
    descripcion TEXT NOT NULL
);

-- Tabla de médicos
CREATE TABLE IF NOT EXISTS medico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rut VARCHAR NOT NULL UNIQUE,
    nombre VARCHAR NOT NULL,
    apellido VARCHAR NOT NULL,
    correo VARCHAR NOT NULL UNIQUE,
    telefono VARCHAR NOT NULL UNIQUE,
    id_especialidad INTEGER NOT NULL,
    horario TEXT,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- Tabla de pacientes
CREATE TABLE IF NOT EXISTS paciente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rut VARCHAR NOT NULL UNIQUE,
    nombre VARCHAR NOT NULL,
    apellido VARCHAR NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    correo VARCHAR NOT NULL UNIQUE,
    telefono VARCHAR NOT NULL UNIQUE,
    genero VARCHAR NOT NULL CHECK(genero IN ('Masculino','Femenino')),
    direccion VARCHAR NOT NULL,
    sistema_salud VARCHAR NOT NULL CHECK(sistema_salud IN ('Isapre', 'Fonasa')),
    nacionalidad VARCHAR NOT NULL,
    nombre_emergencia TEXT,
    apellido_emergencia TEXT,
    telefono_emergencia TEXT
);

-- Tabla de citas médicas
CREATE TABLE IF NOT EXISTS cita (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    estado VARCHAR NOT NULL DEFAULT 'PENDIENTE' 
        CHECK(estado IN ('PENDIENTE','REALIZADA','CANCELADA')),
    motivo TEXT NOT NULL,
    id_paciente INTEGER NOT NULL,
    id_medico INTEGER,
    FOREIGN KEY (id_paciente) REFERENCES paciente(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY (id_medico) REFERENCES medico(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- Tabla de diagnósticos
CREATE TABLE IF NOT EXISTS diagnostico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL,
    descripcion TEXT NOT NULL,
    id_medico INTEGER NOT NULL,
    id_cita INTEGER NOT NULL,
    FOREIGN KEY (id_medico) REFERENCES medico(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY (id_cita) REFERENCES cita(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- Tabla de tratamientos
CREATE TABLE IF NOT EXISTS tratamiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_inicio DATE NOT NULL,
    fecha_termino DATE NOT NULL,
    tratamiento TEXT NOT NULL,
    id_diagnostico INTEGER NOT NULL,
    FOREIGN KEY (id_diagnostico) REFERENCES diagnostico(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- Tabla de historiales médicos
CREATE TABLE IF NOT EXISTS historial (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_registro DATETIME NOT NULL,
    id_diagnostico INTEGER NOT NULL,
    id_tratamiento INTEGER NOT NULL,
    observaciones TEXT NOT NULL,
    alergias TEXT NOT NULL,
    resultado_examen TEXT NOT NULL,
    id_paciente INTEGER NOT NULL,
    id_cita INTEGER NOT NULL,
    FOREIGN KEY (id_paciente) REFERENCES paciente(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY (id_cita) REFERENCES cita(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY (id_tratamiento) REFERENCES tratamiento(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY (id_diagnostico) REFERENCES diagnostico(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- Tabla de atenciones
CREATE TABLE IF NOT EXISTS atencion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_diagnostico INTEGER NOT NULL,
    id_historial INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    FOREIGN KEY (id_diagnostico) REFERENCES diagnostico(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY (id_historial) REFERENCES historial(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- ===========================================================
-- 2. CREACIÓN DE VISTAS
-- ===========================================================

CREATE VIEW vista_pacientes_medicos AS
SELECT 
    p.nombre || ' ' || p.apellido AS paciente,
    m.nombre || ' ' || m.apellido AS medico,
    c.fecha, c.hora, c.estado, c.motivo
FROM cita c
JOIN paciente p ON c.id_paciente = p.id
JOIN medico m ON c.id_medico = m.id;

CREATE VIEW vista_historial_completo AS
SELECT 
    h.id AS id_historial,
    p.nombre || ' ' || p.apellido AS paciente,
    d.descripcion AS diagnostico,
    t.tratamiento AS tratamiento,
    h.fecha_registro, h.observaciones, h.resultado_examen
FROM historial h
JOIN paciente p ON h.id_paciente = p.id
JOIN diagnostico d ON h.id_diagnostico = d.id
JOIN tratamiento t ON h.id_tratamiento = t.id;

-- ===========================================================
-- 3. CREACIÓN DE ÍNDICES
-- ===========================================================

CREATE INDEX idx_paciente_rut ON paciente(rut);
CREATE INDEX idx_cita_estado ON cita(estado);
CREATE INDEX idx_diagnostico_medico ON diagnostico(id_medico);
CREATE INDEX idx_medico_especialidad ON medico(id_especialidad);

-- ===========================================================
-- 4. TABLA DE HORARIOS DE MÉDICOS (Nueva)
-- ===========================================================
-- Permite múltiples bloques por día de la semana por médico.
-- dia_semana: 0=Lunes .. 6=Domingo
-- Restricción lógica (validada en aplicación): hora_inicio < hora_fin y no solapamiento.
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

CREATE INDEX IF NOT EXISTS idx_horario_medico_medico_dia ON horario_medico(id_medico, dia_semana);



-- ===========================================================
-- FIN DEL SCRIPT

-- ===========================================================
