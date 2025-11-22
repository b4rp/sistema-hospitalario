import streamlit as st
import pandas as pd

def mostrar_resultados(resultados, nombre_tabla=""):
    """
    Muestra resultados en un DataFrame de Streamlit con el ID real como índice.
    Evita confundir el índice de Pandas con el ID de la base de datos.
    """
    if not resultados:
        st.warning(f"No se encontraron resultados en {nombre_tabla}.")
        return

    df = pd.DataFrame(resultados)

    # Asegurarse de que exista columna id
    if "id" in df.columns:
        df = df.sort_values("id").set_index("id")
        st.dataframe(df, width="stretch")
    else:
        # Si no existe 'id', mostramos sin índice y avisamos
        st.dataframe(df, hide_index=True, width="stretch")
        st.info("Esta tabla no contiene columna 'id'.")