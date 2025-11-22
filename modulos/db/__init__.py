from .db import conectar, existe_tabla_id
from .utilidades import formatear_rut, validar_rut, validar_email, validar_telefono
from .busqueda import buscar_registros_exactos

# También importamos los módulos principales para que estén disponibles
from . import (
    atencion,
    busqueda,
    cita,
    db,
    diagnostico,
    especialidad,
    historial,
    medico,
    paciente,
    tratamiento,
    utilidades
)

# Exponer las funciones y módulos principales
__all__ = [
    'conectar',
    'existe_tabla_id',
    'formatear_rut',
    'validar_rut',
    'validar_email',
    'validar_telefono',
    'buscar_registros_exactos',
    'atencion',
    'busqueda',
    'cita',
    'db',
    'diagnostico',
    'especialidad',
    'historial',
    'medico',
    'paciente',
    'tratamiento',
    'utilidades'
]
