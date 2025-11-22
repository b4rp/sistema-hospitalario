import streamlit as st
import pandas as pd
import re
import time
from datetime import date, datetime
from modulos.db.paciente import (
    agregar_paciente,
    mostrar_pacientes,
    eliminar_paciente_por_rut,
    actualizar_paciente,
    eliminar_paciente
)
from modulos.db.utilidades import (
    formatear_rut,
    validar_rut,
    validar_email,
    validar_telefono,
    es_menor_de_edad
)

# Lista completa de países del mundo
PAISES = [
    "Afganistán", "Albania", "Alemania", "Andorra", "Angola", "Antigua y Barbuda", "Arabia Saudita", "Argelia",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaiyán", "Bahamas", "Bahrein", "Bangladesh", "Barbados",
    "Bélgica", "Belice", "Benín", "Bielorrusia", "Birmania", "Bolivia", "Bosnia y Herzegovina", "Botsuana", "Brasil",
    "Brunéi", "Bulgaria", "Burkina Faso", "Burundi", "Bután", "Cabo Verde", "Camboya", "Camerún", "Canadá", "Catar",
    "Chad", "Chequia", "Chile", "China", "Chipre", "Ciudad del Vaticano", "Colombia", "Comoras", "Corea del Norte",
    "Corea del Sur", "Costa de Marfil", "Costa Rica", "Croacia", "Cuba", "Dinamarca", "Dominica", "Ecuador", "Egipto",
    "El Salvador", "Emiratos Árabes Unidos", "Eritrea", "Eslovaquia", "Eslovenia", "España", "Estonia", "Eswatini",
    "Estados Unidos", "Etiopía", "Filipinas", "Finlandia", "Fiyi", "Francia", "Gabón", "Gambia", "Georgia", "Ghana",
    "Granada", "Grecia", "Guatemala", "Guinea", "Guinea-Bisáu", "Guinea Ecuatorial", "Guyana", "Haití", "Honduras",
    "Hungría", "India", "Indonesia", "Irak", "Irán", "Irlanda", "Islandia", "Islas Marshall", "Islas Salomón", "Israel",
    "Italia", "Jamaica", "Japón", "Jordania", "Kazajistán", "Kenia", "Kirguistán", "Kiribati", "Kosovo", "Kuwait",
    "Laos", "Lesoto", "Letonia", "Líbano", "Liberia", "Libia", "Liechtenstein", "Lituania", "Luxemburgo",
    "Macedonia del Norte", "Madagascar", "Malasia", "Malaui", "Maldivas", "Malí", "Malta", "Marruecos", "Mauricio",
    "Mauritania", "México", "Micronesia", "Moldavia", "Mónaco", "Mongolia", "Montenegro", "Mozambique", "Namibia",
    "Nauru", "Nepal", "Nicaragua", "Níger", "Nigeria", "Noruega", "Nueva Zelanda", "Omán", "Países Bajos", "Pakistán",
    "Palaos", "Palestina", "Panamá", "Papúa Nueva Guinea", "Paraguay", "Perú", "Polonia", "Portugal", "Puerto Rico",
    "Reino Unido", "República Centroafricana", "República del Congo", "República Democrática del Congo",
    "República Dominicana", "Ruanda", "Rumanía", "Rusia", "Samoa", "San Cristóbal y Nieves", "San Marino",
    "San Vicente y las Granadinas", "Santa Lucía", "Santo Tomé y Príncipe", "Senegal", "Serbia", "Seychelles",
    "Sierra Leona", "Singapur", "Siria", "Somalia", "Sri Lanka", "Sudáfrica", "Sudán", "Sudán del Sur", "Suecia",
    "Suiza", "Surinam", "Tailandia", "Tanzania", "Tayikistán", "Timor Oriental", "Togo", "Tonga", "Trinidad y Tobago",
    "Túnez", "Turkmenistán", "Turquía", "Tuvalu", "Ucrania", "Uganda", "Uruguay", "Uzbekistán", "Vanuatu", "Venezuela",
    "Vietnam", "Yemen", "Yibuti", "Zambia", "Zimbabue"
]


def limpiar_rut(rut_valor):
    """Elimina puntos, guiones y espacios del RUT y lo convierte a minúsculas."""
    if pd.isna(rut_valor):
        return ""
    rut_texto = str(rut_valor)
    rut_limpio = re.sub(r"[^0-9kK]", "", rut_texto)
    return rut_limpio.lower()

def calcular_edad(fecha_nacimiento):
    """Calcula la edad a partir de la fecha de nacimiento."""
    if pd.isna(fecha_nacimiento):
        return None
    if isinstance(fecha_nacimiento, str):
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    return edad

def mostrar_seccion_pacientes():
    st.header("Pacientes")
    tab_listar, tab_crear, tab_actualizar, tab_eliminar = st.tabs(
        ["📋 Listar", "➕ Crear", "🔄 Actualizar", "❌ Eliminar"]
    )

    # Tab Listar
    with tab_listar:
        st.subheader("Lista de Pacientes")
        
        data = mostrar_pacientes()
        if data:
            df = pd.DataFrame(data)
            df.columns = [c.lower() for c in df.columns]
            
            # Búsqueda avanzada
            st.markdown("### 🔍 Búsqueda Avanzada")
            with st.expander("Filtros de búsqueda", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    filtro_id = st.number_input(
                        "ID",
                        min_value=0,
                        step=1,
                        key="pac_list_filtro_id",
                        help="0 para mostrar todos"
                    )
                
                with col2:
                    filtro_nombre = st.text_input(
                        "Nombre",
                        key="pac_list_filtro_nombre",
                        placeholder="Ej: Juan"
                    )
                
                with col3:
                    filtro_apellido = st.text_input(
                        "Apellido",
                        key="pac_list_filtro_apellido",
                        placeholder="Ej: Pérez"
                    )
                
                with col4:
                    filtro_rut = st.text_input(
                        "RUT",
                        key="pac_list_filtro_rut",
                        placeholder="12.345.678-9"
                    )
                
                col5, col6, col7, col8 = st.columns(4)
                
                with col5:
                    filtro_genero = st.selectbox(
                        "Género",
                        ["Todos", "Masculino", "Femenino"],
                        key="pac_list_filtro_gen"
                    )
                
                with col6:
                    # Definir filtro de nacionalidad
                    nac_unicas = ["Todas"]
                    if "nacionalidad" in df.columns:
                        nac_unicas = ["Todas"] + sorted(df["nacionalidad"].dropna().unique().tolist())
                    filtro_nacionalidad = st.selectbox(
                        "Nacionalidad",
                        nac_unicas,
                        key="pac_list_filtro_nac"
                    )
                
                with col7:
                    filtro_sistema = st.selectbox(
                        "Sistema de Salud",
                        ["Todos", "Isapre", "Fonasa"],
                        key="pac_list_filtro_sis"
                    )
                
                with col8:
                    filtro_edad = st.selectbox(
                        "Edad",
                        ["Todos", "Menores de 18", "Mayores de 18"],
                        key="pac_list_filtro_edad"
                    )
            
            # Crear una copia del DataFrame para aplicar filtros
            df_filtrado = df.copy()
            
            # Aplicar filtros
            if "rut" in df_filtrado.columns:
                df_filtrado["rut_limpio"] = df_filtrado["rut"].apply(limpiar_rut)
            
            # Filtro por ID
            if filtro_id > 0:
                df_filtrado = df_filtrado[df_filtrado["id"] == filtro_id]
            
            if filtro_nombre and filtro_nombre.strip():
                df_filtrado = df_filtrado[df_filtrado["nombre"].str.contains(filtro_nombre, case=False, na=False)]
            
            if filtro_apellido and filtro_apellido.strip():
                df_filtrado = df_filtrado[df_filtrado["apellido"].str.contains(filtro_apellido, case=False, na=False)]
            
            if filtro_rut and filtro_rut.strip():
                filtro_rut_limpio = limpiar_rut(filtro_rut)
                if "rut_limpio" in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado["rut_limpio"].str.contains(filtro_rut_limpio, na=False)]
            
            if filtro_genero != "Todos":
                df_filtrado = df_filtrado[df_filtrado["genero"] == filtro_genero]
            
            if "nacionalidad" in df_filtrado.columns and filtro_nacionalidad != "Todas":
                df_filtrado = df_filtrado[df_filtrado["nacionalidad"] == filtro_nacionalidad]
            
            if "sistema_salud" in df_filtrado.columns and filtro_sistema != "Todos":
                df_filtrado = df_filtrado[df_filtrado["sistema_salud"] == filtro_sistema]
            
            if filtro_edad != "Todos" and "fecha_nacimiento" in df_filtrado.columns:
                df_filtrado["edad"] = df_filtrado["fecha_nacimiento"].apply(calcular_edad)
                if filtro_edad == "Menores de 18":
                    df_filtrado = df_filtrado[df_filtrado["edad"] < 18]
                else:
                    df_filtrado = df_filtrado[df_filtrado["edad"] >= 18]
            
            if not df_filtrado.empty:
                # Agregar badges visuales
                if "fecha_nacimiento" in df_filtrado.columns:
                    if "edad" not in df_filtrado.columns:
                        df_filtrado["edad"] = df_filtrado["fecha_nacimiento"].apply(calcular_edad)
                    def _es_menor(x):
                        if x and x < 18:
                            return "Sí"
                        else:
                            return "No"
                    df_filtrado["👶 Menor"] = df_filtrado["edad"].apply(_es_menor)
                
                # Resultados
                st.markdown(f"### 📋 Resultados ({len(df_filtrado)} pacientes encontrados)")
                
                df_para_mostrar = df_filtrado.drop(columns=["rut_limpio"], errors="ignore")
                st.dataframe(df_para_mostrar, hide_index=True, width="stretch")
            else:
                st.warning("No se encontraron resultados con los filtros aplicados.")
        else:
            st.warning("No hay pacientes registrados.")

    # Tab Crear
    with tab_crear:
        st.subheader("Crear Paciente")

        # Mostrar mensaje de éxito (flash) por 5 segundos después del guardado y rerun
        if st.session_state.get("pac_crear_flash"):
            _flash_ph = st.empty()
            _flash_ph.success(st.session_state["pac_crear_flash"])
            time.sleep(5)
            _flash_ph.empty()
            del st.session_state["pac_crear_flash"]

        if "reset_paciente_form" in st.session_state:
            if st.session_state["reset_paciente_form"]:
                st.session_state["pac_crear_rut"] = ""
                st.session_state["pac_crear_nom"] = ""
                st.session_state["pac_crear_ape"] = ""
                # Dejar sin fecha para que no dispare los campos de emergencia
                st.session_state["pac_crear_fn"] = None
                st.session_state["pac_crear_cor"] = ""
                st.session_state["pac_crear_tel"] = ""
                st.session_state["pac_crear_gen"] = "Masculino"
                st.session_state["pac_crear_dir"] = ""
                st.session_state["pac_crear_sis_salud"] = "Fonasa"
                st.session_state["pac_crear_nacionalidad"] = "Chile"
                st.session_state["pac_crear_nom_emerg"] = ""
                st.session_state["pac_crear_ape_emerg"] = ""
                st.session_state["pac_crear_tel_emerg"] = ""
                # Asegurar que los campos de emergencia queden ocultos tras guardar
                st.session_state["mostrar_campos_emergencia_crear"] = False
                st.session_state["reset_paciente_form"] = False

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            rut_input = st.text_input(
                "RUT",
                key="pac_crear_rut",
                placeholder="12.345.678-9"
            )
            # Validación en tiempo real RUT
            if rut_input:
                if validar_rut(rut_input):
                    st.success("✅ RUT válido")
                else:
                    st.error("❌ RUT inválido")
            
            nombre_input = st.text_input(
                "Nombre",
                key="pac_crear_nom",
                placeholder="Ej: Juan"
            )

        with col2:
            apellido_input = st.text_input(
                "Apellido",
                key="pac_crear_ape",
                placeholder="Ej: Pérez"
            )
            fecha_nac_input = st.date_input(
                "Fecha Nacimiento",
                value=None,
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                key="pac_crear_fn"
            )

        with col3:
            correo_input = st.text_input(
                "Correo",
                key="pac_crear_cor",
                placeholder="Ej: juan.perez@correo.com"
            )
            # Validación en tiempo real Email
            if correo_input:
                if validar_email(correo_input):
                    st.success("✅ Email válido")
                else:
                    st.error("❌ Email inválido")
            
            telefono_input = st.text_input(
                "Teléfono",
                key="pac_crear_tel",
                placeholder="Ej: +56912345678"
            )
            # Validación en tiempo real Teléfono
            if telefono_input:
                if validar_telefono(telefono_input):
                    st.success("✅ Teléfono válido")
                else:
                    st.error("❌ Teléfono inválido")

        with col4:
            genero_input = st.selectbox(
                "Género",
                ["Masculino", "Femenino"],
                key="pac_crear_gen"
            )
            direccion_input = st.text_input(
                "Dirección",
                key="pac_crear_dir",
                placeholder="Ej: Av. Libertador 1234, Santiago"
            )
            sistema_salud_input = st.selectbox(
                "Sistema de Salud",
                ["Isapre", "Fonasa"],
                key="pac_crear_sis_salud"
            )
            nacionalidad_input = st.selectbox(
                "Nacionalidad",
                PAISES,
                key="pac_crear_nacionalidad"
            )

        # Verificar si es menor de edad SOLO SI se ha ingresado una fecha
        nombre_emergencia_input = None
        apellido_emergencia_input = None
        telefono_emergencia_input = None
        
        # Inicializar mostrar_campos_emergencia si no existe
        if "mostrar_campos_emergencia_crear" not in st.session_state:
            st.session_state["mostrar_campos_emergencia_crear"] = False
        
        # Actualizar el estado basado en la fecha de nacimiento
        if fecha_nac_input is not None and es_menor_de_edad(fecha_nac_input):
            st.session_state["mostrar_campos_emergencia_crear"] = True
        elif fecha_nac_input is not None and not es_menor_de_edad(fecha_nac_input):
            st.session_state["mostrar_campos_emergencia_crear"] = False
        elif fecha_nac_input is None:
            # Si no hay fecha, no mostramos campos de emergencia
            st.session_state["mostrar_campos_emergencia_crear"] = False
        
        # Solo mostrar campos de emergencia si el estado es True
        if st.session_state["mostrar_campos_emergencia_crear"]:
            st.markdown("---")
            st.warning("⚠️ El paciente es menor de 18 años. Los datos de contacto de emergencia son obligatorios.")
            
            col_emerg1, col_emerg2, col_emerg3 = st.columns(3)
            
            with col_emerg1:
                nombre_emergencia_input = st.text_input(
                    "Nombre Contacto Emergencia *",
                    key="pac_crear_nom_emerg",
                    placeholder="Ej: María"
                )
            
            with col_emerg2:
                apellido_emergencia_input = st.text_input(
                    "Apellido Contacto Emergencia *",
                    key="pac_crear_ape_emerg",
                    placeholder="Ej: González"
                )
            
            with col_emerg3:
                telefono_emergencia_input = st.text_input(
                    "Teléfono Emergencia *",
                    key="pac_crear_tel_emerg",
                    placeholder="Ej: +56987654321"
                )

        if st.button("Agregar Paciente", key="pac_crear_btn"):
            if not fecha_nac_input:
                st.error("La fecha de nacimiento es obligatoria.")
            elif not nombre_input or not nombre_input.strip():
                st.error("El nombre es obligatorio.")
            elif not apellido_input or not apellido_input.strip():
                st.error("El apellido es obligatorio.")
            elif not validar_rut(rut_input):
                st.error("RUT inválido. Formato esperado: 12.345.678-9")
            elif not validar_email(correo_input):
                st.error("Correo inválido. Ejemplo válido: usuario@dominio.cl")
            elif not validar_telefono(telefono_input):
                st.error("Teléfono inválido. Usa solo números o formato +56...")
            else:
                rut_formateado = formatear_rut(rut_input)
                ok, msg = agregar_paciente(
                    rut_formateado,
                    nombre_input,
                    apellido_input,
                    fecha_nac_input,
                    correo_input,
                    telefono_input,
                    genero_input,
                    direccion_input,
                    sistema_salud_input,
                    nacionalidad_input,
                    nombre_emergencia_input,
                    apellido_emergencia_input,
                    telefono_emergencia_input
                )
                if ok:
                    # Mensaje acorde al proyecto tras registro
                    nombre_fmt = (nombre_input or "").strip().title()
                    apellido_fmt = (apellido_input or "").strip().title()
                    extra_emerg = " Se registró contacto de emergencia." if es_menor_de_edad(fecha_nac_input) else ""
                    st.session_state["pac_crear_flash"] = f"✅ Registro exitoso: {nombre_fmt} {apellido_fmt} (RUT {rut_formateado}) fue ingresado correctamente en el sistema.{extra_emerg}"
                    st.session_state["reset_paciente_form"] = True
                    st.session_state["mostrar_campos_emergencia_crear"] = False
                    st.rerun()
                else:
                    st.error(msg)

    # Tab Actualizar
    with tab_actualizar:
        st.subheader("Actualizar Paciente")
        
        # Mensaje flash de actualización por 5 segundos
        if st.session_state.get("pac_upd_flash"):
            _flash_ph_upd = st.empty()
            _flash_ph_upd.success(st.session_state["pac_upd_flash"])
            time.sleep(5)
            _flash_ph_upd.empty()
            del st.session_state["pac_upd_flash"]

        registros = mostrar_pacientes()
        if registros:
            registros_normalizados = []
            for registro in registros:
                registro_min = {}
                for k, v in registro.items():
                    llave_min = k.lower()
                    registro_min[llave_min] = v
                registros_normalizados.append(registro_min)
            
            df = pd.DataFrame(registros_normalizados)
            
            # Filtro por ID
            filtro_id = st.number_input(
                "Filtrar / Seleccionar ID a modificar (0 para mostrar todos)",
                min_value=0,
                value=0,
                key="pac_upd_filtro"
            )
            
            if filtro_id > 0:
                df_filtrado = df[df["id"] == filtro_id]
            else:
                df_filtrado = df
            
            # Si existe el ID ingresado
            if filtro_id > 0 and not df_filtrado.empty:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    rut_upd = st.text_input(
                        "RUT",
                        value="",
                        key="pac_upd_rut",
                        placeholder="Ej: 12.345.678-9"
                    )
                    nombre_upd = st.text_input(
                        "Nombre",
                        value="",
                        key="pac_upd_nom",
                        placeholder="Ej: Juan"
                    )

                with col2:
                    apellido_upd = st.text_input(
                        "Apellido",
                        value="",
                        key="pac_upd_ape",
                        placeholder="Ej: Pérez"
                    )
                    fecha_nac_upd = st.date_input(
                        "Fecha Nacimiento",
                        value=None,
                        min_value=date(1900, 1, 1),
                        max_value=date.today(),
                        key="pac_upd_fn"
                    )

                with col3:
                    correo_upd = st.text_input(
                        "Correo",
                        value="",
                        key="pac_upd_cor",
                        placeholder="Ej: juan.perez@correo.com"
                    )
                    telefono_upd = st.text_input(
                        "Teléfono",
                        value="",
                        key="pac_upd_tel",
                        placeholder="Ej: +56912345678"
                    )

                with col4:
                    genero_upd_select = st.selectbox(
                        "Género",
                        ["Masculino", "Femenino"],
                        key="pac_upd_gen"
                    )

                    direccion_upd = st.text_input(
                        "Dirección",
                        value="",
                        key="pac_upd_dir",
                        placeholder="Ej: Av. Libertador 1234"
                    )

                    sistema_salud_upd = st.selectbox(
                        "Sistema de Salud",
                        ["Isapre", "Fonasa"],
                        key="pac_upd_sis_salud"
                    )
                    
                    nacionalidad_upd = st.selectbox(
                        "Nacionalidad",
                        PAISES,
                        key="pac_upd_nacionalidad"
                    )

                genero_upd = genero_upd_select.strip().capitalize()

                # Verificar si es menor de edad para mostrar campos de emergencia
                nombre_emergencia_upd = None
                apellido_emergencia_upd = None
                telefono_emergencia_upd = None
                
                # Inicializar mostrar_campos_emergencia si no existe
                if "mostrar_campos_emergencia_upd" not in st.session_state:
                    st.session_state["mostrar_campos_emergencia_upd"] = False
                
                # Actualizar el estado basado en la fecha de nacimiento
                if fecha_nac_upd is not None and es_menor_de_edad(fecha_nac_upd):
                    st.session_state["mostrar_campos_emergencia_upd"] = True
                elif fecha_nac_upd is not None and not es_menor_de_edad(fecha_nac_upd):
                    st.session_state["mostrar_campos_emergencia_upd"] = False
                
                # Solo mostrar campos si el estado es True
                if st.session_state["mostrar_campos_emergencia_upd"]:
                    st.markdown("---")
                    st.warning("⚠️ El paciente es menor de 18 años. Los datos de contacto de emergencia son obligatorios.")
                    
                    col_emerg1, col_emerg2, col_emerg3 = st.columns(3)
                    
                    with col_emerg1:
                        nombre_emergencia_upd = st.text_input(
                            "Nombre Contacto Emergencia *",
                            value="",
                            key="pac_upd_nom_emerg",
                            placeholder="Ej: María"
                        )
                    
                    with col_emerg2:
                        apellido_emergencia_upd = st.text_input(
                            "Apellido Contacto Emergencia *",
                            value="",
                            key="pac_upd_ape_emerg",
                            placeholder="Ej: González"
                        )
                    
                    with col_emerg3:
                        telefono_emergencia_upd = st.text_input(
                            "Teléfono Emergencia *",
                            value="",
                            key="pac_upd_tel_emerg",
                            placeholder="Ej: +56987654321"
                        )

                if st.button("Actualizar Paciente", key=f"pac_upd_btn_{filtro_id}", type="primary"):
                    if not nombre_upd or not nombre_upd.strip():
                        st.error("El nombre es obligatorio.")
                    elif not apellido_upd or not apellido_upd.strip():
                        st.error("El apellido es obligatorio.")
                    elif not rut_upd or not rut_upd.strip():
                        st.error("El RUT es obligatorio.")
                    elif not validar_rut(rut_upd):
                        st.error("RUT inválido. Formato esperado: 12.345.678-9")
                    elif not correo_upd or not correo_upd.strip():
                        st.error("El correo es obligatorio.")
                    elif not validar_email(correo_upd):
                        st.error("Correo inválido. Ejemplo válido: usuario@dominio.cl")
                    elif not telefono_upd or not telefono_upd.strip():
                        st.error("El teléfono es obligatorio.")
                    elif not validar_telefono(telefono_upd):
                        st.error("Teléfono inválido. Usa solo números o formato +56...")
                    elif not fecha_nac_upd:
                        st.error("La fecha de nacimiento es obligatoria.")
                    elif es_menor_de_edad(fecha_nac_upd) and (not nombre_emergencia_upd or not apellido_emergencia_upd or not telefono_emergencia_upd):
                        st.error("Para pacientes menores de 18 años, los datos de contacto de emergencia son obligatorios.")
                    else:
                        rut_upd_formateado = formatear_rut(rut_upd)
                        ok, msg = actualizar_paciente(
                            filtro_id,
                            rut_upd_formateado,
                            nombre_upd,
                            apellido_upd,
                            fecha_nac_upd,
                            correo_upd,
                            telefono_upd,
                            genero_upd,
                            direccion_upd,
                            sistema_salud_upd,
                            nacionalidad_upd,
                            nombre_emergencia_upd,
                            apellido_emergencia_upd,
                            telefono_emergencia_upd
                        )
                        if ok:
                            nombre_fmt = (nombre_upd or "").strip().title()
                            apellido_fmt = (apellido_upd or "").strip().title()
                            st.session_state["pac_upd_flash"] = f"✅ Actualización exitosa: {nombre_fmt} {apellido_fmt} (RUT {rut_upd_formateado}) fue actualizado correctamente."
                            st.session_state["mostrar_campos_emergencia_upd"] = False
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                st.info("Ingrese un ID mayor a 0 para modificar un registro.")

            st.markdown("-----")
            st.markdown("#### Pacientes registrados")
            st.dataframe(df_filtrado, hide_index=True, width="stretch")
        else:
            st.info("No hay registros.")

    # Tab Eliminar
    with tab_eliminar:
        st.subheader("Eliminar Paciente")
        data = mostrar_pacientes()

        if data:
            df = pd.DataFrame(data)
            df.columns = [c.lower() for c in df.columns]

            # Filtro por ID
            filtro_id = st.number_input(
                "Filtrar / Seleccionar ID a eliminar (0 para mostrar todos)",
                min_value=0,
                value=0,
                key="pac_del_filtro_id"
            )

            # Aplicar filtro
            if filtro_id > 0:
                df_filtrado = df[df["id"] == filtro_id]
            else:
                df_filtrado = df

            # Botón para eliminar
            if filtro_id > 0:
                if st.button("Eliminar", key=f"pac_del_btn_{filtro_id}"):
                    ok, msg = eliminar_paciente(filtro_id)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.info("Ingrese un ID mayor a 0 para eliminar un registro.")

            st.markdown("-----")
            st.markdown("#### Pacientes registrados")

            df_mostrar = df_filtrado.rename(columns={
                "id": "ID",
                "rut": "RUT",
                "nombre": "Nombre",
                "apellido": "Apellido",
                "fecha_nacimiento": "Fecha Nacimiento",
                "correo": "Correo",
                "telefono": "Teléfono",
                "genero": "Género",
                "direccion": "Dirección",
                "sistema_salud": "Sistema de Salud",
                "nacionalidad": "Nacionalidad",
                "nombre_emergencia": "Nombre Emergencia",
                "apellido_emergencia": "Apellido Emergencia",
                "telefono_emergencia": "Teléfono Emergencia"
            })
            st.dataframe(df_mostrar, hide_index=True, width="stretch")

        else:
            st.info("No hay registros.")
