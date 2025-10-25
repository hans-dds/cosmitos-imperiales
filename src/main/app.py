from presentacion.vista.charts import mostrar_graficos
import streamlit as st
from presentacion.controlador.loader import process_uploaded_file
from presentacion.vista.layout import show_header, show_tables
import presentacion.vista.config_app_ui as cau
from presentacion.vista.layout import upload_file_view
from presentacion.vista.utils import color_discrete_map

cau.config_page()
show_header()

archivo = upload_file_view()
if archivo:
    datos, mensaje, valido = process_uploaded_file(archivo)

    if valido:
        st.sidebar.success(mensaje)

        df = datos
        st.subheader("Vista previa de datos")
        if df is not None and not df.empty:
            st.dataframe(df.head(5), use_container_width=True, hide_index=True)
            st.write("NO SE VEEE")

        elif df is not None and df.empty:
                    st.warning("El archivo se procesó, pero no se encontraron comentarios válidos después de la limpieza.")
        else:
            st.warning("No se pudieron cargar los datos correctamente.")

        mostrar_graficos(df, color_discrete_map)
        show_tables(df)
    else:
        # Si valido es False, 'mensaje' contiene el error
        st.sidebar.error(mensaje)
