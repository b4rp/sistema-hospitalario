import streamlit as st
import pandas as pd
import re
from modulos.db.medico import (
    crear_medico,
    mostrar_medicos,
    borrar_medico,
    actualizar_medico
)
from modulos.db.utilidades import (
    formatear_rut,
    validar_rut,
    validar_email,
    validar_telefono
)

def limpiar_rut_med(rut_valor):
    """Elimina puntos, guiones y espacios del RUT y lo convierte a minúsculas."""
    if pd.isna(rut_valor):
        return ""
    rut_texto = str(rut_valor)
    rut_limpio = re.sub(r"[^0-9kK]", "", rut_texto)
    return rut_limpio.lower()

def mostrar_seccion_medicos():
    st.header("Médicos")
    
    # Inicializar variables de estado si no existen
    if "med_refresh_list" not in st.session_state:
        st.session_state["med_refresh_list"] = False
    
    tab_listar, tab_crear, tab_actualizar, tab_eliminar = st.tabs(
        ["📋 Listar", "➕ Crear", "🔄 Actualizar", "❌ Eliminar"]
    )

    # Tab Listar
    with tab_listar:
        st.subheader("Lista de Médicos")
    
        # Reset de filtros si se acaba de crear/actualizar/eliminar
        if st.session_state.get("med_refresh_list", False):
            st.session_state["med_list_filtro_nombre"] = ""
            st.session_state["med_list_filtro_apellido"] = ""
            st.session_state["med_list_filtro_rut"] = ""
            st.session_state["med_list_filtro_id"] = 1
            st.session_state["med_list_filtro_id_esp"] = 0
            st.session_state["med_refresh_list"] = False
        
        col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])

        with col1:
            filtro_nombre = st.text_input(
                "Buscar por nombre",
                key="med_list_filtro_nombre",
                placeholder="Ej: Juan"
            )

        with col2:
            filtro_apellido = st.text_input(
                "Buscar por apellido",
                key="med_list_filtro_apellido",
                placeholder="Ej: Pérez"
            )

        with col3:
            filtro_rut = st.text_input(
                "Buscar por RUT",
                key="med_list_filtro_rut",
                placeholder="Ej: 12.345.678-9"
            )

        with col4:
            filtro_id = st.number_input(
                "ID Médico",
                min_value=0,
                step=1,
                key="med_list_filtro_id"
            )

    
        with col5:
            filtro_id_esp = st.number_input(
                "ID Esp.",
                min_value=0,
                step=1,
                key="med_list_filtro_id_esp"
            )

        with st.spinner("Cargando lista de médicos..."):
            # Obtener datos
            data = mostrar_medicos()
        
            if data:
                df = pd.DataFrame(data)

                if df.empty:
                    st.warning("No hay datos para mostrar")
                    return

                # Crear columna de RUT limpio para búsqueda
                if "rut" in df.columns:
                    df["rut_limpio"] = df["rut"].apply(limpiar_rut_med)

                df_filtrado = df.copy()
                filtros_aplicados = False

                
                if filtro_id > 0:
                    df_filtrado = df_filtrado[df_filtrado["id"] == filtro_id]
                    filtros_aplicados = True

    
                if filtro_id_esp > 0:
                    df_filtrado = df_filtrado[df_filtrado["id_especialidad"] == filtro_id_esp]
                    filtros_aplicados = True

            
                if filtro_nombre.strip():
                    df_filtrado = df_filtrado[df_filtrado["nombre"].str.contains(filtro_nombre, case=False, na=False)]
                    filtros_aplicados = True

                if filtro_apellido.strip():
                    df_filtrado = df_filtrado[df_filtrado["apellido"].str.contains(filtro_apellido, case=False, na=False)]
                    filtros_aplicados = True

                if filtro_rut.strip():
                    rut_limp = limpiar_rut_med(filtro_rut)
                    df_filtrado = df_filtrado[df_filtrado["rut_limpio"].str.contains(rut_limp, na=False)]
                    filtros_aplicados = True

                # Si no se aplicó filtro → mostrar todos
                if not filtros_aplicados:
                    df_filtrado = df

                # Preparar tabla
                columnas_a_mostrar = [c for c in df_filtrado.columns if c != "rut_limpio"]
                df_mostrar = df_filtrado[columnas_a_mostrar]

                df_mostrar = df_mostrar.rename(columns={
                    'id': 'ID',
                    'rut': 'RUT',
                    'nombre': 'Nombre',
                    'apellido': 'Apellido',
                    'correo': 'Correo',
                    'telefono': 'Teléfono',
                    'id_especialidad': 'ID Especialidad',
                    'especialidad': 'Especialidad',
                    'horario': 'Horario'
                })

                st.dataframe(df_mostrar, hide_index=True, width="stretch")

                if filtros_aplicados:
                    st.success(f"{len(df_mostrar)} registro(s) encontrados")
                else:
                    st.info(f"Total: {len(df_mostrar)} registro(s)")
            else:
                st.warning("No hay médicos registrados.")



    # Tab Crear
    with tab_crear:
        st.subheader("Crear Médico")
        
        # Reset controlado del formulario
        if st.session_state.get("med_reset_form", False):
            st.session_state["med_crear_rut"] = ""
            st.session_state["med_crear_nom"] = ""
            st.session_state["med_crear_ape"] = ""
            st.session_state["med_crear_correo"] = ""
            st.session_state["med_crear_tel"] = ""
            st.session_state["med_crear_esp"] = 1
            st.session_state["med_crear_hor"] = ""  # Resetear horario
            st.session_state["med_reset_form"] = False

        col1, col2, col3 = st.columns(3)

        with col1:
            rut = st.text_input(
                "RUT",
                key="med_crear_rut",
                placeholder="Ej: 12.345.678-9"
            )
            nombre = st.text_input("Nombre", key="med_crear_nom", placeholder="Ej: Alberto")
            apellido = st.text_input("Apellido", key="med_crear_ape", placeholder="Ej: Marín")

        with col2:
            correo = st.text_input("Correo", key="med_crear_correo", placeholder="Ej: alberto.marin@hospital.cl")
            telefono = st.text_input("Teléfono", key="med_crear_tel", placeholder="Ej: +56912345678")

        with col3:
            id_esp = st.number_input(
                "ID Especialidad",
                min_value=1,
                step=1,
                key="med_crear_esp"
            )
            horario = st.text_input("Horario de atención", key="med_crear_hor", placeholder="Ej: Lunes-Viernes 9:00-13:00")

        if st.button("Agregar Médico", key="med_crear_btn", type="primary"):
            # Validar que la especialidad exista primero
            from modulos.db.db import existe_tabla_id
            if not existe_tabla_id("especialidad", id_esp):
                st.error(f"No existe una especialidad con ID {id_esp}. Por favor, verifique el ID.")
                return
                
            if not rut or not rut.strip():
                st.error("El RUT es obligatorio.")
            elif not validar_rut(rut):
                st.error("RUT inválido. Formato esperado: 12.345.678-9")
            elif not nombre or not nombre.strip():
                st.error("El nombre es obligatorio.")
            elif not apellido or not apellido.strip():
                st.error("El apellido es obligatorio.")
            elif not correo or not correo.strip():
                st.error("El correo es obligatorio.")
            elif not validar_email(correo):
                st.error("Correo inválido. Ejemplo válido: usuario@dominio.cl")
            elif not telefono or not telefono.strip():
                st.error("El teléfono es obligatorio.")
            elif not validar_telefono(telefono):
                st.error("Teléfono inválido. Usa solo dígitos o formato +56...")
            else:
                with st.spinner("Creando médico..."):
                    rut_formateado = formatear_rut(rut)
                    ok, msg = crear_medico(
                        rut=rut_formateado,
                        nombre=nombre.strip(),
                        apellido=apellido.strip(),
                        correo=correo.strip(),
                        telefono=telefono.strip(),
                        id_especialidad=id_esp,
                        horario=horario.strip()  # Pasar el horario al crear médico
                    )
                    if ok:
                        st.success(msg)
                        # Limpiar formulario y activar refresco de lista
                        st.session_state["med_reset_form"] = True
                        st.session_state["med_refresh_list"] = True
                        st.rerun()
                    else:
                        st.error(msg)
                        # Mostrar más detalles del error en un expander
                        with st.expander("Detalles del error"):
                            st.write("Datos que se intentaron insertar:")
                            st.json({
                                "rut": rut_formateado,
                                "nombre": nombre.strip(),
                                "apellido": apellido.strip(),
                                "correo": correo.strip(),
                                "telefono": telefono.strip(),
                                "id_especialidad": id_esp,
                                "horario": horario.strip()  # Mostrar el horario también en el error
                            })


    # Tab Actualizar
    with tab_actualizar:
        st.subheader("Actualizar Médico")
        
        data = mostrar_medicos()
        if data:
            df = pd.DataFrame(data)
            cols_lower = []
            for c in df.columns:
                cols_lower.append(c.lower())
            df.columns = cols_lower
            
            # Filtro por ID
            filtro_id = st.number_input(
                "Filtrar / Seleccionar ID a modificar (0 para mostrar todos)",
                min_value=0,
                value=0,
                key="med_upd_filtro"
            )
            
            if filtro_id > 0:
                df_filtrado = df[df["id"] == filtro_id]
            else:
                df_filtrado = df
            
            # Si existe el ID ingresado
            if filtro_id > 0 and not df_filtrado.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    rut_upd = st.text_input(
                        "RUT",
                        value="",
                        key="med_upd_rut",
                        placeholder="Ej: 12.345.678-9"
                    )
                    nombre_upd = st.text_input(
                        "Nombre",
                        value="",
                        key="med_upd_nom",
                        placeholder="Ej: Alberto"
                    )
                    apellido_upd = st.text_input(
                        "Apellido",
                        value="",
                        key="med_upd_ape",
                        placeholder="Ej: Marín"
                    )

                with col2:
                    correo_upd = st.text_input(
                        "Correo",
                        value="",
                        key="med_upd_cor",
                        placeholder="Ej: alberto.marin@hospital.cl"
                    )
                    telefono_upd = st.text_input(
                        "Teléfono",
                        value="",
                        key="med_upd_tel",
                        placeholder="Ej: +56912345678"
                    )

                with col3:
                    id_esp_upd = st.number_input(
                        "ID Especialidad",
                        value=1,
                        min_value=1,
                        step=1,
                        key="med_upd_esp"
                    )
                    horario_upd = st.text_input(
                        "Horario de atención",
                        value="",
                        key="med_upd_hor",
                        placeholder="Ej: Lunes-Viernes 9:00-13:00"
                    )

                if st.button("Actualizar Médico", key=f"med_upd_btn_{filtro_id}", type="primary"):
                    from modulos.db.db import existe_tabla_id
                    if not rut_upd or not rut_upd.strip():
                        st.error("El RUT es obligatorio.")
                    elif not validar_rut(rut_upd):
                        st.error("RUT inválido. Formato esperado: 12.345.678-9")
                    elif not nombre_upd or not nombre_upd.strip():
                        st.error("El nombre es obligatorio.")
                    elif not apellido_upd or not apellido_upd.strip():
                        st.error("El apellido es obligatorio.")
                    elif not correo_upd or not correo_upd.strip():
                        st.error("El correo es obligatorio.")
                    elif not validar_email(correo_upd):
                        st.error("Correo inválido. Ejemplo válido: usuario@dominio.cl")
                    elif not telefono_upd or not telefono_upd.strip():
                        st.error("El teléfono es obligatorio.")
                    elif not validar_telefono(telefono_upd):
                        st.error("Teléfono inválido. Usa solo dígitos o formato +56...")
                    elif id_esp_upd < 1:
                        st.error("Debe ingresar un ID de especialidad válido (mayor o igual a 1).")
                    elif not existe_tabla_id("especialidad", id_esp_upd):
                        st.error(f"No existe una especialidad con ID {id_esp_upd}. Por favor, verifique el ID.")
                    else:
                        rut_upd_formateado = formatear_rut(rut_upd)
                        ok, msg = actualizar_medico(
                            id_medico=filtro_id,
                            rut=rut_upd_formateado,
                            nombre=nombre_upd,
                            apellido=apellido_upd,
                            correo=correo_upd,
                            telefono=telefono_upd,
                            id_especialidad=id_esp_upd,
                            horario=horario_upd.strip()
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                st.info("Ingrese un ID mayor a 0 para modificar un registro.")

            st.markdown("-----")
            st.markdown("#### Médicos registrados")
            df_mostrar = df_filtrado.rename(columns={
                "id": "ID",
                "rut": "RUT",
                "nombre": "Nombre",
                "apellido": "Apellido",
                "correo": "Correo",
                "telefono": "Teléfono",
                "id_especialidad": "ID Especialidad",
                "especialidad": "Especialidad",
                "horario": "Horario"
            })
            st.dataframe(df_mostrar, hide_index=True, width="stretch")
        else:
            st.info("No hay registros.")


    # Tab Eliminar
    with tab_eliminar:
        data = mostrar_medicos()
        if data:
            df = pd.DataFrame(data)

            # Normalizar columnas
            df.columns = [c.lower() for c in df.columns]

        
            filtro_id = st.number_input(
                "Filtrar / Seleccionar ID para eliminar (0 = mostrar todos)",
                min_value=0,
                value=0,
                key="med_del_filtro"
            )

            # Aplicar filtrado
            if filtro_id > 0:
                df_filtrado = df[df["id"] == filtro_id]
            else:
                df_filtrado = df

        
            if filtro_id > 0:
                if st.button("Eliminar", key=f"med_del_btn_{filtro_id}"):
                    ok, msg = borrar_medico(filtro_id)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.info("Ingresa un ID mayor a 0 para eliminar un registro.")

        
            st.markdown("-----")
            st.markdown("#### Médicos registrados")

            df_mostrar = df_filtrado.rename(columns={
                "id": "ID",
                "rut": "RUT",
                "nombre": "Nombre",
                "apellido": "Apellido",
                "correo": "Correo",
                "telefono": "Teléfono",
                "id_especialidad": "ID Especialidad",
                "horario": "Horario"
            })

            st.dataframe(df_mostrar, hide_index=True, width="stretch")

        else:
            st.info("No hay registros.")



