import streamlit as st

# Importar módulos UI
from modulos.ui.especialidades import mostrar_seccion_especialidades
from modulos.ui.medicos import mostrar_seccion_medicos
from modulos.ui.pacientes import mostrar_seccion_pacientes
from modulos.ui.citas import mostrar_seccion_citas
from modulos.ui.diagnosticos import mostrar_seccion_diagnosticos
from modulos.ui.tratamientos import mostrar_seccion_tratamientos
from modulos.ui.historiales import mostrar_seccion_historiales
from modulos.ui.atenciones import mostrar_seccion_atenciones

# Configuración de la página
st.set_page_config(
    page_title="Sistema Hospitalario",
    page_icon="⚕️",
    layout="wide"
)

# Header con título e icono médico personalizado
st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='margin: 0; font-size: 3em; color: #FFFFFF;'>⚕️ Sistema Hospitalario</h1>
        <p style='color: #FFFFFF; font-size: 1.2em; margin-top: 10px;'>Gestión Integral de Pacientes y Atención Médica</p>
    </div>
""", unsafe_allow_html=True)

# Navegación principal
st.sidebar.header("Navegación")
menu = ["Especialidades", "Médicos", "Pacientes", "Citas", "Diagnósticos", "Tratamientos", "Historiales", "Atenciones"]
seccion = st.sidebar.selectbox("Ir a", menu)

# Mostrar sección seleccionada
if seccion == "Especialidades":
    mostrar_seccion_especialidades()
elif seccion == "Médicos":
    mostrar_seccion_medicos()
elif seccion == "Pacientes":
    mostrar_seccion_pacientes()
elif seccion == "Citas":
    mostrar_seccion_citas()
elif seccion == "Diagnósticos":
    mostrar_seccion_diagnosticos()
elif seccion == "Tratamientos":
    mostrar_seccion_tratamientos()
elif seccion == "Historiales":
    mostrar_seccion_historiales()
elif seccion == "Atenciones":
    mostrar_seccion_atenciones()