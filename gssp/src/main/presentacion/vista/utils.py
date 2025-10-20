import plotly.express as px

categorias = ['promotor', 'neutro', 'detractor']
colores = px.colors.sequential.Viridis[len(categorias)]
color_discrete_map = dict(zip(categorias, colores))
