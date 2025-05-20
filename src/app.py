from dash import Dash, html, dcc
import plotly.express as px

app = Dash(__name__)
server = app.server

df = px.data.iris()

fig = px.scatter(
    df,
    x="sepal_width",
    y="sepal_length",
    color="species",
    title="Iris Dataset Scatter Plot"
)

app.layout = html.Div([
    html.H1("Iris Dataset Visualization"),
    dcc.Graph(
        id='iris-scatter-plot',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run(debug=True)