import streamlit as st
import pandas as pd
from modulos.db.cita import (
    agregar_cita,
    mostrar_citas,
    eliminar_cita,
    actualizar_cita,
    mostrar_paciente_nombre,
    mostrar_paciente_rut
)
from modulos.db.medico import mostrar_medicos
from modulos.db.paciente import mostrar_pacientes

def mostrar_seccion_citas():
    st.header("Citas")
    # Inicializar claves de session_state necesarias para evitar AttributeError
    if "citas_estados_modificados" not in st.session_state:
        st.session_state.citas_estados_modificados = {}
    if "citas_a_eliminar" not in st.session_state:
        st.session_state.citas_a_eliminar = set()
    tab_gestionar, tab_crear = st.tabs(
        ["🗂️ Gestión Integral", "➕ Nueva Cita"]
    )

    # Tab Gestionar (antes Listar + Actualizar + Eliminar)
    with tab_gestionar:
        st.subheader("Gestión Integral de Citas")
        st.caption("Visualiza, edita estado y elimina citas desde un solo lugar")
        data = mostrar_citas()

        if not data:
            st.info("No hay citas registradas.")
        else:
            # Obtener datos de médicos para mostrar especialidad
            medicos = mostrar_medicos()
            medicos_dict = {m['id']: m for m in medicos}
            
            # Filtros en la parte superior
            st.markdown("#### 🔍 Filtros")
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            with col_f1:
                filtro_id = st.number_input(
                    "ID Cita",
                    min_value=0,
                    step=1,
                    key="cit_filtro_id"
                )
            
            with col_f2:
                filtro_fecha = st.date_input(
                    "Fecha",
                    value=None,
                    key="cit_filtro_fecha"
                )
            
            with col_f3:
                filtro_estado = st.selectbox(
                    "Estado",
                    ["Todos", "PENDIENTE", "REALIZADA", "CANCELADA"],
                    key="cit_filtro_estado"
                )
            
            with col_f4:
                filtro_rut = st.text_input(
                    "RUT Paciente",
                    key="cit_filtro_rut",
                    placeholder="Ej: 12.345.678-9"
                )
            
            st.markdown("---")
            
            # Aplicar filtros
            citas_filtradas = []
            for cita in data:
                # Filtro por ID
                if filtro_id > 0 and cita['id'] != filtro_id:
                    continue
                
                # Filtro por RUT
                if filtro_rut:
                    rut_paciente = mostrar_paciente_rut(cita['id_paciente'])
                    if filtro_rut.lower() not in rut_paciente.lower():
                        continue
                
                # Filtro por fecha
                if filtro_fecha and str(cita['fecha']) != str(filtro_fecha):
                    continue
                
                # Filtro por estado
                if filtro_estado != "Todos" and cita['estado'] != filtro_estado:
                    continue
                
                citas_filtradas.append(cita)
            
            if not citas_filtradas:
                st.warning("No se encontraron citas con los filtros aplicados.")
            else:
                # Botón principal para guardar todos los cambios - ARRIBA
                cambios_pendientes = len(st.session_state.citas_estados_modificados) + len(st.session_state.citas_a_eliminar)
                
                if cambios_pendientes > 0:
                    col_alert, col_btn_save = st.columns([3, 2])
                    
                    with col_alert:
                        st.warning(f"⚠️ Tienes {cambios_pendientes} cambio(s) pendiente(s)")
                    
                    with col_btn_save:
                        if st.button("💾 Guardar Todos los Cambios", type="primary", key="guardar_cambios_top", width="stretch"):
                            errores = []
                            
                            # Actualizar estados modificados
                            for cita_id, nuevo_estado in st.session_state.citas_estados_modificados.items():
                                cita_original = next((c for c in data if c['id'] == cita_id), None)
                                if cita_original:
                                    ok, msg = actualizar_cita(
                                        cita_id,
                                        cita_original['fecha'],
                                        cita_original['hora'],
                                        nuevo_estado,
                                        cita_original['motivo'],
                                        cita_original['id_paciente'],
                                        cita_original['id_medico']
                                    )
                                    if not ok:
                                        errores.append(f"Cita #{cita_id}: {msg}")
                            
                            # Eliminar citas marcadas
                            for cita_id in st.session_state.citas_a_eliminar:
                                ok, msg = eliminar_cita(cita_id)
                                if not ok:
                                    errores.append(f"Cita #{cita_id}: {msg}")
                            
                            # Limpiar session_state y mostrar resultado
                            st.session_state.citas_estados_modificados = {}
                            st.session_state.citas_a_eliminar = set()
                            
                            if errores:
                                st.error("❌ Algunos cambios no se pudieron guardar:")
                                for error in errores:
                                    st.error(f"  • {error}")
                            else:
                                st.success("✅ Todos los cambios guardados correctamente")
                            
                            st.rerun()
                    
                    st.markdown("---")
                
                st.info(f"📋 Mostrando {len(citas_filtradas)} cita(s)")
                
                # Inicializar estados en session_state si no existen
                if "citas_estados_modificados" not in st.session_state:
                    st.session_state.citas_estados_modificados = {}
                if "citas_a_eliminar" not in st.session_state:
                    st.session_state.citas_a_eliminar = set()
                
                # Mostrar cada cita como tarjeta editable
                for cita in citas_filtradas:
                    # Obtener datos del paciente y médico
                    nombre_paciente = mostrar_paciente_nombre(cita['id_paciente'])
                    rut_paciente = mostrar_paciente_rut(cita['id_paciente'])
                    
                    medico_info = medicos_dict.get(cita['id_medico'], {})
                    nombre_medico = f"{medico_info.get('nombre', 'N/A')} {medico_info.get('apellido', '')}"
                    especialidad_medico = medico_info.get('especialidad', 'Sin especialidad')
                    
                    # Verificar si está marcada para eliminar
                    if cita['id'] in st.session_state.citas_a_eliminar:
                        continue
                    
                    # Contenedor de la tarjeta
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([1.2, 1.8, 1.5, 1.2, 1.3])
                        
                        with col1:
                            st.markdown(f"**Cita #{cita['id']}**")
                            st.caption(f"📅 {cita['fecha']}")
                            st.caption(f"🕒 {cita['hora']}")
                        
                        with col2:
                            st.markdown(f"**👤 {nombre_paciente}**")
                            st.code(rut_paciente, language=None)
                            st.caption(f"💬 {cita['motivo']}")
                        
                        with col3:
                            st.markdown(f"**👨‍⚕️ {nombre_medico}**")
                            st.caption(f"🏥 _{especialidad_medico}_")
                        
                        with col4:
                            nuevo_estado = st.selectbox(
                                "Estado",
                                ["PENDIENTE", "REALIZADA", "CANCELADA"],
                                index=["PENDIENTE", "REALIZADA", "CANCELADA"].index(cita["estado"]),
                                key=f"estado_{cita['id']}",
                                label_visibility="visible"
                            )
                            # Guardar el nuevo estado en session_state
                            if nuevo_estado != cita["estado"]:
                                st.session_state.citas_estados_modificados[cita['id']] = nuevo_estado
                            elif cita['id'] in st.session_state.citas_estados_modificados:
                                del st.session_state.citas_estados_modificados[cita['id']]
                        
                        with col5:
                            if st.button("❌ Eliminar", key=f"del_{cita['id']}", width="stretch"):
                                st.session_state.citas_a_eliminar.add(cita['id'])
                                st.rerun()
                        
                        st.markdown("---")
                
                # Mensaje informativo final si hay cambios pendientes
                if cambios_pendientes > 0:
                    st.info("💡 Recuerda guardar los cambios usando el botón de arriba")

    # Tab Crear
    with tab_crear:
        st.subheader("Crear Cita")
        pacientes = mostrar_pacientes()
        medicos = mostrar_medicos()

        if not pacientes:
            st.warning("No hay pacientes registrados.")
        elif not medicos:
            st.warning("No hay médicos registrados.")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                fecha = st.date_input("Fecha", key="cit_crear_fecha")
                hora = st.time_input("Hora", key="cit_crear_hora")

            with col2:
                paciente_dict = {f"{p['nombre']} {p['apellido']}": p["id"] for p in pacientes}
                paciente_sel = st.selectbox("Selecciona Paciente", list(paciente_dict.keys()), key="cit_crear_pac")
                id_pac = paciente_dict[paciente_sel]

                medico_dict = {f"{m['nombre']} {m['apellido']}": m["id"] for m in medicos}
                medico_sel = st.selectbox("Selecciona Médico", list(medico_dict.keys()), key="cit_crear_med")
                id_med = medico_dict[medico_sel]

            with col3:
                motivo = st.text_input("Motivo de la Cita", key="cit_crear_mot", placeholder="Ej: Control preventivo")
                estado = st.selectbox(
                    "Estado",
                    ["PENDIENTE", "REALIZADA", "CANCELADA"],
                    index=0,
                    key="cit_crear_estado"
                )

            if st.button("Agregar Cita", key="cit_crear_btn"):
                if not motivo.strip():
                    st.error("Debe ingresar el motivo de la cita.")
                else:
                    ok, msg = agregar_cita(
                        fecha=fecha,
                        hora=hora,
                        motivo=motivo.strip(),
                        id_paciente=int(id_pac),
                        id_medico=int(id_med),
                        estado=estado
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)