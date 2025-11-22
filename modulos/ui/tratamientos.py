import streamlit as st
import pandas as pd
from modulos.db.tratamiento import agregar_tratamiento, obtener_tratamientos
from modulos.db.diagnostico import obtener_diagnosticos

def mostrar_seccion_tratamientos():
    st.header("Tratamientos")
    tab_listar, tab_crear = st.tabs(["📋 Listar", "➕ Crear"])
    with tab_listar:
        st.subheader("Lista de Tratamientos")
        datos = obtener_tratamientos()
        if not datos:
            st.info("No hay tratamientos registrados.")
        else:
            df = pd.DataFrame(datos)
            # Asignar nombres de columnas coherentes con el SELECT en obtener_tratamientos
            df.columns = [
                "ID",
                "Tratamiento",
                "Fecha Inicio",
                "Fecha Término",
                "Diagnóstico",
            ]

            # Filtros sencillos
            st.markdown("### 🔍 Filtros")
            col_f1, col_f2, col_f3 = st.columns([3, 2, 2])
            with col_f1:
                q = st.text_input(
                    "Buscar",
                    key="trat_list_q",
                    placeholder="Tratamiento o Diagnóstico"
                )
            with col_f2:
                valores_diag = []
                for x in df["Diagnóstico"].dropna().unique().tolist():
                    valores_diag.append(x)
                valores_diag = sorted(valores_diag)
                diag_opts = ["Todos"]
                for v in valores_diag:
                    diag_opts.append(v)
                filtro_diag = st.selectbox("Diagnóstico", diag_opts, key="trat_list_diag")
            with col_f3:
                desde = st.date_input("Desde (inicio)", value=None, key="trat_list_desde")
                hasta = st.date_input("Hasta (inicio)", value=None, key="trat_list_hasta")

            df_filtrado = df.copy()

            if q:
                qn = q.strip().lower()
                df_filtrado = df_filtrado[
                    df_filtrado["Tratamiento"].astype(str).str.lower().str.contains(qn)
                    | df_filtrado["Diagnóstico"].astype(str).str.lower().str.contains(qn)
                ]

            if filtro_diag != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Diagnóstico"] == filtro_diag]

            # Filtro por rango de fechas (Fecha Inicio)
            if desde or hasta:
                def _to_date(s):
                    try:
                        return pd.to_datetime(s).date()
                    except Exception:
                        return None
                fi_list = []
                for val in df_filtrado["Fecha Inicio"]:
                    fi_list.append(_to_date(val))
                mask_list = []
                for d in fi_list:
                    ok = True
                    if desde:
                        if d is None or d < desde:
                            ok = False
                    if hasta:
                        if d is None or d > hasta:
                            ok = False
                    mask_list.append(ok)
                df_filtrado = df_filtrado[pd.Series(mask_list)]

            st.info(f"Total: {len(df_filtrado)} registro(s)")
            st.dataframe(df_filtrado, hide_index=True, width="stretch")

    with tab_crear:
        st.subheader("Crear Tratamiento")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            fecha_inicio = st.date_input("Fecha inicio")
            fecha_termino = st.date_input("Fecha término")
        
        with col2:
            diag_rows = obtener_diagnosticos()
            diag_options = []
            if diag_rows:
                for d in diag_rows:
                    diag_options.append((d[0], f"ID {d[0]} - {d[1]}"))

            if diag_options:
                opciones_labels = []
                for o in diag_options:
                    opciones_labels.append(o[1])

                diag_map = {}
                for opt in diag_options:
                    diag_map[opt[1]] = opt[0]

                diag_sel = st.selectbox("Diagnóstico", opciones_labels)
                id_diag = diag_map[diag_sel]
            else:
                st.warning("No hay diagnósticos. Agrega diagnósticos primero.")
                id_diag = None
        
        tratamiento_txt = st.text_area("Tratamiento", height=120, placeholder="Ej: Enalapril 10mg c/12h + dieta hiposódica, controles mensuales")

        if st.button("Agregar Tratamiento", type="primary"):
            if not tratamiento_txt.strip():
                st.error("El tratamiento es obligatorio.")
            elif id_diag is None:
                st.error("Seleccione un diagnóstico válido.")
            else:
                agregar_tratamiento(str(fecha_inicio), str(fecha_termino), tratamiento_txt.strip(), id_diag)
                st.success("Tratamiento agregado correctamente.")
                st.rerun()
