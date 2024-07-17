"""
Module related to the different graphs in Post Processing > Pre-Deburring.

Database name : hsma2.
Corresponding CSV file : pp_tracking.csv.
"""

import datetime

import dash_bootstrap_components as dbc, plotly.graph_objects as go

from dash import html, dcc
from dash.dependencies import Input, Output

from smc_load import load_df_smc 
from pp_load import load_df_pre_deburring
from generate_plots import generate_custom_bar_plot
from filters import filter_dataframe, generate_title
from dicts import CustomCard, WEEK_DICT
from utils import load_operator_label, load_equipment_label, extract_type

def register_pre_deburring_callbacks(app):

    ###############################################
    # 1st Graph : Pre-Deburring: NOK by Type per week #
    ###############################################

    @app.callback(
        [
        Output('Pre-Deburring: NOK by Type per week', 'figure'),
        Output('Pre-Deburring: NOK by Type per week (bis)', 'figure')
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
        title = generate_title(input_values, "Pre-Deburring: NOK by Type per week")

        df_ebavurage = load_df_pre_deburring(input_values)
        df_ebavurage_type = extract_type(df_ebavurage)

        filtered_df_type = filter_dataframe(df_ebavurage_type, input_values)

        df_Week = filtered_df_type.groupby(['Week', 'Type'])[['NOK by Type']].sum().reset_index()
        df_Week.sort_values(by=['Type'], inplace=True, ascending=False)
        df_Week.reset_index(drop=True, inplace=True)

        fig = generate_custom_bar_plot(df_Week, 'Week', 'Type', title, 'Weeks', 'NOK by Type')

        return fig, fig

    
    ###########################################################
    # 2nd Graph : Pre-Deburring: NOK by Type per Collaborator #
    ###########################################################

    @app.callback(
        [
        Output('Pre-Deburring: NOK by Type per Collaborator', 'figure'),
        Output('Pre-Deburring: NOK by Type per Collaborator (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 2', 'value'),
        Input('Week Selector 2', 'value'),
        Input('Equipment Dropdown 2', 'value'),
        ]
    )
    def update_2(selected_year, selected_week, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': selected_equipment}
        title = generate_title(input_values, "Pre-Deburring: NOK by Type per Collaborator")

        df_ebavurage = load_df_pre_deburring(input_values)
        df_ebavurage_type = extract_type(df_ebavurage)

        filtered_df_type = filter_dataframe(df_ebavurage_type, input_values)

        df_Collaborator = filtered_df_type.groupby(['Collaborator', 'Type'])[['NOK by Type']].sum().reset_index()

        fig = generate_custom_bar_plot(df_Collaborator, 'Collaborator', 'Type', title, 'Collaborators', 'NOK by Type')

        return fig, fig

    ###################################################
    # 3rd Graph : Pre-Deburring: NOK by Type per Operator #
    ###################################################

    @app.callback(
        [
        Output('Pre-Deburring: NOK by Type per Operator', 'figure'),
        Output('Pre-Deburring: NOK by Type per Operator (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 3', 'value'),
        Input('Week Selector 3', 'value'),
        Input('Equipment Dropdown 3', 'value'),
        ]
    )
    def update_3(selected_year, selected_week, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': selected_equipment}
        title = generate_title(input_values, "Pre-Deburring: NOK by Type per Operator")

        df_ebavurage = load_df_pre_deburring(input_values)
        df_ebavurage_type = extract_type(df_ebavurage)

        filtered_df_type = filter_dataframe(df_ebavurage_type, input_values)

        df_Operator = filtered_df_type.groupby(['Operator', 'Type'])[['NOK by Type']].sum().reset_index()

        fig = generate_custom_bar_plot(df_Operator, 'Operator', 'Type', title, 'Operators', 'NOK by Type')

        return fig, fig

    ########################################################
    # 4th Graph : Pre-Deburring: NOK by Type per Equipment #
    ########################################################

    @app.callback(
        [
        Output('Pre-Deburring: NOK by Type per Equipment', 'figure'),
        Output('Pre-Deburring: NOK by Type per Equipment (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 4', 'value'),
        Input('Week Selector 4', 'value'),
        Input('Operator Dropdown 4', 'value'),
        ]
    )
    def update_4(selected_year, selected_week, selected_operator):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': selected_operator}
        title = generate_title(input_values, "Pre-Deburring: NOK by Type per Equipment")

        df_ebavurage = load_df_pre_deburring(input_values)
        df_ebavurage_type = extract_type(df_ebavurage)

        filtered_df_type = filter_dataframe(df_ebavurage_type, input_values)

        df_Equipment = filtered_df_type.groupby(['Equipment', 'Type'])[['NOK by Type']].sum().reset_index()

        fig = generate_custom_bar_plot(df_Equipment, 'Equipment', 'Type', title, 'Equipments', 'NOK by Type')

        return fig, fig

    #######################################################
    # 5th Graph : Pre-Deburring: Repartition of Deburring #
    #######################################################

    @app.callback(
        [
        Output('Pre-Deburring: Repartition of Deburring', 'figure'),
        Output('Pre-Deburring: Repartition of Deburring (bis)', 'figure'),
        ],
        [
        Input('Year Dropdown 5', 'value'),
        Input('Week Selector 5', 'value'),
        Input('Equipment Dropdown 5', 'value'),
        ]
    )
    def update_5(selected_year, selected_week, equipment_value):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': equipment_value}
        title = generate_title(input_values, "Pre-Deburring: % of OFAs that needed Deburring")

        df_ebavurage = load_df_pre_deburring(input_values)
        df_smc = load_df_smc(input_values)

        filtered_df = filter_dataframe(df_ebavurage, input_values)
        
        ebavurage_present = filtered_df['Type'].apply(lambda x: isinstance(x, dict) and x.get('Ébavurage') == 1)
        
        ofa_ebavurage = filtered_df[ebavurage_present]['OFA'].nunique()
        ofa_non_ebavurage = filtered_df[~ebavurage_present]['OFA'].nunique()
        
        ebavurage_ofas = filtered_df[ebavurage_present]['OFA'].unique()
        df_smc_filtered = df_smc[df_smc['OFA'].isin(ebavurage_ofas)]
        
        ok_count = df_smc_filtered['OK'].sum()
        nok_count = df_smc_filtered['NOK'].sum()
        pcs_count = ok_count + nok_count
        
        fig = go.Figure(data=[go.Pie(labels=['Needs Deburring', 'Does Not'], values=[ofa_ebavurage, ofa_non_ebavurage], hole=.3)])
        
        annotations = [dict(x=0.1, y=-0.1, xref='paper', yref='paper', text=f'Total Parts that needed Deburring: {pcs_count}.', showarrow=False)]
        fig.update_layout(height=400, title_text='<b>' + title + '</b>', annotations=annotations)

        return fig, fig
    
    ####################################################
    # 6th Graph : Pre-Deburring: Repartition of Funnel #
    ####################################################

    @app.callback(
        [
        Output('Pre-Deburring: Repartition of Funnel', 'figure'),
        Output('Pre-Deburring: Repartition of Funnel (bis)', 'figure'),
        ],
        [
        Input('Year Dropdown 6', 'value'),
        Input('Week Selector 6', 'value'),
        Input('Equipment Dropdown 6', 'value'),
        ]
    )
    def update_6(selected_year, selected_week, equipment_value):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': equipment_value}
        title = generate_title(input_values, "Pre-Deburring: % of OFAs that returned to Op 10")

        df_ebavurage = load_df_pre_deburring(input_values)
        df_smc = load_df_smc(input_values)

        filtered_df = filter_dataframe(df_ebavurage, input_values)

        ebavurage_present = filtered_df['Type'].apply(lambda x: isinstance(x, dict) and x.get('Cheminée') == 1)
        
        ofa_ebavurage = filtered_df[ebavurage_present]['OFA'].nunique()
        ofa_non_ebavurage = filtered_df[~ebavurage_present]['OFA'].nunique()
        
        ebavurage_ofas = filtered_df[ebavurage_present]['OFA'].unique()
        df_smc_filtered = df_smc[df_smc['OFA'].isin(ebavurage_ofas)]
        
        ok_count = df_smc_filtered['OK'].sum()
        nok_count = df_smc_filtered['NOK'].sum()
        pcs_count = ok_count + nok_count

        fig = go.Figure(data=[go.Pie(labels=['Returns to Milling Operation', 'Does Not'], values=[ofa_ebavurage, ofa_non_ebavurage], hole=.3)])

        annotations = [dict(x=0.1, y=-0.1, xref='paper', yref='paper', text=f'Total Parts that returned to Milling Operation: {pcs_count}.', showarrow=False)]
        fig.update_layout(height=400, title_text='<b>' + title + '</b>', annotations=annotations)

        return fig, fig

    
def pre_deburring_layout(operator_show):
    current_year = datetime.datetime.now().year
    current_week = datetime.datetime.now().isocalendar()[1]
    operator_label, equipment_label = load_operator_label(), load_equipment_label()
    current_week_list = [max(current_week-6, 1), current_week] 
    # List of years from 2023 to the current year.
    YEAR_LIST = list(range(2023, datetime.datetime.now().year + 1))

    if operator_show:
        return html.Div(children=[

        html.Br(),
        html.P("Data comes from Intranet."),

        dbc.Row([               

            ###############################################
            # 1st Graph : Pre-Deburring: NOK by Type per week #
            ###############################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Pre-Deburring: NOK by Type per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Pre-Deburring: NOK by Type per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
            
            ###################################################
            # 3rd Graph : Pre-Deburring: NOK by Type per Operator #
            ###################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Pre-Deburring: NOK by Type per Operator', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Pre-Deburring: NOK by Type per Operator (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
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

            ###########################################################
            # 2nd Graph : Pre-Deburring: NOK by Type per Collaborator #
            ###########################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Pre-Deburring: NOK by Type per Collaborator', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Pre-Deburring: NOK by Type per Collaborator (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
            
            #######################################################
            # 5th Graph : Pre-Deburring: Repartition of Deburring #
            #######################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Pre-Deburring: Repartition of Deburring', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open5", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Pre-Deburring: Repartition of Deburring (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 5', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 5', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 5', options=equipment_label, placeholder="All Equipments", value = 'All')),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close5", className="ml-auto")),
                ], id="modal5", size="xl"),
            ], md=6),
            ####################################################
            # 5th Graph : Pre-Deburring: Repartition of Funnel #
            ####################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Pre-Deburring: Repartition of Funnel', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open6", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Pre-Deburring: Repartition of Funnel (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 6', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 6', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 6', options=equipment_label, placeholder="All Equipments", value = 'All')),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close6", className="ml-auto")),
                ], id="modal6", size="xl"),
            ], md=6),
        ], className="mt-4"),

    dbc.Row([
            ########################################################
            # 4th Graph : Pre-Deburring: NOK by Type per Equipment #
            ########################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Pre-Deburring: NOK by Type per Equipment', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open4", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Pre-Deburring: NOK by Type per Equipment (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
        html.P("Data comes from Intranet."),

        dbc.Row([               

            ###############################################
            # 1st Graph : Pre-Deburring: NOK by Type per week #
            ###############################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Pre-Deburring: NOK by Type per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Pre-Deburring: NOK by Type per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
            
            #######################################################
            # 5th Graph : Pre-Deburring: Repartition of Deburring #
            #######################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Pre-Deburring: Repartition of Deburring', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open5", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Pre-Deburring: Repartition of Deburring (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 5', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 5', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 5', options=equipment_label, placeholder="All Equipments", value = 'All')),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close5", className="ml-auto")),
                ], id="modal5", size="xl"),
            ], md=6),
            ####################################################
            # 5th Graph : Pre-Deburring: Repartition of Funnel #
            ####################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Pre-Deburring: Repartition of Funnel', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open6", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Pre-Deburring: Repartition of Funnel (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 6', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 6', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 6', options=equipment_label, placeholder="All Equipments", value = 'All')),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close6", className="ml-auto")),
                ], id="modal6", size="xl"),
            ], md=6),
        ], className="mt-4"),

        dbc.Row([

            ########################################################
            # 4th Graph : Pre-Deburring: NOK by Type per Equipment #
            ########################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Pre-Deburring: NOK by Type per Equipment', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open4", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Pre-Deburring: NOK by Type per Equipment (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
