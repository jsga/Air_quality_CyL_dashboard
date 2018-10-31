import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from explore import prepare_data, create_map_plotly, plot_time_series,plot_average_monthly

import json
from textwrap import dedent as d



#===== INITIALIZE =========
#==========================

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )



markdown_text = '''
### Calidad del aire en Castilla y Leon

Haz click en una de las estaciones para seleccionar una.

'''

# Load data
df, est, provincias = prepare_data()

# Initialize map
fig_map = create_map_plotly(est, provincias)

# Launch app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



#===== LAYOUT ===========
#========================


app.layout = html.Div(children=[

    #html.Label('Seleccione provincia'),
    # dcc.Dropdown(
    #     options=[
    #         {'label': 'Valladolid', 'value': 'Valladolid'},
    #         {'label': 'Zamora', 'value': 'Zamora'},
    #         {'label': 'Salamanca', 'value': 'Salamanca'},
    #         {'label': 'León', 'value': 'León'},
    #         {'label': 'Soria', 'value': 'Soria'},
    #         {'label': 'Palencia', 'value': 'Palencia'},
    #         {'label': 'Ávila', 'value': 'Ávila'},
    #         {'label': 'Segovia', 'value': 'Segovia'},
    #         {'label': 'Burgos', 'value': 'Burgos'},
    #     ],
    #     value=['Valladolid','Zamora','Salamanca','León','Soria','Palencia','Ávila','Segovia','Burgos'],
    #     multi=True
    # ),

    html.Div([
            dcc.Markdown(children=markdown_text)
        ]),

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
            value=['CO (mg/m3)', 'NO (ug/m3)', 'NO2 (ug/m3)', 'O3 (ug/m3)','PM10 (ug/m3)', 'PM25 (ug/m3)', 'SO2 (ug/m3)'],
            multi=False
        ),

    dcc.Graph(
        id='cyl-map',
        figure = fig_map,
        style={'height': 700}
    ),


    html.Div([
        dcc.Markdown(d("""
                **Click Data**

                Click on points in the graph.
            """)),
        html.Pre(id='click-data'),
    ], className='three columns'),

    dcc.Graph(
        id='time-series1',
        #figure = fig_time_series,
        style={'height': 400}
    ),

    dcc.Graph(
        id='monthly-plot',
        #figure = fig_time_series,
        style={'height': 400}
    )

    #generate_table(df)

], style={'columnCount': 2})


#===== CALLBACK =========
#========================

@app.callback(
    Output('click-data', 'children'),
    [Input('cyl-map', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


@app.callback(
    dash.dependencies.Output('time-series1', 'figure'),
    [dash.dependencies.Input('cyl-map', 'clickData'),
     dash.dependencies.Input('drop-component', 'value')])
def update_figure(clickData,value):

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
     dash.dependencies.Input('drop-component', 'value')])
def update_figure(clickData,value):

    # Get the estacion from clickData
    sel_estacion = clickData['points'][0]['text']

    # Produce figure
    fig = plot_average_monthly(df, sel_estacion=str(sel_estacion), sel_comp=str(value))

    # END
    return fig




#===== END =========
#===================

if __name__ == '__main__':
    app.run_server(debug=True)
