import pandas as pd

from use_cases.ports.data_cleaner import IDataCleaner
from domain.services.text_cleaner import clean_text


class PandasDataCleaner(IDataCleaner):
    """
    A concrete implementation of IDataCleaner that uses pandas and the domain's
    text cleaning service.
    """

    def clean_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the review data in a pandas DataFrame.
        """
        df = raw_data.copy()

        # Standardize column names
        df.rename(
            columns={'Calificacion': 'calificacion',
                     'Comentarios': 'comentarios'}, inplace=True)

        # Clean ratings
        df['calificacion'] = pd.to_numeric(df['calificacion'], errors='coerce')
        df.dropna(subset=['calificacion'], inplace=True)
        df['calificacion'] = df['calificacion'].astype('Int8')

        # Clean comments using the domain service
        df['comentarios'] = df['comentarios'].apply(clean_text)
        df.dropna(subset=['comentarios'], inplace=True)

        # Filter irrelevant comments
        df = self._filter_irrelevant_comments(df)

        print(f"Cleaning complete. {len(df)} valid comments remaining.")
        return df

    def _filter_irrelevant_comments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters out comments that do not provide meaningful feedback.
        """
        irrelevant_patterns = [
            r'^solo califica',
            r'^no (?:brinda|proporciona|quiso|tiene|contesta)',
            r'^sin comentarios?$',
            r'^ningun[ao]s?$',
            r'^\d+cm$',
            r'^se envia whatsapp$',
            r'^(?:bdc|ok|na|s c)$'
        ]

        regex_filter = '|'.join(irrelevant_patterns)
        irrelevant_mask = df['comentarios'].str.contains(
            regex_filter,
            regex=True,
            na=False)
        short_mask = df['comentarios'].str.len() < 5

        return df[~(irrelevant_mask | short_mask)]
