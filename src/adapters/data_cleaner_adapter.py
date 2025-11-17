import pandas as pd

from use_cases.ports.data_cleaner import IDataCleaner
from domain.services.text_cleaner import clean_text
from domain.services.comment_filter import filter_irrelevant_comments


class PandasDataCleaner(IDataCleaner):
    """
    Una implementación concreta de IDataCleaner que utiliza pandas y el
    servicio de limpieza de texto del dominio.
    """

    def clean_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia los datos de reseñas en un DataFrame de pandas.
        """
        df = raw_data.copy()

        # Estandarizar nombres de columnas
        df.rename(
            columns={'Calificacion': 'calificacion',
                     'Comentarios': 'comentarios'}, inplace=True)

        # Limpiar calificaciones
        df['calificacion'] = pd.to_numeric(df['calificacion'], errors='coerce')
        df.dropna(subset=['calificacion'], inplace=True)
        df['calificacion'] = df['calificacion'].astype('Int8')

        # Limpiar comentarios usando el servicio de dominio
        df['comentarios'] = df['comentarios'].apply(clean_text)
        df.dropna(subset=['comentarios'], inplace=True)

        # Filtrar comentarios irrelevantes usando el servicio de dominio
        df = filter_irrelevant_comments(df)

        print(f"Limpieza completada. {len(df)} comentarios válidos restantes.")
        return df
