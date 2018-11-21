import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from explore import prepare_data, create_map_plotly, empty_plot, plot_time_series, plot_average_aggregate, table_number_dataopints

import json
from textwrap import dedent as d


# ===== INITIALIZE =========
# ==========================

# Load data
df, est, provincias = prepare_data()

# Initialize map
fig_map = create_map_plotly(est, provincias)

# Launch app
external_stylesheets = ['https://codepen.io/plotly/pen/EQZeaW.css']  # ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# ===== LAYOUT ===========
# ========================


app.layout = html.Div([

    # Header
    html.Div([

        # html.Div([
        #     html.Img(
        #         src='https://www.coal.es/wp-content/uploads/2018/08/jcyl.jpg',
        #         height='80', width='135')
        # ], className='two columns'),

        html.Div([
            html.H1(children='Calidad del aire en Castilla y León')
        ], className='nine columns')
    ], className='row'),

    # Main
    html.Div([
        # Left column
        html.Div(
            [

                html.Label('Seleccione componente que desee analizar'),
                dcc.Dropdown(
                    id='drop-component',
                    options=[
                        {'label': 'CO (mg/m3)', 'value': 'CO (mg/m3)'},
                        {'label': 'NO (ug/m3)', 'value': 'NO (ug/m3)'},
                        {'label': 'NO2 (ug/m3)', 'value': 'NO2 (ug/m3)'},
                        {'label': 'O3 (ug/m3)', 'value': 'O3 (ug/m3)'},
                        {'label': 'PM10 (ug/m3)', 'value': 'PM10 (ug/m3)'},
                        {'label': 'PM25 (ug/m3)', 'value': 'PM25 (ug/m3)'},
                        {'label': 'SO2 (ug/m3)', 'value': 'SO2 (ug/m3)'},
                    ],
                    # value=['CO (mg/m3)', 'NO (ug/m3)', 'NO2 (ug/m3)', 'O3 (ug/m3)','PM10 (ug/m3)', 'PM25 (ug/m3)', 'SO2 (ug/m3)'],
                    multi=False,
                    style={'width': 200}
                ),

                html.Label('Seleccione una estación metereologica en el mapa.'),

                dcc.Graph(
                    id='cyl-map',
                    figure=fig_map,
                    style={'height': 700}
                ),
                # Estacion seleccionada...
                html.Div(id='selected-estacion'),

                html.H4(children='Resumen de datos disponibles en la estacion'),

                dcc.Graph(
                    id='table-datapoints'
                )

            ], className='six columns'),

        # Right column
        html.Div(
            [

                dcc.Graph(
                    id='time-series1',
                    style={'height': 400}
                ),

                html.Label('Agregar datos por...'),
                dcc.Dropdown(
                    id='aggregate-component',
                    options=[
                        {'label': 'Mes', 'value': 'month'},
                        {'label': 'Dia de la semana', 'value': 'dayofweek'},
                        #{'label': 'Hour', 'value': 'hour'},
                    ],
                    multi=False, value='month',style={'width': 200}
                ),
                html.H1(' '),
                dcc.Graph(
                    id='monthly-plot',
                    # figure = fig_time_series,
                    style={'height': 400}
                ),

                # generate_table(df)
                # Hidden div inside the app that stores the intermediate value
                html.Div(id='df_sel', style={'display': 'none'}),
                html.H1(' '),
                dcc.Markdown('''
                
Creado por [Javier Saez Gallego](http://jsaezgallego.com/en/). Para mas información contactar por email a <javiersaezgallego@gmail.com>.

Codigo disponible en [Github](https://github.com/jsga/Air_quality_CyL_dashboard).

Los datos han sido de la página web de [Datos Abiertos de Castilla y Leon](https://datosabiertos.jcyl.es/web/jcyl/set/es/medio-ambiente/calidad-aire-historico-horario/1284808467480).
''')

            ], className='six columns')
    ], className='row')


])


# ===== CALLBACK =========
# ========================


# retrieve selected estacion and return with text
@app.callback(
    Output(component_id='selected-estacion', component_property='children'),
    [dash.dependencies.Input('cyl-map', 'clickData')]
)
def update_selected_estacion(clickData):
    print(clickData)
    # If nothing is selected
    if clickData is None:
        return None

    sel_estacion = clickData['points'][0]['text']
    return 'Estacion seleccionada: ' + str(sel_estacion)


# Do the filtering inside a callback, more optimal than at each one.
# Problem: THe functons also need to be changed. Leave it for now.
# @app.callback(
#     Output('df_sel', 'children'),
#     [dash.dependencies.Input('cyl-map', 'clickData'),
#      dash.dependencies.Input('drop-component', 'value')]
# )
# def filter_df_estacion(clickData,value):
#
#     # If nothing is selected
#     if clickData is None:
#         return None
#
#     # Filter by selected estacion
#     sel_estacion = clickData['points'][0]['text']
#     df_sel = df[df['Estacion'] == sel_estacion]
#
#     # Select column by component
#     df_sel = df_sel[['Fecha', value]]
#
#     # Aggregate by week day
#     df_sel = df_sel.sort_values(by='Fecha')
#
#     # END
#     return df_sel


@app.callback(
    dash.dependencies.Output('time-series1', 'figure'),
    [dash.dependencies.Input('cyl-map', 'clickData'),
     dash.dependencies.Input('drop-component', 'value')])
def update_figure_ts1(clickData, value):
    # If None clicked
    if clickData is None or value is None:
        return empty_plot('Seleccione una estación en el mapa y un componente')

    # Get the estacion from clickData
    sel_estacion = clickData['points'][0]['text']
    print('The selected estacion is ' + str(sel_estacion))

    # Produce figure
    fig = plot_time_series(df, sel_estacion=str(sel_estacion), sel_comp=str(value))

    # END
    return fig


@app.callback(
    dash.dependencies.Output('monthly-plot', 'figure'),
    [dash.dependencies.Input('cyl-map', 'clickData'),
     dash.dependencies.Input('drop-component', 'value'),
     dash.dependencies.Input('aggregate-component', 'value')])
def update_figure_mp(clickData, value,period):
    # If None clicked
    if clickData is None or value is None:
        return empty_plot('Seleccione una estación en el mapa y un componente')

    # Get the estacion from clickData
    sel_estacion = clickData['points'][0]['text']

    # Produce figure
    fig = plot_average_aggregate(df, sel_estacion=str(sel_estacion), sel_comp=str(value),period=period)

    # END
    return fig



# Show number of datapoints when hover
@app.callback(Output('table-datapoints', 'figure'),
              [Input('cyl-map', 'clickData')])
def update_table(clickData):
    print(clickData)
    if clickData is None:
        sel_estacion = None
    else:
        # Get the estacion from clickData
        sel_estacion = clickData['points'][0]['text']
        print('estacion selected by hover: ' + str(sel_estacion))
    # Create table
    tab = table_number_dataopints(df, sel_estacion)

    return tab


# ===== END =========
# ===================

if __name__ == '__main__':
    app.run_server(debug=True)
