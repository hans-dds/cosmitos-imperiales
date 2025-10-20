import pandas as pd

df = pd.read_csv('comentarios_limpios.csv')


df_sample = df.sample(n=50, random_state=42) 

def clasificar(calificacion):
    if calificacion >= 9:
        return 'promotor'
    elif calificacion >= 7:
        return 'neutro'
    else:
        return 'detractor'

df_sample['clasificacion'] = df_sample['calificacion'].apply(clasificar)

df_sample.to_csv('arc_aleatorio.csv', index=False)
print(df_sample)
