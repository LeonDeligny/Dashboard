"""
Module related to the different graphs in Overall Scrap.

Database name : hsma2.
Corresponding CSV files : uu_tracking.csv & pp_tracking.csv.
"""

import datetime

import dash_bootstrap_components as dbc, plotly.graph_objects as go, pandas as pd, numpy as np

from dash import html, dcc
from dash.dependencies import Input, Output

from smc_load import load_df_smc 
from pp_load import load_df_twenty, load_df_hundred
from filters import filter_dataframe, generate_title
from dicts import CustomCard, WEEK_DICT, COLOR_DICT_GLOBAL
from utils import load_operator_label, load_equipment_label

def overall_scrap_layout_callbacks(app):

    ####################################################################
    # 1st Graph : NOK of 10, 20, 100 Control per week #
    ####################################################################

    @app.callback(
        [
        Output('NOK of 10, 20, 100 Control per week', 'figure'),
        Output('NOK of 10, 20, 100 Control per week (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 1', 'value'),
        Input('Week Selector 1', 'value'),
        Input('Operator Dropdown 1', 'value'),
        Input('Equipment Dropdown 1', 'value')
        ]
    )
    def Update_Combined_Type_Week_Bar(selected_year, selected_week, selected_operator, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': selected_operator, 'Equipment': selected_equipment}
        title = generate_title(input_values, "NOK per week")

        def process_data(df, df_name_ratio, df_name_nok, df_name_ok):
            filtered_df = filter_dataframe(df, input_values)  #filter the df
            OK_Total = filtered_df.groupby('Week')['OK'].sum().reindex(all_weeks, fill_value=1)
            NOK_Total = filtered_df.groupby('Week')['NOK'].sum().reindex(all_weeks, fill_value=0)
            NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100
            return pd.DataFrame({'Week': all_weeks, df_name_ratio: NOK_Ratio.values, df_name_nok: NOK_Total.values, df_name_ok: OK_Total.values})

        df_smc_copy = load_df_smc(input_values)
        df_twenty = load_df_twenty(input_values)
        df_visuel = load_df_hundred(input_values)

        df_smc_copy['Equipment'] = df_smc_copy['Equipment'].apply(lambda x: x[:-2] if x.startswith("Equipment2") else x)

        dfs = [df_twenty, df_visuel, df_smc_copy]
        df_names_ratio = ['NOK 20 (%)', 'NOK 100 (%)', 'NOK 10 (%)']
        df_names_nok = ['NOK 20', 'NOK 100', 'NOK 10']
        df_names_ok = ['OK 20', 'OK 100 Control', 'OK 10']

        filtered_df_smc = filter_dataframe(df_smc_copy, input_values)  #filter the df_smc for all weeks
        all_weeks = np.sort(filtered_df_smc['Week'].unique())

        processed_dfs = [process_data(df, name_ratio, name_nok, name_ok) for df, name_ratio, name_nok, name_ok in zip(dfs, df_names_ratio, df_names_nok, df_names_ok)]

        final_df = processed_dfs[0].merge(processed_dfs[1], on="Week").merge(processed_dfs[2], on="Week")  # join all dfs on 'Week'
        final_df['NOK (%)'] = final_df[df_names_ratio].sum(axis=1)  # compute total NOK Ratio

        fig = go.Figure()  #create a figure
        for column in df_names_nok:
            fig.add_trace(go.Bar(hovertemplate='%{y:.2f}', x=final_df['Week'], y=final_df[column], name=column, yaxis='y1', marker_color=COLOR_DICT_GLOBAL[column], opacity=0.65))
            fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=final_df['Week'], y=final_df[column + ' (%)'], name=column + ' (%)', yaxis='y2', marker_color=COLOR_DICT_GLOBAL[column]))

        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=final_df['Week'], y=final_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color='black')))
        ymax = 1.1* final_df['NOK (%)'].max()

        fig.update_layout(barmode='stack', height=400, title='<b>' + title + '</b>', hovermode="x unified", xaxis_title="Weeks")  #update layout
        fig.update_layout(yaxis=dict(title='NOK', side='left', showgrid=False), yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False, range=[0,ymax]), autosize=True, legend=dict(orientation="v", x=1.2, y=1))
        fig.update_xaxes(tick0=0, dtick=1, tickangle=315, title_standoff=30)
        
        return fig, fig


    ############################################################################
    # 2nd Graph : NOK (%) of 10, 20, 100 Control per Operator #
    ############################################################################

    @app.callback(
        [
        Output('NOK (%) of 10, 20, 100 Control per Operator', 'figure'),
        Output('NOK (%) of 10, 20, 100 Control per Operator (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 2', 'value'),
        Input('Week Selector 2', 'value'),
        Input('Operator Dropdown 2', 'value'),
        Input('Equipment Dropdown 2', 'value')
        ]
    )
    def Update_Combined_Type_Operator_Bar(selected_year, selected_week, selected_operator, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': selected_operator,'Equipment': selected_equipment}
        title = generate_title(input_values, "NOK per Operator")

        def process_data(df, df_name_ratio, df_name_nok, df_name_ok):
            filtered_df = filter_dataframe(df, input_values)  #filter the df
            all_Operators = filtered_df['Operator'].unique()
            OK_Total = filtered_df.groupby('Operator')['OK'].sum().reindex(all_Operators, fill_value=1)
            NOK_Total = filtered_df.groupby('Operator')['NOK'].sum().reindex(all_Operators, fill_value=0)
            NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100
            return pd.DataFrame({'Operator': all_Operators, df_name_ratio: NOK_Ratio.values, df_name_nok: NOK_Total.values, df_name_ok: OK_Total.values})

        df_smc_copy = load_df_smc(input_values)
        df_twenty = load_df_twenty(input_values)
        df_visuel = load_df_hundred(input_values)
        df_smc_copy['Equipment'] = df_smc_copy['Equipment'].apply(lambda x: x[:-2] if x.startswith("Equipment2") else x)

        dfs = [df_twenty, df_visuel, df_smc_copy]
        df_names_ratio = ['NOK 20 (%)', 'NOK 100 (%)', 'NOK 10 (%)']
        df_names_nok = ['NOK 20', 'NOK 100', 'NOK 10']
        df_names_ok = ['OK 20', 'OK 100 Control', 'OK 10']

        processed_dfs = [process_data(df, name_ratio, name_nok, name_ok) for df, name_ratio, name_nok, name_ok in zip(dfs, df_names_ratio, df_names_nok, df_names_ok)]

        final_df = processed_dfs[0].merge(processed_dfs[1], on="Operator").merge(processed_dfs[2], on="Operator")  # join all dfs on 'Operator'
        final_df['NOK (%)'] = final_df[df_names_ratio].sum(axis=1)  # compute total NOK Ratio

        fig = go.Figure()  #create a figure
        final_df.sort_values(by=['NOK (%)', 'NOK 10 (%)', 'NOK 100 (%)', 'NOK 20 (%)'], ascending=False, inplace=True)
        for column in df_names_nok:
            fig.add_trace(go.Bar(hovertemplate='%{y:.2f}', x=final_df['Operator'], y=final_df[column], name=column, yaxis='y1', marker_color=COLOR_DICT_GLOBAL[column], opacity=0.65))
            fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=final_df['Operator'], y=final_df[column + ' (%)'], name=column + ' (%)', yaxis='y2', marker_color=COLOR_DICT_GLOBAL[column]))

        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=final_df['Operator'], y=final_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color='black')))
        ymax = 1.1* final_df['NOK (%)'].max()

        fig.update_layout(barmode='stack', height=400, title='<b>' + title + '</b>', hovermode="x unified", xaxis_title="Operators")  #update layout
        fig.update_layout(yaxis=dict(title='NOK', side='left', showgrid=False), yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False, range=[0,ymax]), autosize=True, legend=dict(orientation="v", x=1.2, y=1))
        fig.update_xaxes(tick0=0, dtick=1, tickangle=315, title_standoff=30)
        return fig, fig

    #############################################################################
    # 3rd Graph : NOK (%) of 10, 20, 100 Control per Equipment #
    #############################################################################

    @app.callback(
        [
        Output('NOK (%) of 10, 20, 100 Control per Equipment', 'figure'),
        Output('NOK (%) of 10, 20, 100 Control per Equipment (bis)', 'figure')
        ],
        [
        Input('Year Dropdown 3', 'value'),
        Input('Week Selector 3', 'value'),
        Input('Operator Dropdown 3', 'value'),
        Input('Equipment Dropdown 3', 'value')
        ]
    )
    def Update_Combined_Type_Equipment_Bar(selected_year, selected_week, selected_operator, selected_equipment):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': selected_operator, 'Equipment': selected_equipment}
        title = generate_title(input_values, "NOK per Equipment")

        def process_data(df, df_name_ratio, df_name_nok, df_name_ok):
            filtered_df = filter_dataframe(df, input_values)  #filter the df
            all_Equipments = filtered_df['Equipment'].unique()
            OK_Total = filtered_df.groupby('Equipment')['OK'].sum().reindex(all_Equipments, fill_value=1)
            NOK_Total = filtered_df.groupby('Equipment')['NOK'].sum().reindex(all_Equipments, fill_value=0)
            NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100
            return pd.DataFrame({'Equipment': all_Equipments, df_name_ratio: NOK_Ratio.values, df_name_nok: NOK_Total.values, df_name_ok: OK_Total.values})

        df_smc_copy = load_df_smc(input_values)
        df_twenty = load_df_twenty(input_values)
        df_visuel = load_df_hundred(input_values)
        df_smc_copy['Equipment'] = df_smc_copy['Equipment'].apply(lambda x: x[:-2] if x.startswith("Equipment2") else x)

        dfs = [df_twenty, df_visuel, df_smc_copy]

        df_names_ratio = ['NOK 20 (%)', 'NOK 100 (%)', 'NOK 10 (%)']
        df_names_nok = ['NOK 20', 'NOK 100', 'NOK 10']
        df_names_ok = ['OK 20', 'OK 100 Control', 'OK 10']

        processed_dfs = [process_data(df, name_ratio, name_nok, name_ok) for df, name_ratio, name_nok, name_ok in zip(dfs, df_names_ratio, df_names_nok, df_names_ok)]

        final_df = processed_dfs[0].merge(processed_dfs[1], on="Equipment").merge(processed_dfs[2], on="Equipment")  # join all dfs on 'Equipment'
        final_df['NOK (%)'] = final_df[df_names_ratio].sum(axis=1)  # compute total NOK Ratio

        fig = go.Figure()  #create a figure
        final_df.sort_values(by=['NOK (%)', 'NOK 10 (%)', 'NOK 100 (%)', 'NOK 20 (%)'], ascending=False, inplace=True)

        for column in df_names_nok:
            fig.add_trace(go.Bar(hovertemplate='%{y:.2f}', x=final_df['Equipment'], y=final_df[column], name=column, yaxis='y1', marker_color=COLOR_DICT_GLOBAL[column], opacity=0.65))
            fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=final_df['Equipment'], y=final_df[column + ' (%)'], name=column + ' (%)', yaxis='y2', marker_color=COLOR_DICT_GLOBAL[column]))

        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=final_df['Equipment'], y=final_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color='black')))
        ymax = 1.1* final_df['NOK (%)'].max()

        fig.update_layout(barmode='stack', height=400, title='<b>' + title + '</b>', hovermode="x unified", xaxis_title="Equipments")  #update layout
        fig.update_layout(yaxis=dict(title='NOK', side='left', showgrid=False), yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False, range=[0,ymax]), autosize=True, legend=dict(orientation="v", x=1.2, y=1))
        fig.update_xaxes(tick0=0, dtick=1, tickangle=315, title_standoff=30)
        return fig, fig

def overall_scrap_layout(operator_show):
    current_year = datetime.datetime.now().year
    current_week = datetime.datetime.now().isocalendar()[1]
    operator_label, equipment_label = load_operator_label(), load_equipment_label()
    current_week_list = [max(current_week-6, 1), current_week] 
    # List of years from 2023 to the current year.
    YEAR_LIST = list(range(2023, datetime.datetime.now().year + 1))

    if operator_show:
        return html.Div(children=[
            
        html.Br(),
        html.P("Data comes from database1.db.", style={'textAlign': 'center'}),

        dbc.Row([               

            ####################################################################
            # 1st Graph : NOK of 10, 20, 100 Control per week #
            ####################################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='NOK of 10, 20, 100 Control per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='NOK of 10, 20, 100 Control per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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

            ############################################################################
            # 2nd Graph : NOK (%) of 10, 20, 100 Control per Operator #
            ############################################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='NOK (%) of 10, 20, 100 Control per Operator', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='NOK (%) of 10, 20, 100 Control per Operator (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
            
            
            #############################################################################
            # 3rd Graph : NOK (%) of 10, 20, 100 Control per Equipment #
            #############################################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='NOK (%) of 10, 20, 100 Control per Equipment', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='NOK (%) of 10, 20, 100 Control per Equipment (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
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
    ], className='main_div'),
    else:
        return html.Div(children=[
            
        html.Br(),
        html.P("Data comes from database1.db.", style={'textAlign': 'center'}),

        dbc.Row([               

            ####################################################################
            # 1st Graph : NOK of 10, 20, 100 Control per week #
            ####################################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='NOK of 10, 20, 100 Control per week', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='NOK of 10, 20, 100 Control per week (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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

            #############################################################################
            # 3rd Graph : NOK (%) of 10, 20, 100 Control per Equipment #
            #############################################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='NOK (%) of 10, 20, 100 Control per Equipment', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='NOK (%) of 10, 20, 100 Control per Equipment (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 3', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Dropdown 3', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 3', options=operator_label, placeholder="All Operators", value='All'), style={'display':'none'}),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 3', options=equipment_label, placeholder="All Equipments", value = 'All')),
                            ]),
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close3", className="ml-auto")),
                ], id="modal3", size="xl"),
            ], md=6),

        ], className="mt-4"),
    ], className='main_div'),