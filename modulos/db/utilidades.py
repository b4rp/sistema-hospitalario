import unicodedata
import re
from itertools import cycle
from datetime import date

def normalizar_texto(texto):
    '''
    Normaliza un texto removiendo acentos y conviertiendolo a minusculas
    '''
    
    if texto is None:
        return ""

    # Convertir a minúsculas
    texto = str(texto).lower()
    
    # Normalizar caracteres unicode (separar letras de acentos)
    texto = unicodedata.normalize('NFD', texto)
    
    # Remover acentos
    texto_sin_acentos = ""
    for char in texto:
        # Si el caracter NO es una marca diacrítica (acento), lo agregamos
        if unicodedata.category(char) != 'Mn':
            texto_sin_acentos += char
    
    return texto_sin_acentos


def validar_email(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_telefono(telefono):
    # Valida formato de teléfono (solo números, 8-15 dígitos)
    patron = r'^\+?[0-9]{8,15}$'
    return re.match(patron, telefono.replace(" ", "").replace("-", "")) is not None


def calcular_dv(rut_num):
    rut_str = str(rut_num)
    digitos = list(reversed(rut_str))
    serie = cycle([2, 3, 4, 5, 6, 7])
    suma = 0
    for digito, factor in zip(digitos, serie):
        suma += int(digito) * factor
    residuo = 11 - (suma % 11)
    if residuo == 11:
        return "0"
    elif residuo == 10:
        return "K"
    else:
        return str(residuo)

def validar_rut(rut):
    rut = rut.upper().replace(".", "").replace("-", "")
    if len(rut) < 2:
        return False
    rut_num_str = rut[:-1]
    dv_ingresado = rut[-1]
    if not rut_num_str.isdigit():
        return False
    dv_calculado = calcular_dv(int(rut_num_str))
    return dv_ingresado == dv_calculado


def formatear_rut(rut):
    """
    Devuelve el RUT con formato estándar chileno: 12.345.678-9
    Acepta entrada con o sin puntos y guion.
    """
    rut = rut.replace(".", "").replace("-", "").strip().upper()
    if len(rut) < 2:
        return rut  # evita errores si el usuario deja campo vacío
    cuerpo, dv = rut[:-1], rut[-1]
    cuerpo_formateado = f"{int(cuerpo):,}".replace(",", ".")
    return f"{cuerpo_formateado}-{dv}"

def es_menor_de_edad(fecha_nacimiento):
    """Devuelve True si el paciente tiene menos de 18 años."""
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )
    return edad < 18