import streamlit as st
import pandas as pd
import unicodedata
from modulos.db.especialidad import (
    mostrar_especialidades,
    agregar_especialidad,
    actualizar_especialidad,
    eliminar_especialidad
)

def normalizar_texto(texto):
    """Elimina tildes y acentos de un texto para comparación."""
    if pd.isna(texto):
        return ""
    texto = str(texto)
    # Normalizar a NFD (descompone caracteres acentuados)
    nfd = unicodedata.normalize('NFD', texto)
    # Filtrar solo caracteres que no sean marcas diacríticas
    sin_tildes = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return sin_tildes.lower()

def mostrar_seccion_especialidades():
    """Interfaz Streamlit para gestionar las especialidades médicas."""

    st.header("Especialidades")
    tab_listar, tab_crear, tab_actualizar, tab_eliminar = st.tabs(
        ["📋 Listar", "➕ Crear", "🔄 Actualizar", "❌ Eliminar"]
    )

    #Listar
    with tab_listar:
        st.subheader("Lista de Especialidades")

        # Si se acaba de crear o eliminar, limpiar filtro ID
        if st.session_state.get("esp_reset_lista", False):
            st.session_state["esp_list_filtro_id"] = 0
            st.session_state["esp_reset_lista"] = False

        # Filtros (ID + búsqueda por nombre/descr.)
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            # Inicializar el valor en session_state solo si no existe
            if "esp_list_filtro_id" not in st.session_state:
                st.session_state["esp_list_filtro_id"] = 0
                
            filtro_id = st.number_input(
                "Buscar por ID de Especialidad",
                min_value=0,  # 0 significa sin filtro
                step=1,
                key="esp_list_filtro_id"
            )
        with col2:
            filtro_nombre = st.text_input(
                "Nombre contiene", 
                key="esp_list_filtro_nombre", 
                placeholder="Ej: Cardiología"
            )
        with col3:
            filtro_desc = st.text_input(
                "Descripción contiene", 
                key="esp_list_filtro_desc", 
                placeholder="Ej: estudio del corazón"
            )

        # Obtener datos
        data = mostrar_especialidades()

        if not data:
            st.warning("No hay especialidades registradas.")
        else:
            df = pd.DataFrame(data)
            cols_lower = []
            for c in df.columns:
                cols_lower.append(c.lower())
            df.columns = cols_lower

            # Crear columnas normalizadas para búsqueda
            df['nombre_normalizado'] = df['nombre'].apply(normalizar_texto)
            df['descripcion_normalizada'] = df['descripcion'].apply(normalizar_texto)

            if filtro_id > 0:
                id_col = 'id' if 'id' in df.columns else 'id_especialidad'
                df = df[df[id_col] == filtro_id]
            
            # Filtros por texto (ignorando tildes)
            if filtro_nombre and filtro_nombre.strip():
                filtro_nombre_norm = normalizar_texto(filtro_nombre)
                df = df[df["nombre_normalizado"].str.contains(filtro_nombre_norm, na=False)]
            
            if filtro_desc and filtro_desc.strip():
                filtro_desc_norm = normalizar_texto(filtro_desc)
                df = df[df["descripcion_normalizada"].str.contains(filtro_desc_norm, na=False)]

            if not df.empty:
                id_col = 'id' if 'id' in df.columns else 'id_especialidad'
                # Eliminar columnas normalizadas antes de mostrar
                df_mostrar = df.drop(columns=['nombre_normalizado', 'descripcion_normalizada'], errors='ignore')
                df_mostrar = df_mostrar.rename(columns={
                    id_col: "ID",
                    "nombre": "Nombre",
                    "descripcion": "Descripción"
                })
                st.dataframe(df_mostrar, hide_index=True, width="stretch")
                st.info(f"Total: {len(df)} registro(s)")
            else:
                st.warning("No se encontraron resultados con los filtros aplicados.")

    #crear
    with tab_crear:
        st.subheader("Crear Especialidad")

        # Reset controlado del formulario
        if st.session_state.get("esp_reset_form", False):
            st.session_state["esp_crear_nom"] = ""
            st.session_state["esp_crear_desc"] = ""
            st.session_state["esp_reset_form"] = False

        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", key="esp_crear_nom", placeholder="Ej: Cardiología")
        with col2:
            descripcion = st.text_area("Descripción", key="esp_crear_desc", height=50, placeholder="Ej: Especialidad médica dedicada al estudio del corazón y sistema cardiovascular")

        if st.button("Agregar Especialidad", key="esp_crear_btn"):
            if not nombre or not nombre.strip():
                st.warning("El nombre es obligatorio.")
            elif not descripcion or not descripcion.strip():
                st.warning("La descripción es obligatoria.")
            else:
                ok, msg = agregar_especialidad(nombre, descripcion)
                if ok:
                    st.success(msg)
                    # Limpiar formulario y resetear filtro de lista
                    st.session_state["esp_reset_form"] = True
                    st.session_state["esp_reset_lista"] = True
                    st.rerun()
                else:
                    st.error(msg)

    #actualizar
    with tab_actualizar:
        st.subheader("Actualizar Especialidad")

        # Reset controlado
        if st.session_state.get("esp_reset_form_upd", False):
            st.session_state["esp_upd_nom"] = ""
            st.session_state["esp_upd_desc"] = ""
            st.session_state["esp_reset_form_upd"] = False

        data = mostrar_especialidades()
        if not data:
            st.warning("No hay especialidades registradas.")
        else:
            df = pd.DataFrame(data)

            df.columns = [c.lower() for c in df.columns]
            id_col = 'id' if 'id' in df.columns else 'id_especialidad'

            # Filtro por ID
            filtro_id = st.number_input(
                "Filtrar / Seleccionar ID a modificar (0 para mostrar todos)",
                min_value=0,
                value=0,
                key="esp_upd_filtro"
            )

            if filtro_id > 0:
                df_filtrado = df[df[id_col] == filtro_id]
            else:
                df_filtrado = df

            # Si existe el ID ingresado
            if filtro_id > 0 and not df_filtrado.empty:

            
                nuevo_nombre = st.text_input(
                    "Nuevo nombre",
                    value="",
                    key="esp_upd_nom",
                    placeholder="Ingrese el nuevo nombre"
                )

                nueva_desc = st.text_area(
                    "Nueva descripción",
                    value="",
                    key="esp_upd_desc",
                    placeholder="Ingrese la nueva descripción"
                )

                if st.button("Actualizar Especialidad", key=f"esp_upd_btn_{filtro_id}", type="primary"):
                    if not nuevo_nombre.strip():
                        st.warning("El nombre es obligatorio.")
                    elif not nueva_desc.strip():
                        st.warning("La descripción es obligatoria.")
                    else:
                        ok, msg = actualizar_especialidad(filtro_id, nuevo_nombre, nueva_desc)
                        if ok:
                            st.success(msg)
                            st.session_state["esp_reset_form_upd"] = True
                            st.rerun()
                        else:
                            st.error(msg)

            else:
                st.info("Ingrese un ID mayor a 0 para modificar un registro.")

            # Mostrar tabla filtrada
            st.markdown("-----")
            st.markdown("#### Especialidades registradas")

            df_mostrar = df_filtrado.rename(columns={
                id_col: "ID",
                "nombre": "Nombre",
                "descripcion": "Descripción"
            })
            st.dataframe(df_mostrar, hide_index=True, width="stretch")




    #Eliminar
    with tab_eliminar:
        st.markdown("### Eliminar Especialidad")
        data = mostrar_especialidades()

        if data:
            df = pd.DataFrame(data)

            df.columns = [c.lower() for c in df.columns]
            id_col = 'id' if 'id' in df.columns else 'id_especialidad'

            # Filtro
            filtro_id = st.number_input(
                "Filtrar / Seleccionar ID a eliminar (0 para mostrar todos)",
                min_value=0,
                value=0,
                key="esp_del_filtro"
            )

            if filtro_id > 0:
                df_filtrado = df[df[id_col] == filtro_id]
            else:
                df_filtrado = df

            # Eliminar usando filtro_id
            if filtro_id > 0:
                if st.button("Eliminar", key=f"esp_del_btn_{filtro_id}"):
                    ok, msg = eliminar_especialidad(filtro_id)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.info("Ingrese un ID mayor a 0 para eliminar un registro.")

            st.markdown("-----")
            st.markdown("#### Especialidades registradas")

            df_mostrar = df_filtrado.rename(columns={
                id_col: "ID",
                "nombre": "Nombre",
                "descripcion": "Descripción"
            })
            st.dataframe(df_mostrar, hide_index=True, width="stretch")

        else:
            st.info("No hay registros.")


