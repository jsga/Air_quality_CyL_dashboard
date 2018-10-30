import pandas as pd
import folium
import geopandas

import plotly
import plotly.plotly as py
import plotly.graph_objs as go



def prepare_data():

    # Download data from portal
    # Clean and prepare into a pandas dataFrame
    df = pd.read_csv('data/Calidad_del_aire_-_datos_hist_ricos_diarios.csv',
                     sep=";",
                     low_memory=False)
    df.columns.values[9] = 'Estacion'
    df.columns.values[10] = 'Posicion'

    # Transform posicion in array of lat and lon
    pattern_all = '\((\d+\.{1}\d+),\s(-?\d+\.{1}\d+)\)'
    pattern_lat = '\((\d+\.{1}\d+),\s-?\d+\.{1}\d+\)'
    pattern_lon = '\(\d+\.{1}\d+,\s(-?\d+\.{1}\d+)\)'
    df['lat'] = df['Posicion'].str.extract(pattern_lat).astype(float)
    df['lon'] = df['Posicion'].str.extract(pattern_lon).astype(float)

    # Create small dataframe with info from Estacion
    print('There is a total of ' + str(df['Estacion'].nunique()) + ' met stations\n')
    est = df.groupby('Estacion').agg(['count', 'min', 'max', 'std', 'mean'])

    # Load boundaries of provinces
    provincias = geopandas.read_file('data/provincias.json')
    provincias = provincias.query(
        "name in ('Valladolid','Zamora','Salamanca','León','Soria','Palencia','Ávila','Segovia','Burgos')")

    return df, est, provincias



def create_map_plotly(df, est, provincias):
    """
    Creates a plotly map of CyL
    TODO: filter by Estacion and return plotly map

    """
    #df, est, provincias = prepare_data()

    mapbox_access_token = 'pk.eyJ1IjoiamFzYWdhIiwiYSI6ImNqbnVqbGZiNDB4MGkzd3M1bXRzZ2Y5OHQifQ._dftJIOLzL_sLNAWrZbCNA'


    data = [
        go.Scattermapbox(
            lat=est['lat']['mean'],
            lon=est['lon']['mean'],
            mode='markers',
            marker=dict(
                size=9
            ),
            text=est.index.values,
        )
    ]

    layout = go.Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            # layers=[ # TODO: Give a color to Castilla y leon
            #     dict(
            #         sourcetype='geojson',
            #         source=provincias.to_json(),
            #         type='fill',
            #         color='rgba(40,0,113,0.8)'
            #     )
            # ],
            bearing=0,
            center=dict(
                lat=41.6525246,
                lon=-4.7308742
            ),
            pitch=0,
            zoom=7#,
            #style='dark'
        ),
    )

    fig = dict(data=data, layout=layout)
    #plotly.offline.plot(fig)

    return fig



def plot_time_series(df,sel_estacion = 'VALLADOLID SUR',sel_comp = 'NO (ug/m3)'):
    """
    Return a time series plot of the selected component sel_comp for the selected estacion
    """

    # Filter by selected estacion
    df_sel = df[df['Estacion'] == sel_estacion]

    # Select column
    df_sel = df_sel[['Fecha',sel_comp]]

    # TODO: Check that values are actually selected

    # Make time series plot
    data = [go.Scatter(
        name=sel_comp,
        x=df_sel['Fecha'],
        y=df_sel[sel_comp],
        mode='lines',
        #marker=dict(color="#444"),
        #line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)')]

    layout = go.Layout(
        yaxis=dict(title=sel_comp),
        title='Evolution of ' + str(sel_comp) + ' over time',
        showlegend=False)

    fig = go.Figure(data=data, layout=layout)
    #plotly.offline.plot(fig)

    return fig


def plot_average_daily(df,sel_estacion = 'VALLADOLID SUR',sel_comp = 'NO (ug/m3)'):
    """
    Return a time series figure with average values per hour with error bars
    Inspired from here: https://plot.ly/python/continuous-error-bars/
    """

    # Filter by selected estacion
    df_sel = df[df['Estacion'] == sel_estacion]

    # Select column
    df_sel = df_sel[['Fecha',sel_comp]]

    # TODO: Check that values are actually selected

    # aggregate by hour. Calculate mean and sd


    # Create figure
    upper_bound = go.Scatter(
        name='Upper Bound',
        x=df_sel['Time'],
        y=df_sel['10 Min Sampled Avg'] + df_sel['10 Min Std Dev'],
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty')

    trace = go.Scatter(
        name='Measurement',
        x=df['Time'],
        y=df['10 Min Sampled Avg'],
        mode='lines',
        line=dict(color='rgb(31, 119, 180)'),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty')

    lower_bound = go.Scatter(
        name='Lower Bound',
        x=df_sel['Time'],
        y=df_sel['10 Min Sampled Avg'] - df_sel['10 Min Std Dev'],
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines')

    # Trace order can be important
    # with continuous error bars
    data = [lower_bound, trace, upper_bound]

    layout = go.Layout(
        yaxis=dict(title='Wind speed (m/s)'),
        title='Continuous, variable value error bars.<br>Notice the hover text!',
        showlegend=False)

    fig = go.Figure(data=data, layout=layout)

    return fig



def create_map_folium():
    """
    Returns a folium map.
    """

    df, est, provincias = prepare_data()

    # Work here on the map. Show the events in a map with some info on top
    m = folium.Map(location=[41.6525246,-4.7308742], tiles='Stamen Toner',
                       zoom_start=8, control_scale=True)

    # Add a marker for each event
    for index, row in est.iterrows():
        m.add_child(folium.Marker(location=[row['lat']['mean'],row['lon']['mean']],
            popup=(folium.Popup(index))))#,icon=folium.Icon(color=color(elev),icon_color='green')))


    # Add boundaries of CyL
    m.choropleth(privinciastxt,fill_color='YlOrRd', fill_opacity=0.3, line_opacity=0.2,line_color='white', line_weight=1,
                 highlight=True, smooth_factor=1.0)


    # Save the map
    #m.save("/Users/jsg/Documents/Agenda_cultural/base_map2.html")

    return m
