import pandas as pd
import numpy as np
import re
import string
import unicodedata
from datos import GuardarDatosArchivo

class ServicioLimpiarDatos:
    """
    limpieza y preprocesamiento de datos desde un archivo Excel.
    """
    def __init__(self):
        print("Servicio de Limpieza de Datos inicializado.")
        # Hojas y columnas esperadas en el archivo Excel
        self.HOJAS_REQUERIDAS = ["ATC", "Encuesta salida"]
        self.COLUMNAS_REQUERIDAS = ['Calificacion', 'Comentarios']

    def _leer_y_unificar_excel(self, ruta_archivo: str) -> pd.DataFrame:
        """
        Lee las hojas especificadas de un archivo Excel, extrae las columnas
        requeridas y las unifica en un solo DataFrame.
        """
        print(f"Leyendo archivo Excel: '{ruta_archivo}'...")
        lista_dfs = []
        try:
            with pd.ExcelFile(ruta_archivo, engine='openpyxl') as xlsx:
                for hoja in self.HOJAS_REQUERIDAS:
                    if hoja in xlsx.sheet_names:
                        df_hoja = pd.read_excel(xlsx, sheet_name=hoja)
                        if all(col in df_hoja.columns for col in self.COLUMNAS_REQUERIDAS):
                            lista_dfs.append(df_hoja[self.COLUMNAS_REQUERIDAS])
                        else:
                            print(f"Advertencia: La hoja '{hoja}' no contiene las columnas esperadas ('Calificacion', 'Comentarios'). Se omitirá.")
                    else:
                        print(f"Advertencia: La hoja '{hoja}' no se encontró en el archivo. Se omitirá.")
        except FileNotFoundError:
            print(f"ERROR: No se encontró el archivo en la ruta: {ruta_archivo}")
            return pd.DataFrame()

        if not lista_dfs:
            print("ERROR: No se pudo extraer ningún dato válido de las hojas especificadas.")
            return pd.DataFrame()

        df_completo = pd.concat(lista_dfs, ignore_index=True)
        df_completo.rename(columns={'Calificacion': 'calificacion', 'Comentarios': 'comentarios'}, inplace=True)
        return df_completo

    def _limpiar_calificaciones(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y formatea la columna de calificaciones."""
        print("Limpiando columna 'calificacion'...")
        calif_con_espacios = df['calificacion'].astype(str).str.contains(' ')
        df.loc[calif_con_espacios, 'calificacion'] = df.loc[calif_con_espacios, 'calificacion'].astype(str).str.split().str[0]
        
        # Convertir a numérico, los errores se convierten en NaT (Not a Time) que luego se dropean
        df['calificacion'] = pd.to_numeric(df['calificacion'], errors='coerce')
        df.dropna(subset=['calificacion'], inplace=True)
        df['calificacion'] = df['calificacion'].astype('Int8')
        return df

    def _limpiar_texto_individual(self, texto: str) -> str:
        """Aplica todas las reglas de limpieza a una sola cadena de texto."""
        if not isinstance(texto, str) or texto.strip() == '':
            return np.nan

        # 1. Convertir a minúsculas
        texto = texto.lower()
        # 2. Eliminar acentos
        nfkd_form = unicodedata.normalize('NFD', texto)
        texto = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        # 3. Eliminar signos de puntuación
        texto = re.sub(f'[{re.escape(string.punctuation)}]', ' ', texto)
        # 4. Eliminar saltos de línea y espacios extra
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto if texto else np.nan

    def _filtrar_comentarios_irrelevantes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra comentarios que no aportan información utilizando un método
        más inteligente basado en patrones en lugar de una lista fija.
        """
        print("Filtrando comentarios irrelevantes...")
        
        # Patrones de comentarios que indican que no hay feedback real.
        patrones_irrelevantes = [
            r'^solo califica',
            r'^no (?:brinda|proporciona|quiso|tiene|contesta)',
            r'^sin comentarios?$',
            r'^ningun[ao]s?$',
            r'^\d+cm$',
            r'^se envia whatsapp$',
            r'^(?:bdc|ok|na|s c)$'
        ]

        regex_filtro = '|'.join(patrones_irrelevantes)
        mascara_irrelevante = df['comentarios'].str.contains(regex_filtro, regex=True, na=False)
        mascara_corta = df['comentarios'].str.len() < 5
        df_filtrado = df[~(mascara_irrelevante | mascara_corta)]
        
        print(f"Se eliminaron {len(df) - len(df_filtrado)} comentarios irrelevantes o demasiado cortos.")
        return df_filtrado

    def procesar_archivo_excel(self, ruta_archivo: str) -> pd.DataFrame:
        """
        ESTO EJECUTA TODO el proceso de limpieza: leer, unificar, limpiar y filtrar.
        """
        df = self._leer_y_unificar_excel(ruta_archivo)
        if df.empty:
            return df

        df = self._limpiar_calificaciones(df)
        
        print("Limpiando columna 'comentarios'...")
        df['comentarios'] = df['comentarios'].apply(self._limpiar_texto_individual)
        df.dropna(subset=['comentarios'], inplace=True)

        df_final = self._filtrar_comentarios_irrelevantes(df)
        
        print(f"\nProceso de limpieza finalizado. Se obtuvieron {len(df_final)} comentarios válidos.")
        nombre = ruta_archivo.split('/')[-1].replace('.xlsx', '')
        
        # Esta linea llama a la capa de DATOS
        GuardarDatosArchivo.GuardarDatosArchivo().guardar_datos_limpios(df_final, nombre)
        #return df_final

    def procesar_datos_en_memoria(self, datos: dict) -> pd.DataFrame:
        """
        Procesa los datos ya cargados (desde memoria) que provienen de un Excel con múltiples hojas.
        Aplica limpieza de calificaciones y comentarios, y devuelve un DataFrame limpio.
        """
        print("Procesando datos desde memoria...")
        lista_dfs = []

        for hoja in self.HOJAS_REQUERIDAS:
            if hoja in datos:
                df_hoja = datos[hoja]
                if all(col in df_hoja.columns for col in self.COLUMNAS_REQUERIDAS):
                    lista_dfs.append(df_hoja[self.COLUMNAS_REQUERIDAS])
                else:
                    print(f"La hoja '{hoja}' no contiene las columnas requeridas. Se omite.")
            else:
                print(f"La hoja '{hoja}' no está presente en los datos. Se omite.")

        if not lista_dfs:
            print("No se encontró información válida en las hojas requeridas.")
            return pd.DataFrame()

        df = pd.concat(lista_dfs, ignore_index=True)
        df.rename(columns={'Calificacion': 'calificacion', 'Comentarios': 'comentarios'}, inplace=True)

        df = self._limpiar_calificaciones(df)
        print("Limpiando columna 'comentarios'...")
        df['comentarios'] = df['comentarios'].apply(self._limpiar_texto_individual)
        df.dropna(subset=['comentarios'], inplace=True)

        df_final = self._filtrar_comentarios_irrelevantes(df)
        print(f"Proceso de limpieza terminado. Se conservaron {len(df_final)} comentarios.")
        return df_final


if __name__ == "__main__":
    
    # --- Configuración ---
    ARCHIVO_EXCEL_ENTRADA = 'c_Mayo_2025.xlsx' 
    ARCHIVO_CSV_SALIDA = 'c_Mayo_2025.csv'
    
    # 1. Crear una instancia del servicio de limpieza
    limpiador = ServicioLimpiarDatos()
