import io
import pandas as pd


def _generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un DataFrame de resumen agrupado por clasificación.
    
    Args:
        df: DataFrame con las columnas 'Clasificacion', 'comentarios' y opcionalmente 'longitud'
        
    Returns:
        DataFrame con el resumen por clasificación
    """
    # Asegurar que existe la columna 'longitud' para el cálculo
    if 'longitud' not in df.columns and 'comentarios' in df.columns:
        df = df.copy()
        df['longitud'] = df['comentarios'].str.len()
    
    # Crear el resumen con las columnas necesarias en el orden correcto
    # Orden: Clasificacion, NumComentarios, LongitudPromedio, Porcentaje
    summary = df.groupby('Clasificacion').agg(
        NumComentarios=('comentarios', 'count'),
        LongitudPromedio=('longitud', 'mean') if 'longitud' in df.columns else ('comentarios', lambda x: x.str.len().mean()),
        Porcentaje=('comentarios', lambda x: (len(x) / len(df)) * 100)
    ).reset_index()
    
    # Asegurar el orden correcto de las columnas
    summary = summary[['Clasificacion', 'NumComentarios', 'LongitudPromedio', 'Porcentaje']]
    
    # Redondear valores numéricos
    if 'LongitudPromedio' in summary.columns:
        summary['LongitudPromedio'] = summary['LongitudPromedio'].round(2)
    if 'Porcentaje' in summary.columns:
        summary['Porcentaje'] = summary['Porcentaje'].round(2)
    
    return summary


def generate_excel_export(df: pd.DataFrame, resumen: pd.DataFrame = None, distribucion=None):
    """
    Genera un archivo Excel a partir del DataFrame con formato mejorado y gráficas.
    
    Args:
        df: DataFrame con los datos completos (debe incluir 'calificacion', 'comentarios', 'Clasificacion')
        resumen: DataFrame opcional con el resumen. Si no se proporciona, se genera automáticamente.
        distribucion: Parámetro reservado para futuras funcionalidades (no se usa actualmente)
        
    Returns:
        bytes del archivo Excel generado
    """
    output = io.BytesIO()
    
    # Generar resumen si no se proporciona
    if resumen is None:
        resumen = _generate_summary(df)
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir hojas
        # Filtrar solo las columnas requeridas para la hoja de datos
        columns_to_export = ['calificacion', 'comentarios', 'Clasificacion']
        df_export = df[[col for col in columns_to_export if col in df.columns]].copy()
        
        df_export.to_excel(writer, index=False, sheet_name='Datos')
        resumen.to_excel(writer, index=False, sheet_name='Resumen')

        workbook = writer.book
        ws_datos = writer.sheets['Datos']
        ws_resumen = writer.sheets['Resumen']

        # Formato de encabezado
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': "#D5F549",
            'font_color': 'black',
            'align': 'center'
        })

        # Aplicar formato a los encabezados de la hoja de datos
        for col_num, value in enumerate(df_export.columns.values):
            ws_datos.write(0, col_num, value, header_format)
        
        # Aplicar formato a los encabezados de la hoja de resumen
        for col_num, value in enumerate(resumen.columns.values):
            ws_resumen.write(0, col_num, value, header_format)

        # Gráfica 1: Anillo (Doughnut) - Distribución de comentarios por porcentaje
        chart_ring = workbook.add_chart({'type': 'doughnut'})
        chart_ring.add_series({
            'name': 'Distribución de comentarios',
            'categories': ['Resumen', 1, 0, len(resumen), 0],
            'values': ['Resumen', 1, 3, len(resumen), 3] if 'Porcentaje' in resumen.columns else ['Resumen', 1, 1, len(resumen), 1],
            'data_labels': {'percentage': True}
        })
        chart_ring.set_title({'name': 'Distribución de comentarios (%)'})
        ws_resumen.insert_chart('E2', chart_ring)

        # Gráfica 2: Barras - Número de comentarios por categoría
        chart_bar = workbook.add_chart({'type': 'column'})
        chart_bar.add_series({
            'name': 'Número de comentarios',
            'categories': ['Resumen', 1, 0, len(resumen), 0],
            'values': ['Resumen', 1, 1, len(resumen), 1],
            'data_labels': {'value': True}
        })
        chart_bar.set_title({'name': 'Comentarios por categoría'})
        chart_bar.set_x_axis({'name': 'Clasificación'})
        chart_bar.set_y_axis({'name': 'Número de comentarios'})
        ws_resumen.insert_chart('E20', chart_bar)

        # Gráfica 3: Quiénes opinan más - Longitud promedio de comentarios
        if 'LongitudPromedio' in resumen.columns:
            chart_bar2 = workbook.add_chart({'type': 'column'})
            chart_bar2.add_series({
                'name': 'Longitud promedio de comentarios',
                'categories': ['Resumen', 1, 0, len(resumen), 0],
                'values': ['Resumen', 1, 2, len(resumen), 2],
                'data_labels': {'value': True}
            })
            chart_bar2.set_title({'name': '¿Quiénes opinan más? (longitud promedio)'})
            chart_bar2.set_x_axis({'name': 'Clasificación'})
            chart_bar2.set_y_axis({'name': 'Longitud promedio'})
            ws_resumen.insert_chart('E38', chart_bar2)

    output.seek(0)
    return output.getvalue()
