import pandas as pd
from negocio.ServicioValidarArchivo import ServicioValidarArchivo as SVA
from negocio.ServicioLimpiarDatos import ServicioLimpiarDatos as SLD
from negocio.ServicioAnalisisEvaluacion import ServicioAnalisisEvaluacion as SAE
import os

def cargar_datos(archivo):
    extension = archivo.name.split('.')[-1].lower()

    if extension == 'csv':
        archivo.seek(0)
        df = pd.read_csv(archivo)
        return df, "Archivo CSV cargado correctamente.", True

    elif extension in ['xls', 'xlsx']:
        archivo.seek(0)
        sva = SVA()
        valido, mensaje = sva.leer_archivo(archivo, archivo.name)

        if not valido:
            return None, mensaje, False

        datos = sva.obtener_datos_archivo()

        # Paso 1: Limpiar datos
        sld = SLD()
        df_limpio = sld.procesar_datos_en_memoria(datos)

        if df_limpio.empty:
            return None, "El archivo fue válido, pero no contiene datos útiles tras limpieza.", False

        ruta_modelo = os.path.abspath(os.path.join(os.getcwd(), 'main', 'clasificador_sentimiento_final.pkl'))
        print("Ruta absoluta del modelo:", ruta_modelo)

        # Paso 2: Clasificar
        try:
            
            sae = SAE(ruta_modelo=ruta_modelo)

            # sae = SAE(ruta_modelo='clasificador_sentimiento_final.pkl')
            df_clasificado = sae.realizar_analisis_sentimientos(df_limpio)

            if 'Clasificacion' not in df_clasificado.columns:
                return None, "No se pudo generar la clasificación en los comentarios.", False
            
            etiquetas = {
                -1: "Detractor",
                0: "Neutro",
                1: "Promotor"
            }
            df_clasificado['Clasificacion'] = df_clasificado['Clasificacion'].map(etiquetas)

            return df_clasificado, "Archivo Excel validado, limpiado y clasificado correctamente.", True

        except Exception as e:
            return None, f"Error al cargar el modelo de análisis: {str(e)}\nRuta intentada: {ruta_modelo}", False

    else:
        return None, "Extensión de archivo no soportada.", False
