"""
Script para poblar la base de datos con datos de prueba
Ejecutar desde la raíz del proyecto:
    python scripts/datos_pruebas.py

El script pregunta al usuario cuántos registros desea generar (1-100).
Crea automáticamente clave.key y hospital.db si no existen.
Solo inserta datos; no elimina ni resetea tablas.
"""
import os
import sys
from datetime import date, time, timedelta, datetime

# Asegurar que el directorio raíz del proyecto esté en sys.path para poder
# importar el paquete `modulos` aun cuando no exista __init__.py
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modulos.db.especialidad import agregar_especialidad, mostrar_especialidades
from modulos.db.paciente import agregar_paciente, mostrar_pacientes
from modulos.db.medico import crear_medico, mostrar_medicos
from modulos.db.cita import agregar_cita, mostrar_citas
from modulos.db.utilidades import calcular_dv, formatear_rut, normalizar_texto
from modulos.db.diagnostico import agregar_diagnostico, obtener_diagnosticos
from modulos.db.tratamiento import agregar_tratamiento, obtener_tratamientos
from modulos.db.historial import agregar_historial, obtener_historiales
from modulos.db.atencion import agregar_atencion, obtener_atenciones
from modulos.db.db import obtener_fernet
# Horarios estructurados removidos temporalmente


def gen_rut(num):
    """Genera un RUT válido a partir de la parte numérica (int)."""
    dv = calcular_dv(num)
    rut_raw = f"{num}{dv}"
    return formatear_rut(rut_raw)


def main():
    # Inicializa cifrado/BD (crea 'clave.key' y 'hospital.db' si faltan)
    print("="*60)
    print("GENERADOR DE DATOS DE PRUEBA - SISTEMA HOSPITALARIO")
    print("="*60)
    obtener_fernet()
    
    # Preguntar al usuario cuántos datos quiere generar
    while True:
        try:
            cantidad_input = input("\n¿Cuántos registros deseas generar por sección? (1-100, recomendado: 70): ").strip()
            if not cantidad_input:
                N = 70  # valor por defecto
                print(f"Usando valor por defecto: {N} registros")
                break
            N = int(cantidad_input)
            if 1 <= N <= 100:
                print(f"Se generarán {N} registros por cada sección")
                break
            else:
                print("⚠️  Por favor ingresa un número entre 1 y 100")
        except ValueError:
            print("⚠️  Por favor ingresa un número válido")
        except KeyboardInterrupt:
            print("\n\n❌ Operación cancelada por el usuario")
            return

    resultados = {
        "especialidad": [], "paciente": [], "medico": [], "cita": [],
        "diagnostico": [], "tratamiento": [], "historial": [], "atencion": []
    }

    # 1) Especialidades
    especialidades = [
        "Cardiología", "Pediatría", "Neurología", "Dermatología", "Ginecología",
        "Oftalmología", "Psiquiatría", "Oncología", "Urología", "Traumatología",
        "Nefrología", "Endocrinología", "Reumatología", "Otorrinolaringología", "Neumología",
        "Gastroenterología", "Hematología", "Infectología", "Geriatría", "Medicina Interna",
        "Cirugía General", "Anestesiología", "Radiología", "Patología", "Medicina Familiar",
        "Medicina del Deporte", "Medicina del Trabajo", "Nutrición", "Kinesiología", "Fonoaudiología",
        "Medicina Intensiva", "Medicina de Urgencia", "Cirugía Plástica", "Cirugía Vascular",
        "Cirugía Cardiovascular", "Neurocirugía", "Cirugía Pediátrica", "Ortopedia", "Podología",
        "Inmunología", "Alergología", "Medicina Nuclear", "Fisiatría", "Genética Médica",
        "Medicina Paliativa", "Medicina Preventiva", "Medicina Estética", "Odontología",
        "Cirugía Maxilofacial", "Periodoncia", "Ortodoncia", "Endodoncia", "Prótesis Dental",
        "Implantología", "Odontopediatría", "Medicina Forense", "Toxicología", "Epidemiología",
        "Salud Pública", "Administración en Salud", "Bioética", "Farmacología Clínica",
        "Terapia Ocupacional", "Psicología Clínica", "Psicopedagogía", "Trabajo Social en Salud",
        "Enfermería de Cuidados Intensivos", "Matronería"
    ]
    # Completar hasta N si falta
    if len(especialidades) < N:
        faltan = N - len(especialidades)
        especialidades += [f"Especialidad Extra {i+1}" for i in range(faltan)]

    print("Insertando especialidades...")
    for nombre in especialidades:
        ok, msg = agregar_especialidad(nombre, f"Descripción de {nombre}")
        resultados["especialidad"].append((ok, msg))
        print(f"  {nombre}: {ok} - {msg}")

    # Obtener IDs de especialidades
    espe_rows = mostrar_especialidades()
    espe_map = {r['nombre']: r['id'] for r in espe_rows}
    espe_ids = [r['id'] for r in espe_rows]

    # 2) Pacientes
    print("\nInsertando pacientes...")
    nombres_m = ["Luis", "Carlos", "Pedro", "Andrés", "Diego", "Mateo", "Benjamín", "Tomás", "Sebastián", "Jorge",
                 "Manuel", "Pablo", "Javier", "Ricardo", "Francisco", "Roberto", "Raúl", "Martín", "Nicolás", "Emilio",
                 "Gabriel", "Eduardo", "Alberto", "Héctor", "Ignacio", "Mauricio", "Rodrigo", "Claudio", "Sergio", "Mario",
                 "Julio", "Álvaro", "Fernando", "Cristian", "Marcelo", "Daniel", "Gustavo", "Rafael", "Lorenzo", "Vicente"]
    nombres_f = ["María", "Ana", "Sofía", "Lucía", "Camila", "Valentina", "Josefa", "Antonia", "Fernanda", "Daniela",
                 "Isabel", "Carmen", "Elena", "Laura", "Patricia", "Carolina", "Andrea", "Mónica", "Teresa", "Rosa",
                 "Gabriela", "Marcela", "Beatriz", "Verónica", "Claudia", "Sandra", "Alejandra", "Natalia", "Paula", "Julia",
                 "Silvia", "Mariana", "Lorena", "Cecilia", "Victoria", "Pilar", "Raquel", "Cristina", "Francisca", "Ximena"]
    apellidos = ["González", "Fernández", "Soto", "Rojas", "López", "Molina", "Vargas", "Cruz", "Castro", "Vega",
                 "Sánchez", "Torres", "Medina", "Pérez", "Suárez", "Navarro", "Herrera", "Ortega", "Muñoz", "Ramos",
                 "Silva", "Reyes", "Morales", "Jiménez", "Díaz", "Álvarez", "Romero", "Gutiérrez", "Alonso", "Ruiz",
                 "Núñez", "Prieto", "Guerrero", "Campos", "Cortés", "Fuentes", "Flores", "Aguilar", "Pizarro", "Salazar",
                 "Miranda", "Bravo", "Araya", "Espinoza", "Sepúlveda", "Contreras", "Valenzuela", "Carrasco", "Lagos", "Godoy"]
    nacionalidades = ["Chile", "Argentina", "Perú", "Colombia", "Brasil", "Uruguay", "Paraguay", "Bolivia",
                      "Ecuador", "Venezuela", "México", "España", "Estados Unidos", "Canadá", "Alemania", "Francia"]

    base_rut = 20000000
    for i in range(N):
        es_mujer = (i % 2 == 1)
        nom = nombres_f[i % len(nombres_f)] if es_mujer else nombres_m[i % len(nombres_m)]
        ape = apellidos[i % len(apellidos)]

        # Definir fecha nacimiento: cada 5º registro será menor de edad
        if i % 5 == 0:
            # Menor entre 12 y 17 años, determinista
            anio = (date.today().year - (12 + (i % 6)))
        else:
            # Adulto entre 20 y 60 años
            anio = (date.today().year - (20 + (i % 41)))
        mes = (i % 12) + 1
        dia = ((i * 3) % 28) + 1
        fecha_nac = date(anio, mes, dia)

        # Contacto de emergencia si es menor
        nom_emerg = ape_emerg = tel_emerg = None
        hoy = date.today()
        edad = (hoy - fecha_nac).days // 365
        if edad < 18:
            nom_emerg = "Contacto"
            ape_emerg = ape
            tel_emerg = f"+569{88000000 + i}"

        num = base_rut + i
        rut = gen_rut(num)
        correo = f"{normalizar_texto(nom)}.{normalizar_texto(ape)}{i}@ejemplo.com"
        telefono = f"+569{70000000 + i}"
        genero = "Femenino" if es_mujer else "Masculino"
        direccion = f"Calle {i+1} #123, Ciudad"
        sistema_salud = "Fonasa" if i % 2 == 0 else "Isapre"
        nacionalidad = nacionalidades[i % len(nacionalidades)]

        ok, msg = agregar_paciente(
            rut,
            nom,
            ape,
            fecha_nac,
            correo,
            telefono,
            genero,
            direccion,
            sistema_salud,
            nacionalidad,
            nom_emerg,
            ape_emerg,
            tel_emerg
        )
        resultados["paciente"].append((ok, msg, rut))
        info_menor = f" [MENOR: {edad} años, Contacto: {nom_emerg} {ape_emerg}]" if nom_emerg else ""
        print(f"  {nom} {ape}: {ok} - {msg} (RUT: {rut}){info_menor}")

    # Obtener IDs de pacientes
    pacientes_rows = mostrar_pacientes()
    pacientes_ids = [r['id'] for r in pacientes_rows]

    # 3) Médicos
    print("\nInsertando médicos...")
    med_nombres = [
        ("Alberto", "Marín"), ("Beatriz", "Pérez"), ("Cristian", "Ruiz"), ("Diana", "Silva"),
        ("Esteban", "Navarro"), ("Fernanda", "Ramos"), ("Gonzalo", "Muñoz"), ("Helena", "Ortega"),
        ("Iván", "Suárez"), ("Julia", "Herrera"), ("Raúl", "Cortés"), ("Patricia", "Fuentes"),
        ("Ricardo", "Aguilar"), ("Carolina", "Pizarro"), ("Mauricio", "Araya"), ("Ximena", "Lagos"),
        ("Álvaro", "Campos"), ("Natalia", "Espinoza"), ("Felipe", "Salazar"), ("Paula", "Godoy"),
        ("Andrés", "Morales"), ("Daniela", "Reyes"), ("Martín", "Jiménez"), ("Sofía", "Díaz"),
        ("Pablo", "Álvarez"), ("Laura", "Romero"), ("Gabriel", "Gutiérrez"), ("Carmen", "Alonso"),
        ("Eduardo", "Prieto"), ("Isabel", "Guerrero"), ("Roberto", "Cortés"), ("Mónica", "Flores"),
        ("Javier", "Bravo"), ("Verónica", "Miranda"), ("Manuel", "Sepúlveda"), ("Sandra", "Contreras"),
        ("Francisco", "Valenzuela"), ("Andrea", "Carrasco"), ("Nicolás", "Lagos"), ("Claudia", "Godoy"),
        ("Ignacio", "Rojas"), ("Marcela", "Vargas"), ("Sergio", "Cruz"), ("Teresa", "Castro"),
        ("Rodrigo", "Vega"), ("Elena", "Sánchez"), ("Mario", "Torres"), ("Rosa", "Medina"),
        ("Julio", "Navarro"), ("Gabriela", "Herrera"), ("Fernando", "Ortega"), ("Beatriz", "Ramos"),
        ("Cristian", "Silva"), ("Lorena", "Fuentes"), ("Marcelo", "Aguilar"), ("Cecilia", "Pizarro"),
        ("Daniel", "Araya"), ("Victoria", "Espinoza"), ("Gustavo", "Salazar"), ("Pilar", "Campos"),
        ("Rafael", "Núñez"), ("Raquel", "Guerrero"), ("Lorenzo", "Prieto"), ("Cristina", "Flores"),
        ("Vicente", "Bravo"), ("Francisca", "Miranda"), ("Emilio", "Sepúlveda"), ("Ximena", "Contreras"),
        ("Héctor", "Valenzuela"), ("Silvia", "Carrasco"), ("Tomás", "Lagos"), ("Mariana", "Godoy")
    ]

    base_rut_med = 30000000
    for i, (nom, ape) in enumerate(med_nombres[:N]):
        num = base_rut_med + i
        rut = gen_rut(num)
        correo = f"{normalizar_texto(nom)}.{normalizar_texto(ape)}@hospital.com"
        telefono = f"+569{61000000 + i}"
        # Usar IDs reales desde la base
        id_esp = espe_ids[i % len(espe_ids)] if espe_ids else 1
        ok, msg = crear_medico(rut, nom, ape, correo, telefono, id_esp)
        resultados["medico"].append((ok, msg, rut))
        print(f"  Dr/a {nom} {ape}: {ok} - {msg} (RUT: {rut}, EspID: {id_esp})")

    med_rows = mostrar_medicos()
    med_ids = [r['id'] for r in med_rows]

    # (Horarios estructurados omitidos)

    # 4) Citas: asignar combinaciones de paciente-medico
    print("\nInsertando citas...")
    motivos = ["Control", "Urgencia", "Consulta", "Revisión", "Cirugía", "Examen", "Seguimiento",
               "Primera vez", "Chequeo preventivo", "Evaluación prequirúrgica", "Control postoperatorio",
               "Certificado médico", "Receta", "Vacunación", "Procedimiento menor"]
    fecha_base = date.today()
    cita_ids = []  # Almacenar IDs de citas para usar en diagnósticos
    for i in range(N):
        fecha = fecha_base + timedelta(days=i)
        hora = time(hour=9 + (i % 8), minute=30)
        motivo = motivos[i % len(motivos)]
        id_paciente = pacientes_ids[i % len(pacientes_ids)] if pacientes_ids else 1
        id_medico = med_ids[i % len(med_ids)] if med_ids else 1
        ok, msg = agregar_cita(fecha, hora, motivo, id_paciente, id_medico)
        resultados["cita"].append((ok, msg))
        # Obtener el ID de la cita recién insertada
        if ok:
            citas_actuales = mostrar_citas()
            for cita in citas_actuales:
                if (cita['fecha'] == str(fecha) and 
                    cita['hora'] == str(hora) and 
                    cita['id_paciente'] == id_paciente and 
                    cita['id_medico'] == id_medico):
                    cita_ids.append(cita['id'])
                    break
        print(f"  Cita {i+1}: {ok} - {msg} (PacienteID: {id_paciente}, MedicoID: {id_medico})")
        
    # 5) Diagnósticos
    print("\nInsertando diagnósticos...")
    diagnosticos = [
        "Hipertensión arterial", "Diabetes mellitus tipo 2", "Migraña crónica", "Dermatitis atópica",
        "Asma bronquial", "Artritis reumatoide", "Gastritis crónica", "Ansiedad generalizada",
        "Hipotiroidismo", "Lumbalgia crónica", "Infección urinaria", "Esguince de tobillo",
        "Rinitis alérgica", "Insomnio", "Anemia ferropénica", "Colesterol alto",
        "Depresión leve", "Bronquitis aguda", "Covid-19 leve", "Otitis media",
        "Faringitis aguda", "Gripe estacional", "Neumonía leve", "Conjuntivitis viral",
        "Úlcera gástrica", "Reflujo gastroesofágico", "Colon irritable", "Apendicitis",
        "Cálculos biliares", "Hígado graso", "Insuficiencia renal crónica", "Cálculos renales",
        "Cistitis", "Prostatitis", "Hiperplasia prostática benigna", "Endometriosis",
        "Ovarios poliquísticos", "Miomas uterinos", "Vaginosis bacteriana", "Candidiasis vaginal",
        "Gonorrea", "Sífilis", "VIH asintomático", "Hepatitis B crónica",
        "Tiña", "Psoriasis", "Acné severo", "Rosácea",
        "Melanoma in situ", "Carcinoma basocelular", "Queratosis actínica", "Herpes zóster",
        "Varicela", "Sarampión", "Dengue", "Fiebre tifoidea",
        "Tuberculosis pulmonar", "Neumonía por COVID-19", "Bronquiectasias", "EPOC",
        "Enfisema pulmonar", "Neumotórax espontáneo", "Derrame pleural", "Embolia pulmonar",
        "Trombosis venosa profunda", "Insuficiencia cardíaca", "Infarto agudo al miocardio", "Angina de pecho",
        "Arritmia cardíaca", "Fibrilación auricular", "Pericarditis", "Valvulopatía mitral"
    ]
    
    diag_ids = []
    for i, desc in enumerate(diagnosticos[:N]):
        if i < len(cita_ids):
            fecha = fecha_base + timedelta(days=i)
            id_medico = med_ids[i % len(med_ids)]
            id_cita = cita_ids[i]
            ok, msg = agregar_diagnostico(fecha, desc, id_medico, id_cita)
            resultados["diagnostico"].append((ok, msg))
            print(f"  Diagnóstico {i+1}: {ok} - {msg}")
    
    # Obtener IDs de diagnósticos creados
    diag_rows = obtener_diagnosticos()
    diag_ids = [d[0] for d in diag_rows] if diag_rows else []

    # 6) Tratamientos
    print("\nInsertando tratamientos...")
    tratamientos = [
        "Enalapril 10mg c/12h + dieta hiposódica", "Metformina 850mg c/12h + plan alimentario",
        "Sumatriptán 50mg SOS + profilaxis", "Betametasona tópica + humectante",
        "Salbutamol inhalador + técnica inhalatoria", "Metotrexato 15mg/sem + ácido fólico",
        "Omeprazol 20mg c/24h + dieta", "Sertralina 50mg c/24h + psicoterapia",
        "Levotiroxina 100mcg c/24h", "Fisioterapia + AINES",
        "Paracetamol 1g c/8h", "Ibuprofeno 400mg SOS",
        "Amoxicilina 500mg c/8h por 7 días", "Loratadina 10mg c/24h",
        "Melatonina 3mg nocte", "Hierro oral 60mg c/24h",
        "Atorvastatina 20mg nocte", "Psicoterapia cognitivo-conductual",
        "Broncodilatador + corticoides inhalados", "Diclofenaco tópico + reposo",
        "Azitromicina 500mg día 1, luego 250mg por 4 días", "Oseltamivir 75mg c/12h por 5 días",
        "Levofloxacino 500mg c/24h + hidratación", "Tobramicina colirio c/6h",
        "Ranitidina 150mg c/12h antes de comidas", "Trimebutina 200mg c/8h",
        "Hioscina 10mg c/8h SOS", "Apendicectomía laparoscópica programada",
        "Ácido ursodesoxicólico 300mg c/12h", "Silimarina 150mg c/8h + dieta",
        "Enalapril 20mg c/24h + diurético", "Litrotripsia extracorpórea programada",
        "Nitrofurantoína 100mg c/12h por 5 días", "Ciprofloxacino 500mg c/12h por 10 días",
        "Finasteride 5mg c/24h", "Dienogest 2mg c/24h continuo",
        "Metformina 850mg c/12h + anticonceptivos orales", "Miomectomía programada",
        "Metronidazol óvulos por 7 noches", "Fluconazol 150mg dosis única",
        "Ceftriaxona IM dosis única + doxiciclina", "Penicilina benzatínica 2.4 millones IM",
        "Antirretrovirales triple esquema", "Tenofovir + emtricitabina c/24h",
        "Terbinafina crema c/12h por 14 días", "Metotrexato 7.5mg/sem + ácido fólico",
        "Isotretinoína 20mg c/24h por 6 meses", "Metronidazol 0.75% gel c/12h",
        "Resección quirúrgica + biopsia", "Cirugía Mohs + reconstrucción",
        "5-fluorouracilo tópico c/24h", "Aciclovir 800mg c/4h por 7 días",
        "Aciclovir 800mg c/6h por 5 días", "Vitamina A 200,000 UI dosis única",
        "Paracetamol + hidratación oral", "Cloroquina + primaquina",
        "Esquema TAES completo por 6 meses", "Oxigenoterapia + antibióticos",
        "Azitromicina 500mg c/24h + salbutamol", "Tiotropio inhalado c/24h",
        "Oxigenoterapia domiciliaria continua", "Tubo de drenaje torácico",
        "Toracocentesis evacuadora", "Anticoagulación con heparina de bajo peso",
        "Rivaroxabán 20mg c/24h por 3 meses", "IECA + diuréticos + betabloqueadores",
        "Angioplastia coronaria con stent", "Nitratos sublinguales SOS",
        "Amiodarona 200mg c/8h", "Anticoagulación oral con warfarina",
        "Colchicina 0.5mg c/12h", "Reemplazo valvular quirúrgico programado"
    ]
    
    trat_ids = []
    for i, desc in enumerate(tratamientos[:N]):
        if i < len(diag_ids):
            fecha_inicio = fecha_base
            fecha_termino = fecha_base + timedelta(days=30)
            id_diagnostico = diag_ids[i]
            ok, msg = agregar_tratamiento(fecha_inicio, fecha_termino, desc, id_diagnostico)
            resultados["tratamiento"].append((ok, msg))
            print(f"  Tratamiento {i+1}: {ok} - {msg}")
    
    # Obtener IDs de tratamientos creados
    trat_rows = obtener_tratamientos()
    trat_ids = [t[0] for t in trat_rows] if trat_rows else []

    # 7) Historiales
    print("\nInsertando historiales...")
    observaciones = [
        "Paciente estable, buena respuesta al tratamiento", "Requiere ajuste de dosis según evolución",
        "Presenta mejoría de síntomas", "Control periódico necesario",
        "En observación por efectos secundarios", "Evolución favorable",
        "Pendiente exámenes de control", "Seguimiento estrecho",
        "Buen pronóstico", "En evaluación",
        "Dolor controlado", "Se recomienda hidratación abundante",
        "Observación en domicilio", "Derivado a especialista",
        "Alta con recomendaciones", "Control en 2 semanas",
        "Se solicita imagenología", "Requiere laboratorio de urgencia",
        "Sin eventos adversos", "Educación al paciente realizada",
        "Respuesta parcial al tratamiento", "Cambio de esquema terapéutico",
        "Tolerancia adecuada a medicamentos", "Pendiente interconsulta",
        "Signos vitales estables", "Afebril sin molestias",
        "Mejoría clínica evidente", "Alta a domicilio con indicaciones",
        "Requiere hospitalización", "Ingreso a UCI",
        "Cirugía programada", "Postoperatorio sin complicaciones",
        "Herida quirúrgica limpia", "Retiro de puntos en 10 días",
        "Rehabilitación kinésica indicada", "Terapia ocupacional necesaria",
        "Evaluación psicológica recomendada", "Apoyo familiar importante",
        "Adherencia al tratamiento regular", "Incumplimiento terapéutico detectado",
        "Pérdida de seguimiento", "Reingreso por recaída",
        "Mejoría radiológica confirmada", "Lesión en regresión",
        "Masa en crecimiento", "Biopsia programada",
        "Resultado anatomopatológico pendiente", "Tumor benigno confirmado",
        "Malignidad descartada", "Estadificación TNM realizada",
        "Quimioterapia adyuvante iniciada", "Radioterapia paliativa",
        "Cuidados paliativos", "Manejo del dolor optimizado",
        "Náuseas controladas", "Apetito conservado",
        "Pérdida de peso significativa", "Ganancia ponderal adecuada",
        "Hidratación oral suficiente", "Suero intravenoso indicado",
        "Transfusión sanguínea realizada", "Hemoglobina en ascenso",
        "Plaquetas normalizadas", "Leucocitos en rango",
        "Función renal preservada", "Insuficiencia renal aguda",
        "Diálisis de urgencia", "Trasplante renal programado",
        "Rechazo agudo descartado", "Inmunosupresión ajustada",
        "Infección oportunista tratada", "Profilaxis antimicrobiana"
    ]
    
    hist_ids = []
    for i, obs in enumerate(observaciones[:N]):
        if i < len(diag_ids) and i < len(trat_ids) and i < len(pacientes_ids) and i < len(cita_ids):
            fecha_registro = (datetime.now() - timedelta(days=i)).date()
            id_diagnostico = diag_ids[i]
            id_tratamiento = trat_ids[i]
            alergias = "Sin alergias conocidas"
            resultado = "Pendiente"
            id_paciente = pacientes_ids[i]
            id_cita = cita_ids[i]
            ok, msg = agregar_historial(
                fecha_registro, id_diagnostico, id_tratamiento,
                obs, alergias, resultado, id_paciente, id_cita
            )
            resultados["historial"].append((ok, msg))
            print(f"  Historial {i+1}: {ok} - {msg}")
    
    # Obtener IDs de historiales creados
    hist_rows = obtener_historiales()
    hist_ids = [h[0] for h in hist_rows] if hist_rows else []

    # 8) Atenciones
    print("\nInsertando atenciones...")
    for i in range(N):
        if i < len(diag_ids) and i < len(hist_ids):
            descripcion = f"Atención de seguimiento #{i+1}"
            id_diagnostico = diag_ids[i]
            id_historial = hist_ids[i]
            ok, msg = agregar_atencion(id_diagnostico, id_historial, descripcion)
            resultados["atencion"].append((ok, msg))
            print(f"  Atención {i+1}: {ok} - {msg}")

    # Resumen final
    print("\n" + "="*60)
    print("✅ INSERCIONES COMPLETADAS")
    print("="*60)
    print(f"Total de registros creados: {N * 8} ({N} por cada una de las 8 secciones)")
    print("="*60)


if __name__ == '__main__':
    main()
