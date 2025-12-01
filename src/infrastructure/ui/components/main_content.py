"""Componente principal que maneja el contenido de la página principal."""

import pandas as pd
import streamlit as st
from typing import Optional
from pandas.tseries.offsets import DateOffset

from infrastructure.ui.controllers.streamlit_controller import \
    StreamlitController
from infrastructure.ui.components.analysis_state_manager import \
    AnalysisStateManager
from infrastructure.ui.components.charts_component import ChartsComponent
from infrastructure.ui.components.table_component import TableComponent
from infrastructure.ui.components.export_component import ExportComponent
from infrastructure.ui.components.word_cloud_component import \
    WordCloudComponent


class MainContent:
    """
    Componente principal que orquesta la visualización y manejo de análisis.
    """

    def __init__(self, controller: StreamlitController):
        """
        Inicializa el componente principal.
        Args:
            controller: Controlador de Streamlit para interactuar con
            casos de uso
        """
        self._controller = controller
        self._state_manager = AnalysisStateManager()
        self._charts = ChartsComponent()
        self._table = TableComponent()
        self._export = ExportComponent(controller)
        self._word_cloud = WordCloudComponent()

    def render(
        self,
        uploaded_file,
        analysis_to_load: Optional[str]
    ):
        """
        Renderiza el contenido principal de la página.
        Args:
            uploaded_file: Archivo subido por el usuario (si hay)
            analysis_to_load: Nombre del análisis a cargar (si hay)
        """
        # Inicializar estado
        self._state_manager.initialize_state()
        # Procesar archivo subido
        if uploaded_file:
            self._handle_file_upload(uploaded_file)
        # Cargar análisis guardado si es necesario
        if self._state_manager.needs_load(analysis_to_load):
            self._handle_load_analysis(analysis_to_load)
        # Mostrar contenido del análisis actual
        self._render_analysis_display()

    def _handle_file_upload(self, uploaded_file):
        """
        Maneja la carga y procesamiento de un archivo.
        Args:
            uploaded_file: Archivo subido por el usuario
        """
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        # Verificar si este archivo ya fue procesado
        if self._state_manager.is_file_already_processed(file_id):
            return
        file_basename = uploaded_file.name.split('.')[0]
        with st.spinner(
                "Procesando archivo... Esto puede tardar unos segundos."):
            success, analyzed_df, error_message = \
                self._controller.handle_file_upload(
                    uploaded_file,
                    file_basename
                )
        if success and analyzed_df is not None:
            new_analysis_name = f"analisis_{file_basename}"
            st.success(
                f"Archivo '{uploaded_file.name}' procesado y guardado "
                "exitosamente."
            )
            # Establecer el nuevo análisis
            self._state_manager.set_new_analysis(
                new_analysis_name,
                analyzed_df,
                file_id
            )
            # Limpiar selecciones de eliminación
            self._state_manager.clear_delete_selection()
            # Forzar actualización
            st.rerun()
        else:
            st.error(
                f"Ocurrió un error al procesar el archivo: {error_message}")
            self._state_manager.clear_processed_file_flag()

    def _handle_load_analysis(self, analysis_to_load: Optional[str]):
        """
        Maneja la carga de un análisis guardado.
        Args:
            analysis_to_load: Nombre del análisis a cargar
        """
        selected_analysis = st.session_state.get('selected_analysis')
        analysis_name = analysis_to_load or selected_analysis
        if not analysis_name:
            return
        success, loaded_df, error_message = \
            self._controller.handle_load_analysis(
                analysis_name
            )
        if success and loaded_df is not None:
            self._state_manager.set_loaded_analysis(analysis_name, loaded_df)
        else:
            if error_message:
                st.warning(error_message)
            self._state_manager.clear_analysis_display()

    def _render_analysis_display(self):
        """Renderiza la visualización del análisis actual."""
        df_to_show = self._state_manager.get_current_analysis()
        analysis_name = self._state_manager.get_current_analysis_name()
        if df_to_show is None or df_to_show.empty:
            return
        # Mostrar encabezado
        st.header(analysis_name)
        # Preparar DataFrame para visualización usando el caso de uso
        df_prepared, color_map = self._controller.prepare_analysis_display(
            df_to_show)
        # Aplicar filtros de rango de fechas (por mes/año) antes de renderizar
        df_filtered = self._apply_monthly_date_filter(df_prepared)
        # Renderizar componentes
        self._charts.render(df_filtered, color_map)
        self._word_cloud.render(df_filtered)
        
        # Renderizar tabla editable y manejar guardado
        self._render_editable_table_with_save(df_filtered, analysis_name, color_map)
        
        self._export.render(df_filtered, analysis_name, color_map)
    
    def _render_editable_table_with_save(
        self, 
        df: pd.DataFrame, 
        analysis_name: str,
        color_map: dict
    ):
        """
        Renderiza tabla editable con botón de guardar cambios.
        
        Args:
            df: DataFrame filtrado a mostrar
            analysis_name: Nombre del análisis actual
            color_map: Mapa de colores para gráficos
        """
        # Renderizar tabla editable
        edited_df, has_changes = self._table.render_editable(df)
        
        # Mostrar botón de guardar si hay cambios
        if has_changes:
            st.info("⚠️ Se han detectado cambios en las etiquetas de clasificación.")
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("💾 Guardar cambios", type="primary", use_container_width=True):
                    self._handle_sentiment_update(
                        analysis_name=analysis_name,
                        original_df=df,
                        edited_df=edited_df
                    )
        else:
            # Mensaje informativo cuando no hay cambios
            st.caption("💡 Puedes editar las clasificaciones usando los menús desplegables de la tabla.")
    
    def _handle_sentiment_update(
        self,
        analysis_name: str,
        original_df: pd.DataFrame,
        edited_df: pd.DataFrame
    ):
        """
        Maneja la actualización de sentimientos modificados.
        
        Args:
            analysis_name: Nombre del análisis original
            original_df: DataFrame original con columnas en español
            edited_df: DataFrame editado con columnas en español
        """
        # Revertir el mapeo de nombres de columnas
        reverse_mapping = {
            'Calificación': 'calificacion',
            'Comentario': 'comentarios',
            'Clasificación': 'Clasificacion',
            'Fiabilidad': 'Fiabilidad'
        }
        
        # Renombrar columnas del DataFrame editado a nombres originales
        edited_df_original_names = edited_df.rename(columns=reverse_mapping)
        
        # Detectar modificaciones comparando DataFrames
        modifications = []
        
        # Usar los índices del DataFrame original
        for idx in original_df.index:
            # Buscar el índice correspondiente en el DataFrame editado
            # (pueden ser diferentes después de filtros)
            if idx in edited_df_original_names.index:
                original_label = original_df.at[idx, 'Clasificacion']
                new_label = edited_df_original_names.at[idx, 'Clasificacion']
                
                if original_label != new_label:
                    modifications.append((idx, new_label))
        
        if not modifications:
            st.warning("No se detectaron cambios reales para guardar.")
            return
        
        # Obtener el DataFrame completo sin filtros desde el estado
        full_df = self._state_manager.get_current_analysis()
        
        # Llamar al controlador para procesar la actualización
        with st.spinner("Guardando cambios y creando nuevo análisis..."):
            success, new_analysis_name, message = self._controller.handle_update_sentiment(
                analysis_name=analysis_name,
                df=full_df,
                modifications=modifications
            )
        
        if success:
            st.success(f"✅ {message}")
            st.info(f"📊 Nuevo análisis creado: **{new_analysis_name}**")
            
            # Limpiar estado de edición
            if 'original_df_for_edit' in st.session_state:
                del st.session_state['original_df_for_edit']
            
            # Recargar el análisis para mostrar los cambios
            st.rerun()
        else:
            st.error(f"❌ Error al guardar cambios: {message}")
    
    def _apply_monthly_date_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica un filtro de fechas por mes/año al DataFrame según la
        selección del usuario.
        El filtro se basa en una columna 'fecha' (datetime). Si no existe,
        el DataFrame se devuelve sin cambios.
        Args:
            df: DataFrame con los datos a filtrar
        Returns:
            DataFrame filtrado por rango de fechas
        """
        if 'fecha' not in df.columns:
            st.info(
                "Este análisis no contiene información de fechas. "
                "El filtro por rango mensual no se aplicará."
            )
            return df
        # Asegurar tipo datetime
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        if df['fecha'].isna().all():
            st.info(
                "No se pudo interpretar ninguna fecha válida en la columna "
                "'fecha'. Se mostrará la información completa sin filtrar "
                "por mes/año."
            )
            return df
        # Normalizar a inicio de mes para trabajar solo con mes/año
        df['mes'] = df['fecha'].dt.to_period('M').dt.to_timestamp()
        # Validar rango disponible de meses en los datos
        min_month = df['mes'].min()
        max_month = df['mes'].max()
        unique_months = sorted(df['mes'].dropna().unique())
        total_months = len(unique_months)
        if pd.isna(min_month) or pd.isna(max_month):
            return df
        st.subheader("Rango de fechas (por mes)")
        # Selector de rangos rápidos
        rango_rapido = st.selectbox(
            "Rango rápido",
            options=[
                "Todos",
                "Último mes",
                "Último trimestre",
                "Último año",
                "Personalizado",
            ],
            index=0,
            help="Selecciona un rango temporal basado en meses."
        )
        # Valores por defecto para fecha_inicio/fecha_fin en controles
        # personalizados
        default_start = min_month.to_pydatetime().date()
        default_end = max_month.to_pydatetime().date()
        fecha_inicio = default_start
        fecha_fin = default_end
        if rango_rapido == "Último mes":
            fecha_inicio = max_month.to_pydatetime().date()
            fecha_fin = max_month.to_pydatetime().date()
        elif rango_rapido == "Último trimestre":
            # Últimos 3 meses
            fecha_fin = max_month.to_pydatetime().date()
            fecha_inicio_ts = max_month - DateOffset(months=2)
            if fecha_inicio_ts < min_month:
                fecha_inicio_ts = min_month
            fecha_inicio = fecha_inicio_ts.to_pydatetime().date()
            if total_months < 3:
                st.info(
                    f"Solo hay datos de {total_months} mes(es) distintos. "
                    "Se mostrará la información disponible más reciente."
                )
        elif rango_rapido == "Último año":
            fecha_fin = max_month.to_pydatetime().date()
            fecha_inicio_ts = max_month - DateOffset(months=11)
            if fecha_inicio_ts < min_month:
                fecha_inicio_ts = min_month
            fecha_inicio = fecha_inicio_ts.to_pydatetime().date()
            if total_months < 12:
                st.info(
                    f"Solo hay datos de {total_months} mes(es) distintos. "
                    "Se mostrará la información disponible más reciente."
                )
        elif rango_rapido == "Personalizado":
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input(
                    "Mes/Año inicio",
                    value=default_start,
                    help="Selecciona cualquier día del mes; solo se usará el "
                         "mes y año."
                )
            with col2:
                fecha_fin = st.date_input(
                    "Mes/Año fin",
                    value=default_end,
                    help="Selecciona cualquier día del mes; solo se usará el "
                         "mes y año."
                )
        # Normalizar fechas seleccionadas a primer día de mes
        start_month = pd.to_datetime(
            fecha_inicio).to_period('M').to_timestamp()
        end_month = pd.to_datetime(fecha_fin).to_period('M').to_timestamp()
        if start_month > end_month:
            st.warning(
                "La fecha de inicio es posterior a la fecha de fin. "
                "Se mostrará el rango completo.")
            start_month, end_month = min_month, max_month
        # Aplicar filtro manteniendo el orden cronológico por fecha
        mask = (df['mes'] >= start_month) & (df['mes'] <= end_month)
        filtered_df = df[mask].sort_values('fecha')
        st.caption(
            f"Mostrando datos desde {start_month.strftime('%Y-%m')} "
            f"hasta {end_month.strftime('%Y-%m')} "
            f"({len(filtered_df)} registros)."
        )
        # Eliminar columna auxiliar antes de devolver
        return filtered_df.drop(columns=['mes'])
