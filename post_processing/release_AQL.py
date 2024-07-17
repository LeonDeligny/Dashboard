"""
Module related to the different graphs in Post Processing > Release AQL.

Database name : hsma2.
Corresponding CSV file : pp_tracking.csv.
"""

import datetime

import dash_bootstrap_components as dbc, plotly.graph_objects as go, pandas as pd, numpy as np

from dash import html, dcc
from dash.dependencies import Input, Output

from pp_load import load_df_release_AQL
from generate_plots import generate_grouped_bar_plot, generate_bar_plot_no_hues
from filters import filter_dataframe, generate_title
from dicts import CustomCard, COLOR_DICT, WEEK_DICT
from utils import load_operator_label, load_equipment_label, extract_type

def register_release_AQL_callbacks(app):

    #############################################
    # 1st Graph : Release AQL: NOK by Type per week #
    #############################################

    @app.callback(
        [
        Output('Release AQL: NOK by Type per week', 'figure'),
        Output('Release AQL: NOK by Type per week (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 1', 'value'),
        Input('Week Selector 1', 'value'),
        Input('Operator Dropdown 1', 'value'),
        Input('Equipment Dropdown 1', 'value')
        ]
    )
    def Update_PP_Trier_Type_Week_Bar(selected_year, selected_week, selected_operator, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': selected_operator, 'Equipment': selected_equipment}
        title = generate_title(input_values, "Release AQL: NOK by Type per week")

        df_release_AQL = load_df_release_AQL(input_values)
        df_release_AQL_type = extract_type(df_release_AQL)

        filtered_df = filter_dataframe(df_release_AQL, input_values)
        filtered_df_type = filter_dataframe(df_release_AQL_type, input_values)

        df_Week = filtered_df_type.groupby(['Week', 'Type'])[['NOK by Type']].sum().reset_index()
        df_Week.sort_values(by=['Type'], inplace=True, ascending=False)
        df_Week.reset_index(drop=True, inplace=True)
        fig = generate_grouped_bar_plot(df_Week, 'Week', 'Type',title, 'Weeks', 'NOK by Type')
        week_start, week_end = selected_week
        all_weeks = np.arange(week_start, week_end+1)
        OK_Total = filtered_df.groupby('Week')['OK'].sum()
        NOK_Total = filtered_df.groupby('Week')['NOK'].sum()

        OK_Total = OK_Total.reindex(all_weeks, fill_value=1)
        NOK_Total = NOK_Total.reindex(all_weeks, fill_value=0)

        NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100

        team_ratio_df = pd.DataFrame({'Week': all_weeks, 'NOK (%)': NOK_Ratio.values})
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color=COLOR_DICT['NOK (%)'])))
        if NOK_Ratio.size > 0:
            ymax = 1.1* NOK_Ratio.values.max()
            fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', range=[0, ymax], overlaying='y', showgrid=False))
        else: fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False))
        return fig, fig

    #################################################
    # 2nd Graph : Release AQL: NOK by Type per Operator #
    #################################################

    @app.callback(
        [
        Output('Release AQL: NOK by Type per Operator', 'figure'),
        Output('Release AQL: NOK by Type per Operator (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 2', 'value'),
        Input('Week Selector 2', 'value'),
        Input('Operator Dropdown 2', 'value'),
        Input('Equipment Dropdown 2', 'value')
        ]
    )
    def Update_PP_Trier_Type_Operator_Bar(selected_year, selected_week, selected_operator, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': selected_operator, 'Equipment': selected_equipment}
        title = generate_title(input_values, "Release AQL: NOK by Type per Operator")

        df_release_AQL = load_df_release_AQL(input_values)
        df_release_AQL_type = extract_type(df_release_AQL)

        filtered_df = filter_dataframe(df_release_AQL, input_values)
        filtered_df_type = filter_dataframe(df_release_AQL_type, input_values)

        df_Operator = filtered_df_type.groupby(['Operator', 'Type'])[['NOK by Type']].sum().reset_index()
        all_weeks = filtered_df['Operator'].unique()
        OK_Total = filtered_df.groupby('Operator')['OK'].sum()
        NOK_Total = filtered_df.groupby('Operator')['NOK'].sum()

        OK_Total = OK_Total.reindex(all_weeks, fill_value=1)
        NOK_Total = NOK_Total.reindex(all_weeks, fill_value=0)
        NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100

        team_ratio_df = pd.DataFrame({'Operator': all_weeks, 'NOK (%)': NOK_Ratio.values})
        ofa_categories_ordered = team_ratio_df.sort_values('NOK (%)', ascending=False)['Operator']

        team_ratio_df['Operator'] = pd.Categorical(team_ratio_df['Operator'], categories=ofa_categories_ordered, ordered=True)
        team_ratio_df.sort_values(by='Operator', inplace=True)

        fig = generate_grouped_bar_plot(df_Operator, 'Operator', 'Type', title, 'Operators', 'NOK by Type')
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Operator'], y=team_ratio_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color=COLOR_DICT['NOK (%)'])))
        fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':team_ratio_df['Operator']})
        if NOK_Ratio.size > 0:
            ymax = 1.1* NOK_Ratio.values.max()
            fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', range=[0, ymax], overlaying='y', showgrid=False))
        else: fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False))
        return fig, fig

    #####################################################
    # 3rd Graph : Release AQL: NOK by Type per Collaborator #
    #####################################################

    @app.callback(
        [
        Output('Release AQL: NOK by Type per Collaborator', 'figure'),
        Output('Release AQL: NOK by Type per Collaborator (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 3', 'value'),
        Input('Week Selector 3', 'value'),
        Input('Equipment Dropdown 3', 'value')
        ]
    )
    def Update_PP_Trier_Type_Collaborator_Bar(selected_year, selected_week, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': selected_equipment}
        title = generate_title(input_values, "Release AQL: NOK by Type per Collaborator")

        df_release_AQL = load_df_release_AQL(input_values)
        df_release_AQL_type = extract_type(df_release_AQL)

        filtered_df = filter_dataframe(df_release_AQL, input_values)
        filtered_df_type = filter_dataframe(df_release_AQL_type, input_values)

        df_Collaborator = filtered_df_type.groupby(['Collaborator', 'Type'])[['NOK by Type']].sum().reset_index()

        all_weeks = filtered_df['Collaborator'].unique()
        OK_Total = filtered_df.groupby('Collaborator')['OK'].sum()
        NOK_Total = filtered_df.groupby('Collaborator')['NOK'].sum()

        OK_Total = OK_Total.reindex(all_weeks, fill_value=1)
        NOK_Total = NOK_Total.reindex(all_weeks, fill_value=0)
        NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100
        team_ratio_df = pd.DataFrame({'Collaborator': all_weeks, 'NOK (%)': NOK_Ratio.values})
        ofa_categories_ordered = team_ratio_df.sort_values('NOK (%)', ascending=False)['Collaborator']

        team_ratio_df['Collaborator'] = pd.Categorical(team_ratio_df['Collaborator'], categories=ofa_categories_ordered, ordered=True)
        team_ratio_df.sort_values(by='Collaborator', inplace=True)

        fig = generate_grouped_bar_plot(df_Collaborator, 'Collaborator', 'Type', title, 'Collaborators', 'NOK by Type')
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Collaborator'], y=team_ratio_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color=COLOR_DICT['NOK (%)'])))
        fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':team_ratio_df['Collaborator']})
        if NOK_Ratio.size > 0:
            ymax = 1.1* NOK_Ratio.values.max()
            fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', range=[0, ymax], overlaying='y', showgrid=False))
        else: fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False))
        return fig, fig

    ##################################################
    # 4th Graph : Release AQL: NOK by Type per Equipment #
    ##################################################

    @app.callback(
        [
        Output('Release AQL: NOK by Type per Equipment', 'figure'),
        Output('Release AQL: NOK by Type per Equipment (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 4', 'value'),
        Input('Week Selector 4', 'value'),
        Input('Equipment Dropdown 4', 'value'),
        Input('Operator Dropdown 4', 'value')
        ]
    )
    def Update_PP_Trier_Type_Equipment_Bar(selected_year, selected_week, selected_equipment, selected_operator):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': selected_equipment, 'Operator': selected_operator}
        title = generate_title(input_values, "Release AQL: NOK by Type per Equipment")

        df_release_AQL = load_df_release_AQL(input_values)
        df_release_AQL_type = extract_type(df_release_AQL)

        filtered_df = filter_dataframe(df_release_AQL, input_values)
        filtered_df_type = filter_dataframe(df_release_AQL_type, input_values)

        df_Equipment = filtered_df_type.groupby(['Equipment', 'Type'])[['NOK by Type']].sum().reset_index()
        all_weeks = filtered_df['Equipment'].unique()
        OK_Total = filtered_df.groupby('Equipment')['OK'].sum()
        NOK_Total = filtered_df.groupby('Equipment')['NOK'].sum()

        OK_Total = OK_Total.reindex(all_weeks, fill_value=1)
        NOK_Total = NOK_Total.reindex(all_weeks, fill_value=0)
        NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100

        team_ratio_df = pd.DataFrame({'Equipment': all_weeks, 'NOK (%)': NOK_Ratio.values})
        ofa_categories_ordered = team_ratio_df.sort_values('NOK (%)', ascending=False)['Equipment']

        team_ratio_df['Equipment'] = pd.Categorical(team_ratio_df['Equipment'], categories=ofa_categories_ordered, ordered=True)
        team_ratio_df.sort_values(by='Equipment', inplace=True)

        fig = generate_grouped_bar_plot(df_Equipment, 'Equipment', 'Type', title, 'Equipments', 'NOK by Type')
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Equipment'], y=team_ratio_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color=COLOR_DICT['NOK (%)'])))
        fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':team_ratio_df['Equipment']})
        if NOK_Ratio.size > 0:
            ymax = 1.1* NOK_Ratio.values.max()
            fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', range=[0, ymax], overlaying='y', showgrid=False))
        else: fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False))
        return fig, fig

    #########################################
    # 5th Graph : Release AQL: NOK per Type #
    #########################################

    @app.callback(
        [
        Output('Release AQL: NOK per Type', 'figure'),
        Output('Release AQL: NOK per Type (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 5', 'value'),
        Input('Week Selector 5', 'value'),
        Input('Equipment Dropdown 5', 'value'),
        ]
    )
    def update_5(selected_year, selected_week, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': selected_equipment}
        title = generate_title(input_values, "Release AQL: NOK per Type")
        
        df_dimensional = load_df_release_AQL(input_values)
        df_dimensional_type = extract_type(df_dimensional)

        filtered_df_type = filter_dataframe(df_dimensional_type, input_values)

        df_Equipment = filtered_df_type.groupby('Type')['NOK by Type'].sum().reset_index()
        df_Equipment = df_Equipment.sort_values(by='NOK by Type', ascending=False)  # Sort by decreasing value of NOK

        fig = generate_bar_plot_no_hues(df_Equipment, 'Type', title, 'Type', 'NOK by Type')
        
        return fig, fig

def release_AQL_layout(operator_show):
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

            #############################################
            # 1st Graph : Release AQL: NOK by Type per week #
            #############################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Release AQL: NOK by Type per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Release AQL: NOK by Type per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 1', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 1', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 1', options=operator_label, placeholder="All Operators", value='All')),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 1', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close1", className="ml-auto"))
                ], id="modal1", size="xl",),
            ], md=12),
                    
        ], className="mt-4"),
            
        dbc.Row([
            
            #################################################
            # 2nd Graph : Release AQL: NOK by Type per Operator #
            #################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Release AQL: NOK by Type per Operator', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Release AQL: NOK by Type per Operator (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 2', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 2', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 2', options=operator_label, placeholder="All Operators", value='All')),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 2', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close2", className="ml-auto")),
                ], id="modal2", size="xl"),
            ], md=6),

            #####################################################
            # 3rd Graph : Release AQL: NOK by Type per Collaborator #
            #####################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Release AQL: NOK by Type per Collaborator', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Release AQL: NOK by Type per Collaborator (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 3', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 3', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 3', options=operator_label, placeholder="All Operators", value='All')),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 3', options=equipment_label, placeholder="All Equipments", value = 'All')),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close3", className="ml-auto")),
                ], id="modal3", size="xl"),
            ], md=6),

        ], className="mt-4"),

        dbc.Row([

            ##################################################
            # 4th Graph : Release AQL: NOK by Type per Equipment #
            ##################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Release AQL: NOK by Type per Equipment', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open4", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Release AQL: NOK by Type per Equipment (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 4', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 4', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 4', options=operator_label, placeholder="All Operators", value='All')),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 4', options=equipment_label, placeholder="All Equipments", value = 'All')),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close4", className="ml-auto")),
                ], id="modal4", size="xl"),
            ], md=6),
            
            #########################################
            # 5th Graph : Release AQL: NOK per Type #
            #########################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Release AQL: NOK per Type', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open5", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Release AQL: NOK per Type (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 5', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 5', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 5', options=operator_label, placeholder="All Operators", value='All')),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 5', options=equipment_label, placeholder="All Equipments", value = 'All')),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close5", className="ml-auto")),
                ], id="modal5", size="xl"),
            ], md=6),
        ], className="mt-4"),
    ], className='main_div'),

    else:
        return html.Div(children=[

    html.Br(),
    html.P("Data comes from Intranet."),
    
    dbc.Row([               

        #############################################
        # 1st Graph : Release AQL: NOK by Type per week #
        #############################################

        dbc.Col([
            CustomCard([
                dbc.Col(dcc.Graph(id='Release AQL: NOK by Type per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                dbc.Button("Open filter options", id="open1", className="mr-2"),
                ]),
            dbc.Modal([
                dbc.ModalHeader("Filter Options"),
                dbc.ModalBody(
                    CustomCard([
                        dcc.Graph(id='Release AQL: NOK by Type per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                        html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 1', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                        dbc.Row([
                            dbc.Col(dcc.Dropdown(id='Year Dropdown 1', options=YEAR_LIST, value=current_year)),
                            dbc.Col(dcc.Dropdown(id='Operator Dropdown 1', options=operator_label, placeholder="All Operators", value='All'), style={'display': 'none'}),
                            dbc.Col(dcc.Dropdown(id='Equipment Dropdown 1', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                        ]),
                    ]),
                ),
                dbc.ModalFooter(dbc.Button("Close", id="close1", className="ml-auto"))
            ], id="modal1", size="xl",),
        ], md=12),
    
    ], className="mt-4"),

    dbc.Row([
        ##################################################
        # 4th Graph : Release AQL: NOK by Type per Equipment #
        ##################################################

        dbc.Col([
            CustomCard([
                dbc.Col(dcc.Graph(id='Release AQL: NOK by Type per Equipment', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                dbc.Button("Open filter options", id="open4", className="mr-2"),
            ]),
            dbc.Modal([
                dbc.ModalHeader("Filter Options"),
                dbc.ModalBody(
                    CustomCard([
                        dcc.Graph(id='Release AQL: NOK by Type per Equipment (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                        html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 4', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                        dbc.Row([
                            dbc.Col(dcc.Dropdown(id='Year Dropdown 4', options=YEAR_LIST, value=current_year)),
                            dbc.Col(dcc.Dropdown(id='Operator Dropdown 4', options=operator_label, placeholder="All Operators", value='All'), style={'display': 'none'}),
                            dbc.Col(dcc.Dropdown(id='Equipment Dropdown 4', options=equipment_label, placeholder="All Equipments", value = 'All')),
                        ]),
                    ]),
                ),
                dbc.ModalFooter(dbc.Button("Close", id="close4", className="ml-auto")),
            ], id="modal4", size="xl"),
        ], md=6),

        #########################################
        # 5th Graph : Release AQL: NOK per Type #
        #########################################

        dbc.Col([
            CustomCard([
                dbc.Col(dcc.Graph(id='Release AQL: NOK per Type', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                dbc.Button("Open filter options", id="open5", className="mr-2"),
            ]),
            dbc.Modal([
                dbc.ModalHeader("Filter Options"),
                dbc.ModalBody(
                    CustomCard([
                        dcc.Graph(id='Release AQL: NOK per Type (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                        html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 5', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                        dbc.Row([
                            dbc.Col(dcc.Dropdown(id='Year Dropdown 5', options=YEAR_LIST, value=current_year)),
                            dbc.Col(dcc.Dropdown(id='Operator Dropdown 5', options=operator_label, placeholder="All Operators", value='All'), style={'display': 'none'}),
                            dbc.Col(dcc.Dropdown(id='Equipment Dropdown 5', options=equipment_label, placeholder="All Equipments", value = 'All')),
                        ]),
                    ]),
                ),
                dbc.ModalFooter(dbc.Button("Close", id="close5", className="ml-auto")),
            ], id="modal5", size="xl"),
        ], md=6),
    ], className="mt-4"),
], className='main_div'),