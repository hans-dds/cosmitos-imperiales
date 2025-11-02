import pandas as pd
import io

def generar_excel(df, resumen, distribucion):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        #Escribir hojas
        df.to_excel(writer, index=False, sheet_name='Datos')
        resumen.to_excel(writer, index=False, sheet_name='Resumen')
        distribucion.to_excel(writer, index=False, sheet_name='Distribucion')

        workbook = writer.book
        ws_datos = writer.sheets['Datos']
        ws_resumen = writer.sheets['Resumen']
        ws_dist = writer.sheets['Distribucion']

        #Formato de encabezado
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': "#D5F549",
            'font_color': 'black',
            'align': 'center'
        })
        for col_num, value in enumerate(df.columns.values):
            ws_datos.write(0, col_num, value, header_format)

        #Gráfica 1: Pastel
        chart_pie = workbook.add_chart({'type': 'pie'})
        chart_pie.add_series({
            'name': 'Distribución de comentarios',
            'categories': ['Resumen', 1, 0, len(resumen), 0],
            'values': ['Resumen', 1, 3, len(resumen), 3],
            'data_labels': {'percentage': True}
        })
        chart_pie.set_title({'name': 'Distribución de comentarios (%)'})
        ws_resumen.insert_chart('E2', chart_pie)

        #Gráfica 2: Barras
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

        #Gráfica 3: Quiénes opinan más
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

        #Gráfica 4: Distribución de longitudes
        chart_dist = workbook.add_chart({'type': 'column'})
        categorias = distribucion['Clasificacion'].unique()
        for i, cat in enumerate(categorias):
            chart_dist.add_series({
                'name': cat,
                'categories': ['Distribucion', 1, 1, len(distribucion), 2],
                'values': ['Distribucion', 1, 3 + i, len(distribucion), 3 + i],
            })
        chart_dist.set_title({'name': '¿Quiénes opinan más? (Distribución de longitud)'})
        chart_dist.set_x_axis({'name': 'Número de palabras'})
        chart_dist.set_y_axis({'name': 'Cantidad de comentarios'})
        ws_dist.insert_chart('G2', chart_dist)

    output.seek(0)
    return output.getvalue()
