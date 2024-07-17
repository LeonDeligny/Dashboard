import warnings

import dash, dash_bootstrap_components as dbc

from dash import dcc, html
from dash.dependencies import Input, Output, State
from homepage.homepage_layout import home_layout
from micro_machining.micro_machining_layout import register_micro_machining_layout_callbacks, micro_machining_layout
from post_processing.post_processing_layout import register_post_processing_layout_callbacks, post_processing_layout
from overall_scrap.overall_scrap_layout import overall_scrap_layout_callbacks, overall_scrap_layout

warnings.filterwarnings('ignore')

app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True, 
    external_stylesheets=[
        dbc.themes.FLATLY, 
        dbc.themes.BOOTSTRAP, 
        dbc.icons.BOOTSTRAP, 
        '/assets/bootstrap.min.css', 
        '/assets/styles.css'
        ]
    )

# Collapse Button of Dashboard
@app.callback(
    Output("collapse", "is_open"),
    [
    Input("collapse-button", "n_clicks")
    ],
    [
    State("collapse", "is_open")
    ],
)
def toggle_nav(n, is_open):
    if n:
        return not is_open
    return is_open

# Filter Option 1 of Dashboard
@app.callback(
    Output("modal1", "is_open"),
    [
    Input("open1", "n_clicks"), 
    Input("close1", "n_clicks")
    ],
    [
    State("modal1", "is_open")
    ],
)
def toggle_modal1(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Filter Option 2 of Dashboard
@app.callback(
    Output("modal2", "is_open"),
    [
    Input("open2", "n_clicks"), 
    Input("close2", "n_clicks")
    ],
    [
    State("modal2", "is_open")
    ],
)
def toggle_modal2(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Filter Option 3 of Dashboard
@app.callback(
    Output("modal3", "is_open"),
    [
    Input("open3", "n_clicks"),
    Input("close3", "n_clicks")
    ],
    [
    State("modal3", "is_open")
    ],
)   
def toggle_modal3(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Filter Option 4 of Dashboard
@app.callback(
    Output("modal4", "is_open"),
    [
    Input("open4", "n_clicks"), 
    Input("close4", "n_clicks")
    ],
    [
    State("modal4", "is_open")
    ],
)
def toggle_modal4(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Filter Option 5 of Dashboard
@app.callback(
    Output("modal5", "is_open"),
    [
    Input("open5", "n_clicks"), 
    Input("close5", "n_clicks")
    ],
    [
    State("modal5", "is_open")
    ],
)
def toggle_modal5(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Filter Option 6 of Dashboard
@app.callback(
    Output("modal6", "is_open"),
    [
    Input("open6", "n_clicks"), 
    Input("close6", "n_clicks")
    ],
    [
    State("modal6", "is_open")
    ],
)
def toggle_modal7(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Filter Option 7 of Dashboard
@app.callback(
    Output("modal7", "is_open"),
    [
    Input("open7", "n_clicks"), 
    Input("close7", "n_clicks")
    ],
    [
    State("modal7", "is_open")
    ],
)
def toggle_modal7(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

app.layout = html.Div([ 
        dcc.Location(id="url"),
        html.Div(id='dynamic-layout'),
    ])

@app.callback(
    Output('dynamic-layout', 'children'),
    Input('url', 'search')
)
def update_layout(search):
    if search != '?admin':
        return html.Div([ 
        html.Div(className='hover-trigger'),
        
        # Sidebar
        html.Div(id="sidebar", className="sidebar", children=[
            html.H2("Q-Dot Scrap Data", className='my-4'),
            html.Hr(),
            dbc.Nav([ 
                # Home Page Button
                dbc.NavLink("Home Page", href="/", active="exact"),

                # Scraps Button
                dbc.NavLink("Scraps", id="collapse-button", className="mb-3"),

                dbc.Collapse(dbc.Nav([
                    # Micro-Machining Access
                    dbc.NavLink("Micro-Machining", href="/mu", active="exact"),

                    # Post-Processing Access
                    dbc.NavLink("Post Processing", href="/pp", active="exact"),

                    # Global Scraps Access
                    dbc.NavLink("Global", href="/os", active="exact"),

                ]), id="collapse", is_open=False),
            ], vertical=True, pills=True),
        ]),

        html.Div(id="page-content", style={"padding": "2rem 1rem"}),
    ])
    else:
        return html.Div([ 
        html.Div(className='hover-trigger'),
        
        # Sidebar
        html.Div(id="sidebar", className="sidebar", children=[
            html.H2("Q-Dot Scrap Data", className='my-4'),
            html.Hr(),
            dbc.Nav([ 
                # Home Page Button
                dbc.NavLink("Home Page", href="/", active="exact"),

                # Scraps Button
                dbc.NavLink("Scraps", id="collapse-button", className="mb-3"),

                dbc.Collapse(dbc.Nav([
                    # Micro-Machining Access
                    dbc.NavLink("Micro-Machining", href="/mu?admin", active="exact"),

                    # Post-Processing Access
                    dbc.NavLink("Post Processing", href="/pp?admin", active="exact"),

                    # Global Scraps Access
                    dbc.NavLink("Global", href="/os?admin", active="exact"),

                ]), id="collapse", is_open=False),
            ], vertical=True, pills=True),
        ]),

        html.Div(id="page-content", style={"padding": "2rem 1rem"}),
    ])


register_micro_machining_layout_callbacks(app)
register_post_processing_layout_callbacks(app)
overall_scrap_layout_callbacks(app)

@app.callback(
    Output('page-content', 'children'),
    [
    Input('url', 'pathname'),
    Input('url', 'search')
    ]
)
def render_page_content(pathname, search):
    if pathname in ["/", "/ho"]:
        return home_layout()
    elif (pathname == "/mu") and (search  == "?admin"):
        return micro_machining_layout(operator_show = True)
    elif (pathname == "/os") and (search  == "?admin"):
        return overall_scrap_layout(operator_show = True)
    elif pathname == "/mu":
        return micro_machining_layout(operator_show = False)
    elif pathname == "/pp":
        return post_processing_layout()
    elif pathname == "/os":
        return overall_scrap_layout(operator_show = False)
    else:
        return html.Div([
            html.H3("404 Error: Page not found"),
            html.P(f"The requested path '{pathname}' is not a valid page."),
            html.P(f"Query parameters: {search}"),
        ])

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=8180) # app.run(debug=True, host="172.30.45.67", port=8180)