"""
Module related to the different graphs in Micro-Machining > Tool.

Database name : hsma2.
Corresponding CSV files : uu_tracking.csv.
"""

import calendar, datetime

import dash_bootstrap_components as dbc, plotly.graph_objects as go, pandas as pd, numpy as np

from dash import html, dcc
from dash.dependencies import Input, Output

from smc_load import load_df_smc
from generate_plots import generate_grouped_bar_plot
from filters import filter_dataframe, generate_title
from dicts import CustomCard, COLOR_DICT, WEEKDAY_DICT, WEEK_DICT, EQUIPMENTS_PER_OPERATOR_LIST, EQUIPMENTS_PER_OPERATOR_LABEL_LIST, SHIFT_LABEL_LIST, NOK_SORTING_LIST, WEEKDAY_LABEL_LIST
from utils import load_operator_label, load_equipment_label, extract_type_smc

def register_weekday_callbacks(app):

    ##################################################
    # 1st Graph : Machining: NOK by Type per Weekday #
    ##################################################

    @app.callback(
        [
        Output('Machining: NOK by Type per Weekday', 'figure'),
        Output('Machining: NOK by Type per Weekday (bis)', 'figure'),
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
        title = generate_title(input_values, "Machining: NOK by Type per Weekday")

        df_ebavurage = load_df_smc(input_values)
        df_ebavurage_type = extract_type_smc(df_ebavurage)

        filtered_df = filter_dataframe(df_ebavurage, input_values)
        filtered_df_type = filter_dataframe(df_ebavurage_type, input_values)

        df_Collaborator = filtered_df_type.groupby(['Weekday', 'Type'])[['NOK by Type']].sum().reset_index()
        all_weeks = filtered_df_type['Weekday'].unique()
        OK_Total = filtered_df.groupby('Weekday')['OK'].sum()
        NOK_Total = filtered_df.groupby('Weekday')['NOK'].sum()

        OK_Total = OK_Total.reindex(all_weeks, fill_value=1)
        NOK_Total = NOK_Total.reindex(all_weeks, fill_value=0)
        NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100
        team_ratio_df = pd.DataFrame({'Weekday': all_weeks, 'NOK (%)': NOK_Ratio.values})
        ofa_categories_ordered = team_ratio_df.sort_values('NOK (%)', ascending=False)['Weekday']

        team_ratio_df['Weekday'] = pd.Categorical(team_ratio_df['Weekday'], categories=ofa_categories_ordered, ordered=True)
        team_ratio_df.sort_values(by='Weekday', inplace=True)

        fig = generate_grouped_bar_plot(df_Collaborator, 'Weekday', 'Type', title, 'Weekdays', 'NOK by Type')
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Weekday'], y=team_ratio_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color=COLOR_DICT['NOK (%)'])))
        fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':team_ratio_df['Weekday']})
        if NOK_Ratio.size > 0:
            ymax = 1.1* NOK_Ratio.values.max()
            fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', range=[0, ymax], overlaying='y', showgrid=False))
        else: fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False))


        return fig, fig

    ######################################################
    # 2nd Graph : Machining: NOK (%) Boxplot per Weekday #
    ######################################################

    @app.callback(
        [
        Output('Machining: NOK (%) Boxplot per Weekday', 'figure'),
        Output('Machining: NOK (%) Boxplot per Weekday (bis)', 'figure'),
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
        title = generate_title(input_values, "Machining: NOK (%) Boxplot per Weekday")

        filtered_df[f'NOK (%)'] = (filtered_df[f'NOK'] / (filtered_df['OK'] + filtered_df['NOK'])) * 100
        filtered_df['Weekday Rank'] = filtered_df['Weekday'].map(WEEKDAY_DICT)
        filtered_df.sort_values('Weekday Rank', inplace=True)
        del filtered_df['Weekday Rank']
        fig = go.Figure()
        fig.add_trace(go.Box(x=filtered_df['Weekday'], y= filtered_df[f'NOK (%)'], boxpoints='all', jitter=0.5, whiskerwidth=0.2))
        fig.update_layout(height=400, title='<b>' + title + '</b>')
        fig.update_xaxes(title_text='Weekday', tickangle=315)
        fig.update_yaxes(title_text=f'NOK (%)')

        return fig, fig

def weekday_layout(operator_show):
    current_year = datetime.datetime.now().year
    current_week = datetime.datetime.now().isocalendar()[1]
    operator_label, equipment_label = load_operator_label(), load_equipment_label()
    current_week_list = [current_week, current_week]
    # List of years from 2023 to the current year.
    YEAR_LIST = list(range(2023, datetime.datetime.now().year + 1))

    if operator_show:

        return html.Div(children=[
            
        html.Br(),
        html.P("Data comes from Intranet."),

        dbc.Row([               

            ##################################################
            # 1st Graph : Machining: NOK by Type per Weekday #
            ##################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK by Type per Weekday', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK by Type per Weekday (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
            ], md=6),
        
            ######################################################
            # 2nd Graph : Machining: NOK (%) Boxplot per Weekday #
            ######################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK (%) Boxplot per Weekday', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK (%) Boxplot per Weekday (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
    ], className='main_div'),

    else:
        return html.Div(children=[
            
        html.Br(),
        html.P("Data comes from Intranet."),

        dbc.Row([               

            ##################################################
            # 1st Graph : Machining: NOK by Type per Weekday #
            ##################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK by Type per Weekday', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK by Type per Weekday (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
            ], md=6),
        
            ######################################################
            # 2nd Graph : Machining: NOK (%) Boxplot per Weekday #
            ######################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK (%) Boxplot per Weekday', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK (%) Boxplot per Weekday (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
    ], className='main_div'),




