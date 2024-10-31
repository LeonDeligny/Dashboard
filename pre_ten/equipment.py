"""
Module related to the different graphs in pre-Ten > Equipment.
"""
import calendar, datetime

import dash_bootstrap_components as dbc, plotly.graph_objects as go, pandas as pd

from dash import html, dcc
from dash.dependencies import Input, Output

from smc_load import load_df_smc
from generate_plots import generate_grouped_bar_plot
from filters import filter_dataframe, generate_title
from dicts import CustomCard, WEEK_DICT, EQUIPMENTS_PER_OPERATOR_LIST, EQUIPMENTS_PER_OPERATOR_LABEL_LIST, SHIFT_LABEL_LIST, WEEKDAY_LABEL_LIST
from utils import load_operator_label, load_equipment_label, extract_type_smc

FIRST_GRAPH = "Ten: NOK by Type per Equipment"

def register_equipment_callbacks(app):

    ##############################################
    # 1st Graph : Ten: NOK by Type per Equipment #
    ##############################################

    @app.callback(
        [
        Output(FIRST_GRAPH, 'figure'),
        Output(FIRST_GRAPH + ' (bis)', 'figure'),
        ],
        [
        Input('Year Selector 1', 'value'),
        Input('Week Selector 1', 'value'),
        Input('Operator Dropdown 1', 'value'),
        Input('Equipment Dropdown 1', 'value'),
        Input('Shift Dropdown 1', 'value'),
        Input('Weekday Dropdown 1', 'value'),
        Input('Equipments Per Operator Dropdown 1', 'value'),
        ]
    )
    def update_1(selected_year, selected_week, operator_value, equipment_value, shift_value, weekday_value, equipment_per_operator):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': operator_value,'Equipment': equipment_value, 'Shift': shift_value, 'Weekday': weekday_value, 'Equipments per Operator': equipment_per_operator}
        title = generate_title(input_values, FIRST_GRAPH)

        df_twenty = load_df_smc(input_values)
        df_twenty_type = extract_type_smc(df_twenty)

        filtered_df = filter_dataframe(df_twenty, input_values)
        filtered_df_type = filter_dataframe(df_twenty_type, input_values)

        df_Collaborator = filtered_df_type.groupby(['Equipment', 'Type'])[['NOK by Type']].sum().reset_index()
        all_weeks = filtered_df_type['Equipment'].unique()
        OK_Total = filtered_df.groupby('Equipment')['OK'].sum()
        NOK_Total = filtered_df.groupby('Equipment')['NOK'].sum()

        OK_Total = OK_Total.reindex(all_weeks, fill_value=1)
        NOK_Total = NOK_Total.reindex(all_weeks, fill_value=0)
        NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100
        team_ratio_df = pd.DataFrame({'Equipment': all_weeks, 'NOK (%)': NOK_Ratio.values})
        ofa_categories_ordered = team_ratio_df.sort_values('NOK (%)', ascending=False)['Equipment']

        team_ratio_df['Equipment'] = pd.Categorical(team_ratio_df['Equipment'], categories=ofa_categories_ordered, ordered=True)
        team_ratio_df.sort_values(by='Equipment', inplace=True)

        fig = generate_grouped_bar_plot(df_Collaborator, 'Equipment', 'Type', title, 'Equipments', 'NOK by Type')
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Equipment'], y=team_ratio_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color='black')))
        fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':team_ratio_df['Equipment']})
        if NOK_Ratio.size > 0:
            ymax = 1.1* NOK_Ratio.values.max()
            fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', range=[0, ymax], overlaying='y', showgrid=False))
        else: fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False))
    
        return fig, fig

def equipment_layout(operator_show):
    current_year = datetime.datetime.now().year
    current_week = datetime.datetime.now().isocalendar()[1]
    operator_label, equipment_label = load_operator_label(), load_equipment_label()
    current_week_list = [1, current_week]
    # List of years from 2023 to the current year.
    YEAR_LIST = list(range(2023, datetime.datetime.now().year + 1))

    if operator_show:
        return html.Div(children=[

        html.Br(),
        html.P("Data comes from database1.db."),

        dbc.Row([               

            ##############################################
            # 1st Graph : Ten: NOK by Type per Equipment #
            ##############################################

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
                                dbc.Col(dcc.Dropdown(id='Year Selector 1', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 1', options=operator_label, placeholder="All Operators", value='All')),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 1', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                                dbc.Col(dcc.Dropdown(id='Shift Dropdown 1', options=SHIFT_LABEL_LIST, value='All', placeholder="All shifts"),),
                            ]),
                            dcc.Dropdown(id='Weekday Dropdown 1', options=WEEKDAY_LABEL_LIST, multi=True, value=list(calendar.day_name)),
                            dcc.Dropdown(id='Equipments Per Operator Dropdown 1', options=EQUIPMENTS_PER_OPERATOR_LABEL_LIST, multi=True, placeholder="All Equipments/Operator", value=EQUIPMENTS_PER_OPERATOR_LIST),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close1", className="ml-auto"))
                ], id="modal1", size="xl",),
            ], md=12),
        ], className="mt-4"),
    ], className='main_div'),

    else:
        return html.Div(children=[

        html.Br(),
        html.P("Data comes from database1.db."),

        dbc.Row([               

            ##############################################
            # 1st Graph : Ten: NOK by Type per Equipment #
            ##############################################

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
                                dbc.Col(dcc.Dropdown(id='Year Selector 1', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 1', options=operator_label, placeholder="All Operators", value='All'), style={'display': 'none'}),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 1', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                                dbc.Col(dcc.Dropdown(id='Shift Dropdown 1', options=SHIFT_LABEL_LIST, value='All', placeholder="All shifts"),),
                            ]),
                            dcc.Dropdown(id='Weekday Dropdown 1', options=WEEKDAY_LABEL_LIST, multi=True, value=list(calendar.day_name)),
                            dbc.Col(dcc.Dropdown(id='Equipments Per Operator Dropdown 1', options=EQUIPMENTS_PER_OPERATOR_LABEL_LIST, multi=True, placeholder="All Equipments/Operator", value=EQUIPMENTS_PER_OPERATOR_LIST), style={'display': 'none'}),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close1", className="ml-auto"))
                ], id="modal1", size="xl",),
            ], md=12),
        ], className="mt-4"),
    ], className='main_div'),


"""
    ################################################
    # 2nd Graph : Ten: NOK (%) per Equipment #
    ################################################

    @app.callback(
        [
        Output('Ten: NOK (%) per Equipment', 'figure'),
        Output('Ten: NOK (%) per Equipment (bis)', 'figure'),
        ],
        [
        Input('Year Selector 2', 'value'),
        Input('Week Selector 2', 'value'),
        Input('Operator Dropdown 2', 'value'),
        Input('Equipment Dropdown 2', 'value'),
        Input('Equipments Per Operator Dropdown 2', 'value'),
        Input('Shift Dropdown 2', 'value'),
        Input('Weekday Dropdown 2', 'value'),
        ]
    )
    def update_2(selected_year, selected_week, operator_value, equipment_value, equipment_per_operator, shift_value, weekday_value):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': operator_value,'Equipment': equipment_value, 'Shift': shift_value, 'Weekday': weekday_value, 'Equipments per Operator': equipment_per_operator}
        df_smc = load_df_smc(input_values)
        filtered_df = filter_dataframe(df_smc, input_values)
        title = generate_title(input_values, "Ten: NOK (%) per Equipment")

        df_Equipment = filtered_df.groupby('Equipment')[['OK', 'NOK', 'C', 'O', 'U', 'R', 'A']].sum().reset_index()
        df_Equipment['NOK (%)'] = (df_Equipment['NOK'] / (df_Equipment['OK'] + df_Equipment['NOK'])) * 100
        df_Equipment['C (%)'] = (df_Equipment['C'] / (df_Equipment['OK'] + df_Equipment['NOK'])) * 100
        df_Equipment['O (%)'] = (df_Equipment['O'] / (df_Equipment['OK'] + df_Equipment['NOK'])) * 100
        df_Equipment['U (%)'] = (df_Equipment['U'] / (df_Equipment['OK'] + df_Equipment['NOK'])) * 100
        df_Equipment['R (%)'] = (df_Equipment['R'] / (df_Equipment['OK'] + df_Equipment['NOK'])) * 100
        df_Equipment['A (%)'] = (df_Equipment['A'] / (df_Equipment['OK'] + df_Equipment['NOK'])) * 100
        df_Equipment.sort_values('Equipment', ascending=True, inplace=True)
        ymax = 1.1* df_Equipment['NOK (%)'].max()
        fig = go.Figure()

        for i in df_Equipment.index:
            fig.add_trace(go.Scatterpolar(
                r=[
                    df_Equipment.loc[i, 'NOK (%)'],
                    df_Equipment.loc[i, 'C (%)'],
                    df_Equipment.loc[i, 'O (%)'],
                    df_Equipment.loc[i, 'U (%)'],
                    df_Equipment.loc[i, 'R (%)'],
                    df_Equipment.loc[i, 'A (%)']
                    ],
                theta=['NOK (%)', 'C (%)', 'O (%)', 'U (%)', 'R (%)', 'A (%)'],
                fill='toself',
                name=df_Equipment.loc[i, 'Equipment'],
            ))
        fig.update_layout(height=400, polar=dict(radialaxis=dict(visible=True, range=[0, ymax])),showlegend=True, title='<b>' + title + '</b>')
        return fig, fig

    ########################################################
    # 3rd Graph : Ten: NOK (%) Boxplot per Equipment #
    ########################################################

    @app.callback(
        [
        Output('Ten: NOK (%) Boxplot per Equipment', 'figure'),
        Output('Ten: NOK (%) Boxplot per Equipment (bis)', 'figure'),
        ],
        [
        Input('Year Selector 3', 'value'),
        Input('Week Selector 3', 'value'),
        Input('Operator Dropdown 3', 'value'),
        Input('Equipment Dropdown 3', 'value'),
        Input('Shift Dropdown 3', 'value'),
        Input('Equipments Per Operator Dropdown 3', 'value'),
        Input('Weekday Dropdown 3', 'value'),
        ]
    )
    def update_3(selected_year, selected_week, operator_value, equipment_value, shift_value, equipment_per_operator, weekday_value):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': operator_value,'Equipment': equipment_value, 'Shift': shift_value, 'Weekday': weekday_value, 'Equipments per Operator': equipment_per_operator}
        df_smc = load_df_smc(input_values)
        filtered_df = filter_dataframe(df_smc, input_values)
        title = generate_title(input_values, "Ten: NOK (%) Boxplot per Equipment")

        filtered_df['NOK (%)'] = (filtered_df['NOK'] / (filtered_df['OK'] + filtered_df['NOK'])) * 100
        filtered_df.sort_values('Equipment', ascending=True, inplace=True)
        fig = go.Figure()
        fig.add_trace(go.Box(x=filtered_df['Equipment'], y= filtered_df['NOK (%)'], boxpoints='all', jitter=0.5, whiskerwidth=0.2))
        fig.update_layout(height=400, title='<b>' + title + '</b>')
        fig.update_xaxes(tickangle=315)
        return fig, fig
 

            ################################################
            # 2nd Graph : Ten: NOK (%) per Equipment #
            ################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Ten: NOK (%) per Equipment', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Ten: NOK (%) per Equipment (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 2', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Selector 2', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 2', options=operator_label, placeholder="All Operators", value='All')),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 2', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                                dbc.Col(dcc.Dropdown(id='Shift Dropdown 2', options=SHIFT_LABEL_LIST, value='All', placeholder="All shifts"),),
                            ]),
                            dcc.Dropdown(id='Weekday Dropdown 2', options=WEEKDAY_LABEL_LIST, multi=True, value=list(calendar.day_name)),
                            dcc.Dropdown(id='Equipments Per Operator Dropdown 2', options=EQUIPMENTS_PER_OPERATOR_LABEL_LIST, multi=True, placeholder="All Equipments/Operator", value=EQUIPMENTS_PER_OPERATOR_LIST),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close2", className="ml-auto")),
                ], id="modal2", size="xl"),
            ], md=6),
            
        ], className="mt-4"),
            
        dbc.Row([
            
            ########################################################
            # 3rd Graph : Ten: NOK (%) Boxplot per Equipment #
            ########################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Ten: NOK (%) Boxplot per Equipment', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Ten: NOK (%) Boxplot per Equipment (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 3', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Selector 3', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 3', options=operator_label, placeholder="All Operators", value='All')),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 3', options=equipment_label, placeholder="All Equipments", value = 'All')),
                                dbc.Col(dcc.Dropdown(id='Shift Dropdown 3', options=SHIFT_LABEL_LIST, value='All', placeholder="All shifts"),),
                            ]),
                            dcc.Dropdown(id='Weekday Dropdown 3', options=WEEKDAY_LABEL_LIST, multi=True, value=list(calendar.day_name)),
                            dcc.Dropdown(id='Equipments Per Operator Dropdown 3', options=EQUIPMENTS_PER_OPERATOR_LABEL_LIST, multi=True, placeholder="All Equipments/Operator", value=EQUIPMENTS_PER_OPERATOR_LIST),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close3", className="ml-auto")),
                ], id="modal3", size="xl"),
            ], md=6),


            ################################################
            # 2nd Graph : Ten: NOK (%) per Equipment #
            ################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Ten: NOK (%) per Equipment', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Ten: NOK (%) per Equipment (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 2', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Selector 2', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 2', options=operator_label, placeholder="All Operators", value='All'), style={'display': 'none'}),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 2', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                                dbc.Col(dcc.Dropdown(id='Shift Dropdown 2', options=SHIFT_LABEL_LIST, value='All', placeholder="All shifts"),),
                            ]),
                            dcc.Dropdown(id='Weekday Dropdown 2', options=WEEKDAY_LABEL_LIST, multi=True, value=list(calendar.day_name)),
                            dbc.Col(dcc.Dropdown(id='Equipments Per Operator Dropdown 2', options=EQUIPMENTS_PER_OPERATOR_LABEL_LIST, multi=True, placeholder="All Equipments/Operator", value=EQUIPMENTS_PER_OPERATOR_LIST), style={'display': 'none'}),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close2", className="ml-auto")),
                ], id="modal2", size="xl"),
            ], md=6),
            
        ], className="mt-4"),
            
        dbc.Row([
            
            ########################################################
            # 3rd Graph : Ten: NOK (%) Boxplot per Equipment #
            ########################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Ten: NOK (%) Boxplot per Equipment', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Ten: NOK (%) Boxplot per Equipment (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 3', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Selector 3', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 3', options=operator_label, placeholder="All Operators", value='All'), style={'display': 'none'}),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 3', options=equipment_label, placeholder="All Equipments", value = 'All')),
                                dbc.Col(dcc.Dropdown(id='Shift Dropdown 3', options=SHIFT_LABEL_LIST, value='All', placeholder="All shifts"),),
                            ]),
                            dcc.Dropdown(id='Weekday Dropdown 3', options=WEEKDAY_LABEL_LIST, multi=True, value=list(calendar.day_name)),
                            dbc.Col(dcc.Dropdown(id='Equipments Per Operator Dropdown 3', options=EQUIPMENTS_PER_OPERATOR_LABEL_LIST, multi=True, placeholder="All Equipments/Operator", value=EQUIPMENTS_PER_OPERATOR_LIST), style={'display': 'none'}),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close3", className="ml-auto")),
                ], id="modal3", size="xl"),
            ], md=6),


"""