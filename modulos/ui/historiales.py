import streamlit as st
import pandas as pd
from modulos.db.historial import agregar_historial, obtener_historiales
from modulos.db.diagnostico import obtener_diagnosticos
from modulos.db.tratamiento import obtener_tratamientos
from modulos.db.paciente import mostrar_pacientes
from modulos.db.cita import mostrar_citas

def mostrar_seccion_historiales():
    st.header("Historiales")
    tab_listar, tab_crear = st.tabs(["📋 Listar", "➕ Crear"])
    with tab_listar:
        st.subheader("Lista de Historiales")
        datos = obtener_historiales()
        if not datos:
            st.info("No hay historiales registrados.")
        else:
            df = pd.DataFrame(datos)
            # Columnas según SELECT en obtener_historiales
            df.columns = [
                "ID",
                "Fecha Registro",
                "Paciente",
                "Diagnóstico",
                "Tratamiento",
                "Observaciones",
                "Alergias",
                "Resultado Examen",
            ]

            # Filtros
            st.markdown("### 🔍 Filtros")
            col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
            with col_f1:
                q = st.text_input(
                    "Buscar",
                    key="hist_list_q",
                    placeholder="Ej: Paciente, Diagnóstico o Tratamiento"
                )
            with col_f2:
                desde = st.date_input("Desde", value=None, key="hist_list_desde")
            with col_f3:
                hasta = st.date_input("Hasta", value=None, key="hist_list_hasta")

            df_filtrado = df.copy()
            if q:
                qn = q.strip().lower()
                df_filtrado = df_filtrado[
                    df_filtrado["Paciente"].astype(str).str.lower().str.contains(qn)
                    | df_filtrado["Diagnóstico"].astype(str).str.lower().str.contains(qn)
                    | df_filtrado["Tratamiento"].astype(str).str.lower().str.contains(qn)
                ]

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
        st.subheader("Crear Historial")
        fecha_reg = st.date_input("Fecha registro")
        # Seleccionar diagnóstico
        diag_rows = obtener_diagnosticos()
        diag_options = []
        if diag_rows:
            for d in diag_rows:
                diag_options.append((d[0], f"ID {d[0]} - {d[1]}"))
        if diag_options:
            diag_labels = []
            for o in diag_options:
                diag_labels.append(o[1])
            diag_map = {}
            for opt in diag_options:
                diag_map[opt[1]] = opt[0]
            diag_sel = st.selectbox("Diagnóstico", diag_labels)
            id_diag = diag_map[diag_sel]
        else:
            st.warning("No hay diagnósticos disponibles.")
            id_diag = None

        # Seleccionar tratamiento
        trat_rows = obtener_tratamientos()
        trat_options = []
        if trat_rows:
            for t in trat_rows:
                trat_options.append((t[0], f"ID {t[0]} - {t[1]}"))
        if trat_options:
            trat_labels = []
            for o in trat_options:
                trat_labels.append(o[1])
            trat_map = {}
            for opt in trat_options:
                trat_map[opt[1]] = opt[0]
            trat_sel = st.selectbox("Tratamiento", trat_labels)
            id_trat = trat_map[trat_sel]
        else:
            st.warning("No hay tratamientos disponibles.")
            id_trat = None

        obs = st.text_area("Observaciones", placeholder="Ej: Paciente estable, buena respuesta al tratamiento")
        alergias = st.text_input("Alergias", placeholder="Ej: Penicilina, Polen")
        resultado_ex = st.text_area("Resultado examen", placeholder="Ej: Exámenes dentro de parámetros normales")

        # Paciente
        pac_rows = mostrar_pacientes()
        pac_map = {}
        if pac_rows:
            for p in pac_rows:
                nombre = p.get('nombre', '')
                apellido = p.get('apellido', '')
                clave = f"{p['id']} - {nombre} {apellido}"
                pac_map[clave] = p['id']
        if pac_map:
            pac_labels = list(pac_map.keys())
            pac_sel = st.selectbox("Paciente", pac_labels)
            id_pac = pac_map[pac_sel]
        else:
            st.warning("No hay pacientes registrados.")
            id_pac = None

        # Cita
        cita_rows = mostrar_citas()
        cita_map = {}
        if cita_rows:
            for c in cita_rows:
                clave = f"{c['id']} - {c.get('fecha')} {c.get('hora')}"
                cita_map[clave] = c['id']
        if cita_map:
            cita_labels = list(cita_map.keys())
            cita_sel = st.selectbox("Cita", cita_labels)
            id_cita = cita_map[cita_sel]
        else:
            st.warning("No hay citas registradas.")
            id_cita = None

        if st.button("Agregar Historial"):
            if not id_diag or not id_trat or not id_pac or not id_cita:
                st.error("Seleccione diagnóstico, tratamiento, paciente y cita válidos.")
            else:
                agregar_historial(str(fecha_reg), id_diag, id_trat, obs.strip(), alergias.strip(), resultado_ex.strip(), id_pac, id_cita)
                st.success("Historial agregado correctamente.")
                st.rerun()
