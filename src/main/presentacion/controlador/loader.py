import pandas as pd
from negocio.ServicioValidarArchivo import ServicioValidarArchivo as SVA
from negocio.ServicioLimpiarDatos import ServicioLimpiarDatos as SLD
from negocio.ServicioAnalisisEvaluacion import ServicioAnalisisEvaluacion as SAE
import os

def process_uploaded_file(archivo):
    extension = archivo.name.split('.')[-1].lower()

    sld = SLD()

    try:
        # .../src/main/presentacion/controlador/
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Subir dos niveles para llegar a 'src/main/'
        # .../src/main/
        main_dir = os.path.join(current_dir, '..', '..')
        
        # Construir la ruta al modelo
        ruta_modelo = os.path.join(main_dir, 'clasificador_sentimiento_final.pkl')
        
        print(f"Ruta absoluta del modelo: {ruta_modelo}")

        if not os.path.exists(ruta_modelo):
            print("Error: El archivo del modelo NO existe en la ruta.")
            return None, f"Error interno: No se encuentra el archivo del modelo en {ruta_modelo}", False

        sae = SAE(ruta_modelo)

    except Exception as e:
        print(f"Error al inicializar servicios o rutas: {e}")
        return None, f"Error al inicializar el servicio de análisis: {e}", False

    df_limpio = pd.DataFrame()
    mensaje_exito = ""

    if extension == 'csv':
        archivo.seek(0)
        df_raw = pd.read_csv(archivo)
        
        if 'Calificacion' not in df_raw.columns or 'Comentarios' not in df_raw.columns:
            return None, "El CSV debe tener las columnas 'Calificacion' y 'Comentarios'.", False
        
        df_raw.rename(columns={'Calificacion': 'calificacion', 'Comentarios': 'comentarios'}, inplace=True)
        
        df_con_calif = sld._limpiar_calificaciones(df_raw)
        df_con_calif['comentarios'] = df_con_calif['comentarios'].apply(sld._limpiar_texto_individual)
        df_con_calif.dropna(subset=['comentarios'], inplace=True)
        df_limpio = sld._filtrar_comentarios_irrelevantes(df_con_calif)
        mensaje_exito = "Archivo CSV limpiado y clasificado correctamente."

    elif extension in ['xls', 'xlsx']:
        archivo.seek(0)
        sva = SVA()
        valido, mensaje = sva.leer_archivo(archivo, archivo.name)

        if not valido:
            return None, mensaje, False

        datos = sva.obtener_datos_archivo()
        if datos is None:
            return None, "No se pudieron obtener datos del archivo.", False
        
        # SLD procesa el dict de las dos hojas
        df_limpio = sld.procesar_datos_en_memoria(datos)
        mensaje_exito = "Archivo Excel validado, limpiado y clasificado correctamente."

    else:
        return None, "Extensión de archivo no soportada.", False

    # Análisis
    if df_limpio.empty:
        return df_limpio, "El archivo fue válido, pero no contiene datos útiles tras limpieza.", True

    try:
        df_clasificado = sae.realizar_analisis_sentimientos(df_limpio)

        if 'Clasificacion' not in df_clasificado.columns:
            return None, "No se pudo generar la clasificación. Revisa la carga del modelo.", False
        
        etiquetas = {
            -1: "Detractor",
            0: "Neutro",
            1: "Promotor"
        }
        df_clasificado['Clasificacion'] = df_clasificado['Clasificacion'].map(etiquetas)
        
        # Se añade 'longitud' para 'layout.py'
        if 'comentarios' in df_clasificado.columns:
            df_clasificado['longitud'] = df_clasificado['comentarios'].str.len()
        else:
            df_clasificado['longitud'] = 0

        return df_clasificado, mensaje_exito, True

    except Exception as e:
        print(f"Error durante el análisis de sentimientos: {e}")
        import traceback
        traceback.print_exc() # Imprime el error completo en la consola
        return None, f"Error al realizar el análisis: {str(e)}", False

