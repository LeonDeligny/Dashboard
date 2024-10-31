"""
Module related to the different graphs in pre-Ten > Trend.
"""

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import calendar, datetime
import pandas as pd, numpy as np

from dash import html, dcc
from dash.dependencies import Input, Output

from smc_load import load_df_smc, extract_cons_tool
from generate_plots import generate_grouped_bar_plot
from filters import filter_dataframe, generate_title
from dicts import CustomCard, COLOR_DICT_EQUIPMENT, TEAM_COLOR, WEEK_DICT, EQUIPMENTS_PER_OPERATOR_LIST, EQUIPMENTS_PER_OPERATOR_LABEL_LIST, SHIFT_LABEL_LIST, WEEKDAY_LABEL_LIST
from utils import load_operator_label, load_equipment_label, extract_type_smc

FIRST_GRAPH = "Ten: NOK by Type per week"

def register_week_callbacks(app):

    #########################################
    # 1st Graph : Ten: NOK by Type per week #
    #########################################

    @app.callback(
        [
        Output(FIRST_GRAPH, 'figure'),
        Output(FIRST_GRAPH + ' (bis)', 'figure'),
        ],
        [
        Input('Year Dropdown 1', 'value'),
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

        df_Week = filtered_df_type.groupby(['Week', 'Type'])[['NOK by Type']].sum().reset_index()
        df_Week.sort_values(by=['Type'], inplace=True, ascending=False)
        df_Week.reset_index(drop=True, inplace=True)

        fig = generate_grouped_bar_plot(df_Week, 'Week', 'Type', title, 'Weeks', 'NOK by Type')
        week_start, week_end = selected_week
        all_weeks = np.arange(week_start, week_end+1)
        OK_Total = filtered_df.groupby('Week')['OK'].sum()
        NOK_Total = filtered_df.groupby('Week')['NOK'].sum()

        OK_Total = OK_Total.reindex(all_weeks, fill_value=1)
        NOK_Total = NOK_Total.reindex(all_weeks, fill_value=0)
        NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100

        team_ratio_df = pd.DataFrame({'Week': all_weeks, 'NOK (%)': NOK_Ratio.values})
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color='black')))
        if NOK_Ratio.size > 0:
            ymax = 1.1* NOK_Ratio.values.max()
            fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', range=[0, ymax], overlaying='y', showgrid=False))
        else: fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False))

        return fig, fig

def week_layout(operator_show):
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

            #########################################
            # 1st Graph : Ten: NOK by Type per week #
            #########################################

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

            #########################################
            # 1st Graph : Ten: NOK by Type per week #
            #########################################

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
    #############################################
    # 2nd Graph : Ten: NOK by Operator per week #
    #############################################

    @app.callback(
        [
        Output(SECOND_GRAPH, 'figure'),
        Output(SECOND_GRAPH + ' (bis)', 'figure'),
        ],
        [
        Input('Year Dropdown 2', 'value'),
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
        title = generate_title(input_values, SECOND_GRAPH)
        
        df_smc = load_df_smc(input_values)
        filtered_df = filter_dataframe(df_smc, input_values)

        recent_operator_teams = filtered_df.sort_values('Date').groupby('Operator').last()['Team'].reset_index()
        operators_by_teams = recent_operator_teams.sort_values('Team')['Operator']
        recent_teams = filtered_df.sort_values('Date', ascending=True).drop_duplicates('Operator', keep='last')
        operators_by_teams = recent_teams.groupby("Team")["Operator"].unique().to_dict()
        ordered_operators = [operator for operators in operators_by_teams.values() for operator in operators]
                
        df_Week = filtered_df.groupby(['Week', 'Operator'])[['OK', "NOK"]].sum().reset_index()
        df_Week['Operator'] = pd.Categorical(df_Week['Operator'], categories=ordered_operators, ordered=True)
        df_Week.sort_values(by=['Operator'], inplace=True)
        df_Week.reset_index(drop=True, inplace=True)

        fig = generate_grouped_bar_plot(df_Week, 'Week', 'Operator', title, 'Weeks', "NOK", 315, filtered_df)
        week_start, week_end = selected_week
        all_weeks = np.arange(week_start, week_end+1)
        OK_Total = filtered_df.groupby('Week')['OK'].sum()
        NOK_Total = filtered_df.groupby('Week')["NOK"].sum()

        OK_Team_0 = filtered_df[filtered_df['Team'] == 0].groupby('Week')['OK'].sum()
        OK_Team_1 = filtered_df[filtered_df['Team'] == 1].groupby('Week')['OK'].sum()
        OK_Team_2 = filtered_df[filtered_df['Team'] == 2].groupby('Week')['OK'].sum()
        OK_Team_3 = filtered_df[filtered_df['Team'] == 3].groupby('Week')['OK'].sum()
        NOK_Team_0 = filtered_df[filtered_df['Team'] == 0].groupby('Week')["NOK"].sum()
        NOK_Team_1 = filtered_df[filtered_df['Team'] == 1].groupby('Week')["NOK"].sum()
        NOK_Team_2 = filtered_df[filtered_df['Team'] == 2].groupby('Week')["NOK"].sum()
        NOK_Team_3 = filtered_df[filtered_df['Team'] == 3].groupby('Week')["NOK"].sum()

        OK_Team_0 = OK_Team_0.reindex(all_weeks, fill_value=1)
        OK_Team_1 = OK_Team_1.reindex(all_weeks, fill_value=1)
        OK_Team_2 = OK_Team_2.reindex(all_weeks, fill_value=1)
        OK_Team_3 = OK_Team_3.reindex(all_weeks, fill_value=1)
        NOK_Team_0 = NOK_Team_0.reindex(all_weeks, fill_value=0)
        NOK_Team_1 = NOK_Team_1.reindex(all_weeks, fill_value=0)
        NOK_Team_2 = NOK_Team_2.reindex(all_weeks, fill_value=0)
        NOK_Team_3 = NOK_Team_3.reindex(all_weeks, fill_value=0)

        NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100
        Team_0_Ratio = (NOK_Team_0 / (OK_Team_0 + NOK_Team_0)) * 100
        Team_1_Ratio = (NOK_Team_1 / (OK_Team_1 + NOK_Team_1)) * 100
        Team_2_Ratio = (NOK_Team_2 / (OK_Team_2 + NOK_Team_2)) * 100
        Team_3_Ratio = (NOK_Team_3 / (OK_Team_3 + NOK_Team_3)) * 100

        team_ratio_df = pd.DataFrame({'Week': all_weeks, f'NOK (%)': NOK_Ratio.values,'Team 0 (%)': Team_0_Ratio.values,'Team 1 (%)': Team_1_Ratio.values,'Team 2 (%)': Team_2_Ratio.values, 'Team 3 (%)': Team_3_Ratio.values})
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df['Team 3 (%)'], name=f'NOK Team 3 (%)', yaxis='y2', line=dict(color=TEAM_COLOR['Team 3 (%)']), visible='legendonly'))
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df['Team 2 (%)'], name=f'NOK Team 2 (%)', yaxis='y2', line=dict(color=TEAM_COLOR['Team 2 (%)'])))
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df['Team 1 (%)'], name=f'NOK Team 1 (%)', yaxis='y2', line=dict(color=TEAM_COLOR['Team 1 (%)'])))
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df['Team 0 (%)'], name=f'NOK Team 0 (%)', yaxis='y2', line=dict(color=TEAM_COLOR['Team 0 (%)'])))
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df[f'NOK (%)'], name=f'NOK (%)', yaxis='y2', line=dict(color='black'), visible='legendonly'))

        try:
            ymax = 1.1 * max(Team_0_Ratio.values.max(), Team_1_Ratio.values.max(), Team_2_Ratio.values.max(), Team_3_Ratio.values.max())
        except ValueError:
            ymax = 0
        fig.update_layout(yaxis2=dict(title=f'NOK (%)', side='right', range=[0, ymax], overlaying='y', showgrid=False))

        return fig, fig

    ##############################################
    # 3rd Graph : Ten: NOK by Equipment per week #
    ##############################################

    @app.callback(
        [
        Output('Ten: NOK by Equipment per week', 'figure'),
        Output('Ten: NOK by Equipment per week (bis)', 'figure'),
        ],
        [
        Input('Year Dropdown 3', 'value'),
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
        title = generate_title(input_values, "Ten: NOK by Equipment per week")
        week_start, week_end = selected_week
        all_weeks = np.arange(week_start, week_end+1)
        df_Week = filtered_df.groupby(['Week', 'Equipment'])[['OK', "NOK"]].sum().reset_index()
        df_Week.sort_values(by=['Equipment'], inplace=True, ascending=False)
        df_Week.reset_index(drop=True, inplace=True)

        unique_equipments = sorted(df_smc['Equipment'].unique())

        fig = generate_grouped_bar_plot(df_Week, 'Week', 'Equipment', title, 'Weeks', "NOK")
        OK_Total = filtered_df.groupby('Week')['OK'].sum()
        NOK_Total = filtered_df.groupby('Week')["NOK"].sum()

        OK_Equipment_0 = filtered_df[filtered_df['Equipment'].str.contains('Equipment1')].groupby('Week')['OK'].sum()
        OK_Equipment_1 = filtered_df[filtered_df['Equipment'].str.contains('Equipment2')].groupby('Week')['OK'].sum()
        OK_Equipment_2 = filtered_df[filtered_df['Equipment'].str.contains('Equipment3')].groupby('Week')['OK'].sum()
        NOK_Equipment_0 = filtered_df[filtered_df['Equipment'].str.contains('Equipment1')].groupby('Week')["NOK"].sum()
        NOK_Equipment_1 = filtered_df[filtered_df['Equipment'].str.contains('Equipment2')].groupby('Week')["NOK"].sum()
        NOK_Equipment_2 = filtered_df[filtered_df['Equipment'].str.contains('Equipment3')].groupby('Week')["NOK"].sum()

        OK_Equipment_0 = OK_Equipment_0.reindex(all_weeks, fill_value=1)
        OK_Equipment_1 = OK_Equipment_1.reindex(all_weeks, fill_value=1)
        OK_Equipment_2 = OK_Equipment_2.reindex(all_weeks, fill_value=1)
        NOK_Equipment_0 = NOK_Equipment_0.reindex(all_weeks, fill_value=0)
        NOK_Equipment_1 = NOK_Equipment_1.reindex(all_weeks, fill_value=0)
        NOK_Equipment_2 = NOK_Equipment_2.reindex(all_weeks, fill_value=0)

        NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100
        Equipment_0_Ratio = (NOK_Equipment_0 / (OK_Equipment_0 + NOK_Equipment_0)) * 100
        Equipment_1_Ratio = (NOK_Equipment_1 / (OK_Equipment_1 + NOK_Equipment_1)) * 100
        Equipment_2_Ratio = (NOK_Equipment_2 / (OK_Equipment_2 + NOK_Equipment_2)) * 100

        team_ratio_df = pd.DataFrame({'Week': all_weeks,'NOK (%)': NOK_Ratio.values,'Equipment1 (%)': Equipment_0_Ratio.values,'Equipment2 (%)': Equipment_1_Ratio.values,'Equipment3 (%)': Equipment_2_Ratio.values})
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df['Equipment3 (%)'], name=f'{"NOK"} Equipment3 (%)', yaxis='y2', line=dict(color=COLOR_DICT_EQUIPMENT['Equipment3 (%)']) ))
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df['Equipment2 (%)'], name=f'NOK Equipment2 (%)', yaxis='y2', line=dict(color=COLOR_DICT_EQUIPMENT['Equipment2 (%)'])))
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df['Equipment1 (%)'], name=f'NOK Equipment1 (%)', yaxis='y2', line=dict(color=COLOR_DICT_EQUIPMENT['Equipment1 (%)'])))
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Week'], y=team_ratio_df['NOK (%)'], name=f'NOK (%)', yaxis='y2', line=dict(color='black'), visible='legendonly'))

        equipment_ratios = {}
        for equipment in unique_equipments:
            NOK = filtered_df[filtered_df['Equipment'] == equipment].groupby('Week')['NOK'].sum()
            NOK = NOK.reindex(all_weeks, fill_value=0)
            TYPE = filtered_df[filtered_df['Equipment'] == equipment].groupby('Week')[f'NOK'].sum()
            TYPE = TYPE.reindex(all_weeks, fill_value=0)
            OK = filtered_df[filtered_df['Equipment'] == equipment].groupby('Week')['OK'].sum()
            OK = OK.reindex(all_weeks, fill_value=1)
            ratio = (TYPE / (OK + NOK)) * 100
            equipment_ratios[equipment] = ratio

        for equipment in unique_equipments:
            if equipment in equipment_ratios:
                fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines", x=all_weeks, y=equipment_ratios[equipment].values, name=f'{equipment} (%)', yaxis='y2', line=dict(color=COLOR_DICT_EQUIPMENT[equipment[:4]+' (%)']), visible='legendonly'))
        try:
            ymax = 1.1 * max(Equipment_0_Ratio.values.max(), Equipment_1_Ratio.values.max(), Equipment_2_Ratio.values.max())
        except ValueError:
            ymax = 0
        fig.update_layout(yaxis2=dict(title=f'NOK (%)', side='right', range=[0, ymax], overlaying='y', showgrid=False))

        return fig, fig

    ##################################################
    # 4th Graph : Ten: NOK by N° CONS per week #
    ##################################################

    @app.callback(
        [
        Output('Ten: NOK by N° CONS per week', 'figure'),
        Output('Ten: NOK by N° CONS per week (bis)', 'figure'),
        ],
        [
        Input('Year Dropdown 4', 'value'),
        Input('Week Selector 4', 'value'),
        Input('Operator Dropdown 4', 'value'),
        Input('Equipment Dropdown 4', 'value'),
        Input('Equipments Per Operator Dropdown 4', 'value'),
        Input('Shift Dropdown 4', 'value'),
        Input('Weekday Dropdown 4', 'value'),
        ]
    )
    def update_4(selected_year, selected_week, operator_value, equipment_value, equipment_per_operator, shift_value, weekday_value):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': operator_value,'Equipment': equipment_value, 'Shift': shift_value, 'Weekday': weekday_value, 'Equipments per Operator': equipment_per_operator}
        df_smc = load_df_smc(input_values)
        df_smc_cons = extract_cons_tool(df_smc)
        filtered_df = filter_dataframe(df_smc_cons, input_values)
        title = generate_title(input_values, "Ten: NOK by N° CONS per week")

        df_Week = filtered_df.groupby(['Week', 'N° CONS'])[["NOK"]].sum().reset_index()
        df_Week.sort_values(by=['N° CONS'], inplace=True, ascending=False)
        df_Week.reset_index(drop=True, inplace=True)
        fig = generate_grouped_bar_plot(df_Week, 'Week', 'N° CONS', title, 'Weeks', "NOK")

        return fig, fig

            ##################################################
            # 4th Graph : Ten: NOK by N° CONS per week #
            ################################################## 

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Ten: NOK by N° CONS per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open4", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Ten: NOK by N° CONS per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 4', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 4', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 4', options=operator_label, placeholder="All Operators", value='All')),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 4', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                                dbc.Col(dcc.Dropdown(id='Shift Dropdown 4', options=SHIFT_LABEL_LIST, value='All', placeholder="All shifts"),),
                            ]),
                            dcc.Dropdown(id='Weekday Dropdown 4', options=WEEKDAY_LABEL_LIST, multi=True, value=list(calendar.day_name)),
                            dcc.Dropdown(id='Equipments Per Operator Dropdown 4', options=EQUIPMENTS_PER_OPERATOR_LABEL_LIST, multi=True, placeholder="All Equipments/Operator", value=EQUIPMENTS_PER_OPERATOR_LIST),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close4", className="ml-auto")),
                ], id="modal4", size="xl"),
            ], md=6),
            ##################################################
            # 4th Graph : Ten: NOK by N° CONS per week #
            ################################################## 

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Ten: NOK by N° CONS per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open4", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Ten: NOK by N° CONS per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 4', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 4', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 4', options=operator_label, placeholder="All Operators", value='All'), style={'display': 'none'}),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 4', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                                dbc.Col(dcc.Dropdown(id='Shift Dropdown 4', options=SHIFT_LABEL_LIST, value='All', placeholder="All shifts"),),
                            ]),
                            dcc.Dropdown(id='Weekday Dropdown 4', options=WEEKDAY_LABEL_LIST, multi=True, value=list(calendar.day_name)),
                            dbc.Col(dcc.Dropdown(id='Equipments Per Operator Dropdown 4', options=EQUIPMENTS_PER_OPERATOR_LABEL_LIST, multi=True, placeholder="All Equipments/Operator", value=EQUIPMENTS_PER_OPERATOR_LIST), style={'display': 'none'}),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close4", className="ml-auto")),
                ], id="modal4", size="xl"),
            ], md=6),


"""

"""
            ###################################################
            # 2nd Graph : Ten: NOK by Operator per week #
            ###################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Ten: NOK by Operator per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Ten: NOK by Operator per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 2', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 2', options=YEAR_LIST, value=current_year)),
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
            
            ####################################################
            # 3rd Graph : Ten: NOK by Equipment per week #
            ####################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Ten: NOK by Equipment per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Ten: NOK by Equipment per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 3', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 3', options=YEAR_LIST, value=current_year)),
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

            ####################################################
            # 3rd Graph : Ten: NOK by Equipment per week #
            ####################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Ten: NOK by Equipment per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Ten: NOK by Equipment per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 3', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 3', options=YEAR_LIST, value=current_year)),
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


"""