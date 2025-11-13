import io
import pandas as pd


def generate_excel_export(df):
    """Genera un archivo Excel a partir del DataFrame y devuelve sus bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DatosCompletos')

        # Añadir una hoja de resumen
        summary = df.groupby('Clasificacion').agg(
            NumComentarios=('comentarios', 'count'),
            LongitudPromedio=('longitud', 'mean')
        ).reset_index()
        summary.to_excel(writer, index=False, sheet_name='Resumen')

        # Añadir gráficos a la hoja de resumen
        workbook = writer.book
        ws_summary = writer.sheets['Resumen']

        chart_pie = workbook.add_chart({'type': 'pie'})
        chart_pie.add_series({
            'name': 'Distribución',
            'categories': ['Resumen', 1, 0, len(summary), 0],
            'values': ['Resumen', 1, 1, len(summary), 1],
        })
        ws_summary.insert_chart('E2', chart_pie)

    output.seek(0)
    return output.getvalue()
