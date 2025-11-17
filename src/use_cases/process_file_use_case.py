import pandas as pd
from datetime import datetime
from typing import Optional

from use_cases.ports.data_cleaner import IDataCleaner
from use_cases.ports.sentiment_analyzer import ISentimentAnalyzer
from use_cases.ports.analysis_repository import IAnalysisRepository


class ProcessFileUseCase:
    """
    Este caso de uso orquesta la limpieza, análisis y almacenamiento de datos
    de reseñas desde un archivo.
    """

    def __init__(
        self,
        data_cleaner: IDataCleaner,
        sentiment_analyzer: ISentimentAnalyzer,
        analysis_repository: IAnalysisRepository,
    ):
        self._data_cleaner = data_cleaner
        self._sentiment_analyzer = sentiment_analyzer
        self._analysis_repository = analysis_repository

    def execute(
            self,
            raw_data: pd.DataFrame,
            file_basename: str) -> pd.DataFrame:
        """
        Ejecuta el caso de uso.

        Args:
            raw_data: El DataFrame sin procesar leído del archivo subido.
            file_basename: El nombre base del archivo original
            (ej., 'c_Abril_2025').

        Returns:
            El DataFrame que contiene los datos analizados.
        """
        # 1. Limpiar los datos
        cleaned_data = self._data_cleaner.clean_data(raw_data)
        if cleaned_data.empty:
            raise ValueError("Los datos están vacíos después del proceso de limpieza.")

        # 2. Analizar sentimiento
        analyzed_data = self._sentiment_analyzer.analyze(cleaned_data)
        if analyzed_data.empty:
            raise ValueError("Los datos están vacíos después del análisis de sentimiento.")

        # 2.b Añadir información temporal derivada del nombre del archivo.
        # Esto permite trabajar por mes/año aunque el archivo no tenga una
        # columna de fecha explícita.
        fecha_mes = self._extract_month_year_from_basename(file_basename)
        if fecha_mes is not None and 'fecha' not in analyzed_data.columns:
            # Se usa el primer día del mes como representación del mes/año.
            analyzed_data['fecha'] = pd.to_datetime(fecha_mes)

        # 3. Guardar los resultados
        table_name = f"analisis_{file_basename}"
        self._analysis_repository.save_csv(analyzed_data, file_basename)
        self._analysis_repository.save_mysql(analyzed_data, table_name)

        return analyzed_data
    
    @staticmethod
    def _extract_month_year_from_basename(file_basename: str) -> Optional[datetime]:
        """
        A partir del nombre base del archivo (ej. 'c_Abril_2025') obtiene una
        fecha representativa (primer día de ese mes).
        
        Esto asegura que podamos construir una columna 'fecha' uniforme que
        luego se utilizará para filtros por mes/año en la UI.
        
        Args:
            file_basename: Nombre base del archivo (ej. 'c_Abril_2025')
            
        Returns:
            Fecha del primer día del mes/año detectado, o None si no se puede extraer
        """
        # Separar por guiones bajos esperando un formato similar a 'c_Mes_YYYY'
        parts = file_basename.split('_')
        if len(parts) < 3:
            return None
        
        # El mes suele ser la segunda parte y el año la tercera
        month_name = parts[-2]
        year_part = parts[-1]
        
        month_map = {
            'enero': 1,
            'febrero': 2,
            'marzo': 3,
            'abril': 4,
            'mayo': 5,
            'junio': 6,
            'julio': 7,
            'agosto': 8,
            'septiembre': 9,
            'setiembre': 9,
            'octubre': 10,
            'noviembre': 11,
            'diciembre': 12,
        }
        
        month_key = month_name.lower()
        if month_key not in month_map:
            return None
        
        try:
            year = int(year_part)
        except ValueError:
            return None
        
        try:
            return datetime(year=year, month=month_map[month_key], day=1)
        except ValueError:
            return None
