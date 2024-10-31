"""
Module related to the different graphs in Post Processing > 0.

Database name : hsma2.
Corresponding CSV file : pp_tracking.csv.
"""

import datetime

import dash_bootstrap_components as dbc, plotly.graph_objects as go

from dash import html, dcc
from dash.dependencies import Input, Output

from smc_load import load_df_smc 
from pp_load import load_df_zero
from generate_plots import generate_custom_bar_plot
from filters import filter_dataframe, generate_title
from dicts import CustomCard, WEEK_DICT
from utils import load_operator_label, load_equipment_label, extract_type

FIRST_GRAPH = "0: NOK by Type per week"
SECOND_GRAPH = "0: NOK by Type per Collaborator"
THIRD_GRAPH = "0: NOK by Type per Operator"
FOURTH_GRAPH = "0: NOK by Type per Equipment"

def create_graph(input_values, title_name, hue):
    title = generate_title(input_values, title_name)

    df_zero = load_df_zero(input_values)
    df_zero_type = extract_type(df_zero)

    filtered_df_type = filter_dataframe(df_zero_type, input_values)

    df_Operator = filtered_df_type.groupby([hue, 'Type'])[['NOK by Type']].sum().reset_index()

    fig = generate_custom_bar_plot(df_Operator, hue, 'Type', title, hue + 's', 'NOK by Type')
    return fig 

def register_zero_callbacks(app):

    #######################################
    # 1st Graph : 0: NOK by Type per week #
    #######################################

    @app.callback(
        [
        Output(FIRST_GRAPH, 'figure'),
        Output(FIRST_GRAPH + ' (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 1', 'value'),
        Input('Week Selector 1', 'value'),
        Input('Operator Dropdown 1', 'value'),
        Input('Equipment Dropdown 1', 'value')
        ]
    )
    def update_1(selected_year, selected_week, selected_operator, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': selected_operator, 'Equipment': selected_equipment}
        title = generate_title(input_values, FIRST_GRAPH)

        df_zero = load_df_zero(input_values)
        df_zero_type = extract_type(df_zero)

        filtered_df_type = filter_dataframe(df_zero_type, input_values)

        df_Week = filtered_df_type.groupby(['Week', 'Type'])[['NOK by Type']].sum().reset_index()
        df_Week.sort_values(by=['Type'], inplace=True, ascending=False)
        df_Week.reset_index(drop=True, inplace=True)

        fig = generate_custom_bar_plot(df_Week, 'Week', 'Type', title, 'Weeks', 'NOK by Type')

        return fig, fig

    ###############################################
    # 2nd Graph : 0: NOK by Type per Collaborator #
    ###############################################

    @app.callback(
        [
        Output(SECOND_GRAPH, 'figure'),
        Output(SECOND_GRAPH + ' (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 2', 'value'),
        Input('Week Selector 2', 'value'),
        Input('Equipment Dropdown 2', 'value'),
        ]
    )
    def update_2(selected_year, selected_week, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': selected_equipment}
        fig = create_graph(input_values, SECOND_GRAPH, 'Collaborator')

        return fig, fig

    ###########################################
    # 3rd Graph : 0: NOK by Type per Operator #
    ###########################################

    @app.callback(
        [
        Output(THIRD_GRAPH, 'figure'),
        Output(THIRD_GRAPH + ' (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 3', 'value'),
        Input('Week Selector 3', 'value'),
        Input('Equipment Dropdown 3', 'value'),
        ]
    )
    def update_3(selected_year, selected_week, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': selected_equipment}
        fig = create_graph(input_values, THIRD_GRAPH, 'Operator')

        return fig, fig

    ############################################
    # 4th Graph : 0: NOK by Type per Equipment #
    ############################################

    @app.callback(
        [
        Output(FOURTH_GRAPH, 'figure'),
        Output(FOURTH_GRAPH + ' (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 4', 'value'),
        Input('Week Selector 4', 'value'),
        Input('Operator Dropdown 4', 'value'),
        ]
    )
    def update_4(selected_year, selected_week, selected_operator):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': selected_operator}
        fig = create_graph(input_values, FOURTH_GRAPH, 'Equipment')

        return fig, fig
    
def zero_layout(operator_show):
    current_year = datetime.datetime.now().year
    current_week = datetime.datetime.now().isocalendar()[1]
    operator_label, equipment_label = load_operator_label(), load_equipment_label()
    current_week_list = [max(current_week-6, 1), current_week] 
    # List of years from 2023 to the current year.
    YEAR_LIST = list(range(2023, datetime.datetime.now().year + 1))

    if operator_show:
        return html.Div(children=[

        html.Br(),
        html.P("Data comes from database1.db."),

        dbc.Row([               

            #######################################
            # 1st Graph : 0: NOK by Type per week #
            #######################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id=FIRST_GRAPH, clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id=FIRST_GRAPH + ' (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 1', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 1', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 1', options=operator_label, placeholder="All Operators", value='All')),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 1', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close1", className="ml-auto"))
                ], id="modal1", size="xl"),
            ], md=12),
        
        ], className="mt-4"),
            
        dbc.Row([
            
            ###########################################
            # 3rd Graph : 0: NOK by Type per Operator #
            ###########################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id=SECOND_GRAPH, clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id=SECOND_GRAPH + ' (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 3', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 3', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 3', options=equipment_label, placeholder="All Equipments", value = 'All')),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close3", className="ml-auto")),
                ], id="modal3", size="xl"),
            ], md=6),

            ###############################################
            # 2nd Graph : 0: NOK by Type per Collaborator #
            ###############################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id=THIRD_GRAPH, clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id=THIRD_GRAPH + ' (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 2', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 2', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 2', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close2", className="ml-auto")),
                ], id="modal2", size="xl"),
            ], md=6),

        ], className="mt-4"),
            
    dbc.Row([

            ############################################
            # 4th Graph : 0: NOK by Type per Equipment #
            ############################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id=FOURTH_GRAPH, clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open4", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id=FOURTH_GRAPH + ' (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 4', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 4', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 4', options=operator_label, placeholder="All Operators", value='All')),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close4", className="ml-auto")),
                ], id="modal4", size="xl"),
            ], md=6),

        ], className="mt-4"),

    ], className='main_div'),

    else:
        return html.Div(children=[

        html.Br(),
        html.P("Data comes from database1.db."),

        dbc.Row([               

            #######################################
            # 1st Graph : 0: NOK by Type per week #
            #######################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id=FIRST_GRAPH, clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id=FIRST_GRAPH + ' (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 1', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 1', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 1', options=operator_label, placeholder="All Operators", value='All'), style={'display': 'none'}),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 1', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close1", className="ml-auto"))
                ], id="modal1", size="xl"),
            ], md=12),
        
        ], className="mt-4"),
            
        dbc.Row([

            ############################################
            # 4th Graph : 0: NOK by Type per Equipment #
            ############################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id=FOURTH_GRAPH, clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open4", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id=FOURTH_GRAPH + ' (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 4', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 4', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 4', options=operator_label, placeholder="All Operators", value='All'), style={'display': 'none'}),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close4", className="ml-auto")),
                ], id="modal4", size="xl"),
            ], md=6),
        ], className="mt-4"),
    ], className='main_div'),
