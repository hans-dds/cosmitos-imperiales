def limpiar_datos(df):
    df['clasificacion'] = df['clasificacion'].str.lower().str.strip()
    return df

def calcular_longitud(df):
    df['longitud'] = df['comentarios'].astype(str).apply(lambda x: len(x.split()))
    return df
