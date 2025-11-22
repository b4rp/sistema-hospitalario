import streamlit as st
import pandas as pd
from modulos.db.atencion import agregar_atencion, obtener_atenciones
from modulos.db.diagnostico import obtener_diagnosticos
from modulos.db.historial import obtener_historiales

def mostrar_seccion_atenciones():
    st.header("Atenciones")
    tab_listar, tab_crear = st.tabs(["📋 Listar", "➕ Crear"])

    with tab_listar:
        st.subheader("Lista de Atenciones")
        datos = obtener_atenciones()
        if not datos:
            st.info("No hay atenciones registradas.")
        else:
            df = pd.DataFrame(datos)
            # Columnas según SELECT en obtener_atenciones
            df.columns = [
                "ID",
                "Descripción",
                "Diagnóstico",
                "Historial",
                "Fecha Registro",
            ]

            # Filtros
            st.markdown("### 🔍 Filtros")
            col_f1, col_f2, col_f3 = st.columns([3, 2, 2])
            with col_f1:
                q = st.text_input(
                    "Buscar",
                    key="aten_list_q",
                    placeholder="Ej: seguimiento, control, evaluación"
                )
            with col_f2:
                diag_values = []
                for x in df["Diagnóstico"].dropna().unique().tolist():
                    diag_values.append(x)
                diag_values = sorted(diag_values)
                diag_opts = ["Todos"]
                for v in diag_values:
                    diag_opts.append(v)
                filtro_diag = st.selectbox("Diagnóstico", diag_opts, key="aten_list_diag")
            with col_f3:
                desde = st.date_input("Desde", value=None, key="aten_list_desde")
                hasta = st.date_input("Hasta", value=None, key="aten_list_hasta")

            df_filtrado = df.copy()
            if q:
                qn = q.strip().lower()
                mask_list = []
                for idx in range(len(df_filtrado)):
                    desc_val = str(df_filtrado.iloc[idx]["Descripción"]).lower()
                    diag_val = str(df_filtrado.iloc[idx]["Diagnóstico"]).lower()
                    ok = False
                    if qn in desc_val:
                        ok = True
                    if qn in diag_val:
                        ok = True
                    mask_list.append(ok)
                df_filtrado = df_filtrado[pd.Series(mask_list)]

            if filtro_diag != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Diagnóstico"] == filtro_diag]

            if desde or hasta:
                def _to_date(s):
                    try:
                        return pd.to_datetime(s).date()
                    except Exception:
                        return None
                fr_list = []
                for val in df_filtrado["Fecha Registro"]:
                    fr_list.append(_to_date(val))
                mask_list = []
                for d in fr_list:
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
        st.subheader("Crear Atención")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            diag_rows = obtener_diagnosticos()
            diag_opts = []
            if diag_rows:
                for d in diag_rows:
                    etiqueta = f"ID {d[0]} - {d[1]}"
                    diag_opts.append((d[0], etiqueta))
            if diag_opts:
                diag_map = {}
                for o in diag_opts:
                    diag_map[o[1]] = o[0]
                diag_labels = []
                for o in diag_opts:
                    diag_labels.append(o[1])
                diag_sel = st.selectbox("Diagnóstico", diag_labels)
                id_diag = diag_map[diag_sel]
            else:
                st.warning("No hay diagnósticos. Agrega diagnósticos primero.")
                id_diag = None
        
        with col2:
            hist_rows = obtener_historiales()
            hist_opts = []
            if hist_rows:
                for h in hist_rows:
                    etiqueta = f"ID {h[0]} - {h[2]}"
                    hist_opts.append((h[0], etiqueta))
            if hist_opts:
                hist_map = {}
                for o in hist_opts:
                    hist_map[o[1]] = o[0]
                hist_labels = []
                for o in hist_opts:
                    hist_labels.append(o[1])
                hist_sel = st.selectbox("Historial", hist_labels)
                id_hist = hist_map[hist_sel]
            else:
                st.warning("No hay historiales. Agrega historiales primero.")
                id_hist = None
        
        descripcion = st.text_area("Descripción de la atención", height=120, placeholder="Ej: Atención de seguimiento post-tratamiento, paciente presenta mejoría")

        if st.button("Agregar Atención", type="primary"):
            if not id_diag or not id_hist:
                st.error("Seleccione diagnóstico e historial válidos.")
            elif not descripcion.strip():
                st.error("La descripción es obligatoria.")
            else:
                agregar_atencion(id_diag, id_hist, descripcion.strip())
                st.success("Atención agregada correctamente.")
                st.rerun()
