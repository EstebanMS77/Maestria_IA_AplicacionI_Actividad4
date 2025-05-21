from dash import Dash, html, dcc,dash_table
import plotly.express as px
import pandas as pd
from pandasql import sqldf
import json


app = Dash(__name__)
server = app.server

df_Codigos_Muerte = pd.read_excel(r"Maestria_IA_AplicacionI_Actividad4\data\_Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx",sheet_name="Final")
df_Codigos_Departamento = pd.read_excel(r"Maestria_IA_AplicacionI_Actividad4\data\Divipola_CE_.xlsx", sheet_name="Hoja1")
df_Data_Muertes = pd.read_excel(r"Maestria_IA_AplicacionI_Actividad4\data\Anexo1.NoFetal2019_CE_15-03-23.xlsx",sheet_name="No_Fetales_2019")
with open(r"Maestria_IA_AplicacionI_Actividad4\data\Colombia.geo.json", encoding='utf-8') as f:
    geojson_col = json.load(f)

Query_TotalMuertes = """
SELECT Df_CD.DEPARTAMENTO, Df_CD.COD_DEPARTAMENTO, COUNT(Df_CD.DEPARTAMENTO) AS Total_Muertes
FROM df_Codigos_Departamento as Df_CD
INNER JOIN df_Data_Muertes as Df_DM ON Df_DM.COD_DEPARTAMENTO = Df_CD.COD_DEPARTAMENTO 
GROUP BY Df_CD.DEPARTAMENTO, Df_CD.COD_DEPARTAMENTO
"""

df_Total_Muertes = sqldf(Query_TotalMuertes, locals())

Query_TotalPorMes = """

SELECT MES, COUNT(MES) AS Muertes
FROM df_Data_Muertes
GROUP BY MES ORDER BY MES DESC   
"""

Query_TopCiudades = """

SELECT Df_CD.MUNICIPIO,COUNT(Df_CD.MUNICIPIO) AS Total_Muertes FROM df_Data_Muertes AS Df_DM
INNER JOIN df_Codigos_Muerte as Df_CM ON Df_CM.[Código de la CIE-10 cuatro caracteres] = Df_DM.COD_MUERTE
INNER JOIN df_Codigos_Departamento as Df_CD ON Df_DM.COD_MUNICIPIO = Df_CD.COD_MUNICIPIO 
WHERE DF_DM.COD_MUERTE IN ('X950','X951','X952','X953','X954','X955','X956','X957','X958','X959')
GROUP BY Df_CD.MUNICIPIO ORDER BY Total_Muertes DESC LIMIT 5
"""


Query_TablaCiudades = """

SELECT Df_DM.COD_MUERTE, Df_CM.[Descripcion  de códigos mortalidad a cuatro caracteres], COUNT(Df_DM.COD_MUERTE) AS Total_Muertes FROM df_Data_Muertes AS Df_DM
INNER JOIN df_Codigos_Muerte as Df_CM ON Df_CM.[Código de la CIE-10 cuatro caracteres] = Df_DM.COD_MUERTE
GROUP BY  Df_DM.COD_MUERTE ORDER BY Total_Muertes DESC LIMIT 10
"""

df_TotalPorMes = sqldf(Query_TotalPorMes, locals())

df_TopCiudades = sqldf(Query_TopCiudades, locals())

df_TablaCiudades = sqldf(Query_TablaCiudades, locals())


print(df_TablaCiudades.head(10))

df_Total_Muertes['COD_DEPARTAMENTO'] = df_Total_Muertes['COD_DEPARTAMENTO'].astype(str).str.zfill(2)

fig = px.choropleth(
    df_Total_Muertes,
    geojson=geojson_col,
    locations='COD_DEPARTAMENTO', 
    featureidkey='properties.DPTO', 
    color='Total_Muertes',  
    color_continuous_scale="Jet",
    range_color=(0, df_Total_Muertes['Total_Muertes'].max()),
    labels={'Total_Muertes': 'Número de muertes'},
    title='Distribución de muertes por departamento en Colombia (2019)',
)


fig_bar = px.bar(
        df_TopCiudades,
        x='MUNICIPIO',
        y='Total_Muertes',
        color='MUNICIPIO',
        text_auto=True,
        title='Top 5 Ciudades con más muertes por homicidio en 2019',
        labels={
            'Total_Muertes': 'Total_Muertes',
            'MUNICIPIO': 'MUNICIPIO',
        },
        height=500
    )

# Personalizar el diseño del mapa
fig.update_geos(
    fitbounds="locations",
    visible=False,
    subunitcolor="gray",
    showcountries=True,
    showsubunits=True
)

fig.update_layout(
    margin={"r":0,"t":40,"l":0,"b":0},
    coloraxis_colorbar={
        'title': 'Número de muertes',
        'thickness': 20,
        'len': 0.75
    },
    title_x=0.5
)

# Diseño de la aplicación
app.layout = html.Div([
    html.H1('Muertes por Departamento en Colombia - 2019', style={'textAlign': 'center'}),
    dcc.Graph(
        id='colombia-map',
        figure=fig,
        style={'height': '700px'}
    ),
    html.Div([
        html.P('Fuente: DANE', 
              style={'textAlign': 'center', 'fontStyle': 'italic'})
    ]),html.Div([

    html.H1('Tendencia de Muertes por Mes', style={'textAlign': 'center'}),
    
    dcc.Graph(
        id='line-chart',
        figure=px.line(
            df_TotalPorMes,
            x='MES',
            y='Muertes',
            title='Evolución Mensual de Muertes',
            markers=True,  # Muestra puntos en cada dato
            template='plotly_white'
        ).update_layout(
            xaxis_title='Mes',
            yaxis_title='Número de Muertes',
            hovermode='x unified'
        )
    )
]),html.Div([
    html.H1('5 ciudades más violentas de Colombia', style={'textAlign': 'center'}),
    dcc.Graph(
        id='Bar-chart',
        figure=fig_bar,
        style={'height': '700px'}
    ),
    html.Div([
        html.P('Fuente: DANE', 
              style={'textAlign': 'center', 'fontStyle': 'italic'})
    ])
]),html.Div([
    html.H1('Las 10 principales causas de muerte en Colombia', style={'textAlign': 'center'}),
    dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df_TablaCiudades.columns],
    data=df_TablaCiudades.to_dict('records'),
    style_table={'overflowX': 'auto'},  # Permite scroll horizontal
    style_cell={
        'textAlign': 'left',
        'padding': '10px',
        'whiteSpace': 'normal',
        'height': 'auto',
    },
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold',
        'border': '1px solid black'
    },
    style_data={
        'border': '1px solid grey'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ],
    filter_action="native",  # Permite filtrado
    sort_action="native",    # Permite ordenamiento
    page_action="native",    # Paginación
    page_size=10             # 10 filas por página
)
])

])


if __name__ == '__main__':
    app.run(debug=True)