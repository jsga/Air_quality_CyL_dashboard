import dash_html_components as html
import dash_core_components as dcc

def Header():
    return html.Div([
        get_logo(),
        get_header(),
        html.Br([]),
        get_menu()
    ])

def get_logo():
    logo = html.Div([

        html.Div([
            html.Img(src='https://www.coal.es/wp-content/uploads/2018/08/jcyl.jpg', height='80', width='160')
        ], className="ten columns padded"),

        # html.Div([
        #     dcc.Link('Full View   ', href='/dash-vanguard-report/full-view')
        # ], className="two columns page-view no-print")

    ], className="row gs-header")
    return logo


def get_header():
    header = html.Div([

        html.Div([
            html.H5(
                'Calidad del aire en Castilla y Leon')
        ], className="twelve columns padded")

    ], className="row gs-header gs-text-header")
    return header


def get_menu():
    menu = html.Div([

        dcc.Link('Principal   ', href='/calidad_aire_cyl/principal', className="tab first"),

        dcc.Link('Sobre algo mas   ', href='/calidad_aire_cyl/algo', className="tab")

    ], className="row ")
    return menu