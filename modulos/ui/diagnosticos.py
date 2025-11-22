import streamlit as st
import pandas as pd
from modulos.db.diagnostico import agregar_diagnostico, obtener_diagnosticos
from modulos.db.medico import mostrar_medicos
from modulos.db.cita import mostrar_citas

def mostrar_seccion_diagnosticos():
    st.header("Diagnósticos")
    tab_listar, tab_crear = st.tabs(["📋 Listar", "➕ Crear"])

    with tab_listar:
        st.subheader("Lista de Diagnósticos")
        datos = obtener_diagnosticos()
        if not datos:
            st.info("No hay diagnósticos registrados.")
        else:
            df = pd.DataFrame(datos)
            # Columnas según SELECT en obtener_diagnosticos
            df.columns = [
                "ID",
                "Fecha",
                "Descripción",
                "Médico",
                "Fecha Cita",
                "Motivo Cita",
            ]

            # Filtros
            st.markdown("### 🔍 Filtros")
            col_f1, col_f2, col_f3 = st.columns([3, 2, 2])
            with col_f1:
                q = st.text_input(
                    "Buscar",
                    key="diag_list_q",
                    placeholder="Ej: Hipertensión, Diabetes, Gripe"
                )
            with col_f2:
                med_values = []
                for x in df["Médico"].dropna().unique().tolist():
                    med_values.append(x)
                med_values = sorted(med_values)
                med_opts = ["Todos"]
                for v in med_values:
                    med_opts.append(v)
                filtro_med = st.selectbox("Médico", med_opts, key="diag_list_med")
            with col_f3:
                desde = st.date_input("Desde", value=None, key="diag_list_desde")
                hasta = st.date_input("Hasta", value=None, key="diag_list_hasta")

            df_filtrado = df.copy()
            if q:
                qn = q.strip().lower()
                df_filtrado = df_filtrado[
                    df_filtrado["Descripción"].astype(str).str.lower().str.contains(qn)
                    | df_filtrado["Médico"].astype(str).str.lower().str.contains(qn)
                    | df_filtrado["Motivo Cita"].astype(str).str.lower().str.contains(qn)
                ]

            if filtro_med != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Médico"] == filtro_med]

            if desde or hasta:
                def _to_date(s):
                    try:
                        return pd.to_datetime(s).date()
                    except Exception:
                        return None
                f_list = []
                for val in df_filtrado["Fecha"]:
                    f_list.append(_to_date(val))
                mask_list = []
                for d in f_list:
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
        st.subheader("Crear Diagnóstico")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            fecha = st.date_input("Fecha")
            
            # Seleccionar médico
            med_rows = mostrar_medicos()
            med_options = []
            if med_rows:
                for m in med_rows:
                    etiqueta = f"{m.get('nombre','')} {m.get('apellido','')}"
                    med_options.append((m['id'], etiqueta))
            med_map = {}
            for opt in med_options:
                med_map[opt[1]] = opt[0]
            if med_options:
                med_labels = []
                for m in med_options:
                    med_labels.append(m[1])
                med_sel_label = st.selectbox("Médico", med_labels)
                id_medico = med_map[med_sel_label]
            else:
                st.warning("No hay médicos registrados. Agrega médicos primero.")
                id_medico = None
        
        with col2:
            # Seleccionar cita
            cita_rows = mostrar_citas()
            cita_options = []
            if cita_rows:
                for c in cita_rows:
                    etiqueta = f"ID {c.get('id')} - {c.get('fecha')} {c.get('hora')}"
                    cita_options.append((c['id'], etiqueta))
            cita_map = {}
            for opt in cita_options:
                cita_map[opt[1]] = opt[0]
            if cita_options:
                cita_labels = []
                for c in cita_options:
                    cita_labels.append(c[1])
                cita_sel_label = st.selectbox("Cita", cita_labels)
                id_cita = cita_map[cita_sel_label]
            else:
                st.warning("No hay citas registradas. Agrega citas primero.")
                id_cita = None
        
        descripcion = st.text_area("Descripción", height=120, placeholder="Ej: Hipertensión arterial grado 2, requiere tratamiento farmacológico")

        if st.button("Agregar Diagnóstico", type="primary"):
            if not descripcion.strip():
                st.error("La descripción es obligatoria.")
            elif id_medico is None or id_cita is None:
                st.error("Seleccione médico y cita válidos.")
            else:
                ok = agregar_diagnostico(str(fecha), descripcion.strip(), id_medico, id_cita)
                if ok:
                    st.success("Diagnóstico agregado correctamente.")
                    st.rerun()
                else:
                    st.error("Error al agregar diagnóstico. Verifique que médico y cita existen.")
