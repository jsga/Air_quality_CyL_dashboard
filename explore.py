import pandas as pd
import numpy as np
import geopandas

import plotly
import plotly.plotly as py
import plotly.graph_objs as go



def prepare_data(file_path = 'data/Calidad_del_aire_-_datos_hist_ricos_diarios.csv',
                 provincias_path = 'data/provincias.json'):

    # Download data from portal
    # TODO

    df = pd.read_csv(file_path, sep=";",parse_dates = ['Fecha'] ,low_memory=False )

    df.columns.values[df.columns.values == 'Estación'] = 'Estacion'
    df.columns.values[df.columns.values == 'Posición'] = 'Posicion'
    #df.columns.values[df.columns.values == 'Posición de la estación'] = 'Posicion'
    #df.columns.values[df.columns.values == 'Hora'] = 'Fecha'

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
    provincias = geopandas.read_file(provincias_path)
    provincias = provincias.query(
        "name in ('Valladolid','Zamora','Salamanca','León','Soria','Palencia','Ávila','Segovia','Burgos')")

    return df, est, provincias



def create_map_plotly( est, provincias):
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
            text= est.index.values,
            hoverinfo='text',
            mode='markers',
            marker=dict(
                size=9
            )
        )
    ]

    layout = go.Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            layers=[
                dict(
                    sourcetype='geojson',
                    source='https://gist.githubusercontent.com/jsga/bde68149f50fb9a9cd399f3da7494260/raw/4cc48bf68f9f0324811c74d2ab4565d0bde1e643/castilla_y_leon.geojson',
                    type='fill',
                    color='rgba(255,204,204,0.2)'
                )
            ],
            bearing=0,
            center=dict(
                lat=41.6525246,
                lon=-4.7308742
            ),
            pitch=0,
            zoom=6,
            #style='dark'
        )
        #dragmode = 'lasso'
    )


    fig = dict(data=data, layout=layout)
    #plotly.offline.plot(fig)

    return fig




def empty_plot(label_annotation):
    '''
    Returns an empty plot with a text in the center of it
    This is used when no data is available
    '''

    trace1 = go.Scatter(
        x=[],
        y=[]
    )

    data = [trace1]

    layout = go.Layout(
        showlegend=False,
        xaxis=dict(
            autorange=True,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
        yaxis=dict(
            autorange=True,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
        annotations=[
            dict(
                x=0,
                y=0,
                xref='x',
                yref='y',
                text=label_annotation,
                showarrow=True,
                arrowhead=7,
                ax=0,
                ay=0
            )
        ]
    )

    fig = go.Figure(data=data, layout=layout)
    # END
    return fig


def plot_time_series(df,sel_estacion = 'VALLADOLID SUR',sel_comp = 'NO (ug/m3)'):
    """
    Return a time series plot of the selected component sel_comp for the selected estacion
    """

    # Filter by selected estacion
    df_sel = df[df['Estacion'] == sel_estacion]

    # Select column
    df_sel = df_sel[['Fecha',sel_comp]]

    # Check that values are actually selected or all are nan. return empty plot
    if df_sel.shape[0]==0 or df_sel.shape[1]==0 or ( df_sel.shape[0] - pd.isna(df_sel.iloc[:,1]).sum()) == 0:
        return empty_plot('No hay datos disponibles de ' + str(sel_comp) + '\npara la estacion de ' + str(sel_estacion) + '.\nPruebe con otra selección.')

    # Order by time
    df_sel = df_sel.sort_values(by='Fecha')

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
        title='Evolucion de ' + str(sel_comp) + ' a lo largo del tiempo',
        showlegend=False)

    fig = go.Figure(data=data, layout=layout)
    #plotly.offline.plot(fig)

    return fig


def table_number_dataopints(df,sel_estacion = 'VALLADOLID SUR'):
    """
    Creates a plotly table with summary information from the selected estacion
    If sel_estacion is None, then an empty table is generated
    """

    col_names = ['CO (mg/m3)', 'NO (ug/m3)', 'NO2 (ug/m3)', 'PM10 (ug/m3)', 'PM25 (ug/m3)']
    header = [ 'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']

    if sel_estacion is not None:
        # Filter by selected estacion
        df_sel = df[df['Estacion'] == sel_estacion]
        # Count
        df_summary = df_sel[col_names].describe()
    else:
        # Crete empty table
        df_summary = pd.DataFrame('', index=header, columns=col_names)

    # concat the row names, i.e. col_names above
    aux2 = np.c_[col_names, np.round(df_summary.T, 2)]

    # Create figure
    sc = 80
    col_w = [130, 100] + [sc for i in range(0,6)]
    trace = go.Table(
        columnwidth = col_w,
        header=dict(values= [''] + header ,
                    line=dict(color='#7D7F80'),
                    fill=dict(color='#a1c3d1'),
                    align=['left'] * (len(header)+1)),
        cells=dict(values=aux2.T,
                   line=dict(color='#7D7F80'),
                   fill=dict(color='#EDFAFF'),
                   align=['left'] * (len(header)+1),
                   height = 40))

    layout = dict(width=sum(col_w))#, height=700)
    data = [trace]
    fig = dict(data=data, layout=layout)
    #plotly.offline.plot(fig)

    return fig



def plot_average_aggregate(df,sel_estacion = 'VALLADOLID SUR',sel_comp = 'NO (ug/m3)',period="month"):
    """
    Return a time series figure with average values per month with error bars
    Inspired from here: https://plot.ly/python/continuous-error-bars/
    """

    # Filter by selected estacion
    df_sel = df[df['Estacion'] == sel_estacion]

    # Select column
    df_sel = df_sel[['Fecha',sel_comp]]
    df_sel = df_sel.sort_values(by='Fecha')

    # Aggregate by period
    if period == "month":
        df_sel['period'] = pd.DatetimeIndex(df_sel.Fecha).month
        names = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
             'Noviembre', 'Diciembre']

    elif period == 'dayofweek':
        df_sel['period'] = pd.DatetimeIndex(df_sel.Fecha).dayofweek
        names = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']

    else:
        return empty_plot('No hay datos disponibles de ' + str(sel_comp) + '\npara la estacion de ' + str(
            sel_estacion) + '.\nPruebe con otra selección.')

    # Aggregate or return empty plot
    try:
        df_agg = df_sel.groupby('period').agg(['std', 'mean'])[sel_comp]
    except ValueError:
        return empty_plot('No hay datos disponibles de ' + str(sel_comp) + '\npara la estacion de ' + str(
            sel_estacion) + '.\nPruebe con otra selección.')

    # Create figure
    upper_bound = go.Scatter(
        name='',
        x=names,
        y=df_agg['mean'] + df_agg['std'],
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty')

    trace = go.Scatter(
        name='Media',
        x=names,
        y=df_agg['mean'],
        mode='lines',
        line=dict(color='rgb(31, 119, 180)'),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty')

    lower_bound = go.Scatter(
        name='',
        x=names,
        y=df_agg['mean'] - df_agg['std'],
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines')

    # Trace order can be important
    # with continuous error bars
    data = [lower_bound, trace, upper_bound]

    layout = go.Layout(
        yaxis=dict(title='Month'),
        title='Concentracion media de ' + str(sel_comp) + ' en ' + str(sel_estacion),
        showlegend=False)

    fig = go.Figure(data=data, layout=layout)
    #plotly.offline.plot(fig)

    return fig








def show_table_avg(est,sel_estacion = 'VALLADOLID SUR'):
    """
    Returns a plotly table with info from the selected estacion
    """

    # Select estacion
    est_sel = est[est.index == sel_estacion]

    # Re-arrange the table
    est_sel.iloc[0,]
    pd.melt( est_sel[0,],id_vars='',value_vars=['count','mean','std','min','max'])

    header = ['CO (mg/m3)', 'NO (ug/m3)', 'NO2 (ug/m3)', 'PM10 (ug/m3)', 'PM25 (ug/m3)']

    pd.melt(est_sel.iloc[0,],id_vars = 'CO (mg/m3)', value_vars=header)

    dd = [est_sel['CO (mg/m3)'],
        est_sel['NO (ug/m3)'],
        est_sel['NO2 (ug/m3)'],
        #est_sel['O3 (ug/m3)']
        est_sel['PM10 (ug/m3)'],
        est_sel['PM25 (ug/m3)']]#,
        #est_sel['SO2 (ug/m3)']


    # Create table
    trace = go.Table(
        header=dict(values=est_sel.iloc[0,].T.index,
                    fill=dict(color='#C2D4FF'),
                    align=['left'] * 5),
        cells=dict(values = est_sel.iloc[0,].T,
                   fill=dict(color='#F5F8FF'),
                   align=['left'] * 5))

    data = [trace]
    plotly.offline.plot(data)



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
