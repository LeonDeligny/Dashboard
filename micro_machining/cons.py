"""
Module related to the different graphs in Micro-Machining > Tool.

Database name : hsma2.
Corresponding CSV files : uu_tracking.csv.
"""

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import calendar, datetime

from dash import html, dcc
from dash.dependencies import Input, Output

from smc_load import load_df_smc, extract_cons_tool, load_color_dict_operator, load_cons_list
from generate_plots import generate_bar_plot
from filters import filter_dataframe, generate_title
from dicts import CustomCard, COLOR_DICT_EQUIPMENT, EQUIPMENT_TYPES, WEEK_DICT, EQUIPMENTS_PER_OPERATOR_LIST, EQUIPMENTS_PER_OPERATOR_LABEL_LIST, SHIFT_LABEL_LIST, NOK_SORTING_LIST, WEEKDAY_LABEL_LIST
from utils import load_operator_label, load_equipment_label


def register_cons_callbacks(app):

    ##################################################
    # 1st Graph : Machining: NOK by Type per N° CONS #
    ##################################################

    @app.callback(
        [
        Output('Machining: NOK by Type per N° CONS', 'figure'),
        Output('Machining: NOK by Type per N° CONS (bis)', 'figure'),
        ],
        [
        Input('Year Selector 1', 'value'),
        Input('Week Selector 1', 'value'),
        Input('Sort Selector 1', 'value'),
        Input('Operator Dropdown 1', 'value'),
        Input('Equipment Dropdown 1', 'value'),
        Input('Shift Dropdown 1', 'value'),
        Input('Weekday Dropdown 1', 'value'),
        Input('Equipments Per Operator Dropdown 1', 'value'),
        ]
    )
    def update_1(selected_year, selected_week, sort_value, operator_value, equipment_value, shift_value, weekday_value, equipment_per_operator):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Operator': operator_value,'Equipment': equipment_value, 'Shift': shift_value, 'Weekday': weekday_value, 'Equipments per Operator': equipment_per_operator}
        df_smc = load_df_smc(input_values)
        df_smc_cons = extract_cons_tool(df_smc)
        LIST_CONS_LISTS = load_cons_list(df_smc)
        filtered_df = filter_dataframe(df_smc, input_values)
        filtered_df_CONS = filter_dataframe(df_smc_cons, input_values)
        title = generate_title(input_values, "Machining: NOK by Type per N° CONS")

        df_CONS = filtered_df_CONS.groupby('N° CONS')[['C', 'O', 'U']].sum().reset_index()
        df_CONS['OK CONS'] = 0
        df_CONS['NOK CONS'] = 0

        for equip, CONS_list in zip(EQUIPMENT_TYPES, LIST_CONS_LISTS):
            equip_df = filtered_df[filtered_df['Equipment'].str.contains(equip)]
            total_ok = equip_df['OK'].sum()
            total_nok = equip_df['NOK'].sum()
            for cons in CONS_list:
                df_CONS.loc[df_CONS['N° CONS']==str(cons), 'OK CONS'] += total_ok
                df_CONS.loc[df_CONS['N° CONS']==str(cons), 'NOK CONS'] += total_nok

        df_CONS['Total'] = df_CONS[['C', 'O', 'U']].sum(axis=1)
        df_CONS['C (%)'] = (df_CONS['C'] / (df_CONS['OK CONS']+df_CONS['NOK CONS'])) * 100
        df_CONS['O (%)'] = (df_CONS['O'] / (df_CONS['OK CONS']+df_CONS['NOK CONS'])) * 100
        df_CONS['U (%)'] = (df_CONS['U'] / (df_CONS['OK CONS']+df_CONS['NOK CONS'])) * 100
        df_CONS['NOK (%)'] = df_CONS['C (%)'] + df_CONS['O (%)'] + df_CONS['U (%)']

        if sort_value == 'NOK': df_CONS.sort_values('Total', ascending=False, inplace=True)
        elif sort_value == 'NOK (%)': df_CONS.sort_values('NOK (%)', ascending=False, inplace=True)
        elif sort_value == 'C (%)': df_CONS.sort_values('C (%)', ascending=False, inplace=True)
        elif sort_value == 'O (%)': df_CONS.sort_values('O (%)', ascending=False, inplace=True)
        elif sort_value == 'U (%)': df_CONS.sort_values('U (%)', ascending=False, inplace=True)
        elif sort_value == 'alphabet': df_CONS.sort_values('N° CONS', ascending=True, inplace=True)
        del df_CONS['Total']
        fig = generate_bar_plot(df_CONS, 'N° CONS', ['U', 'O', 'C'], title, 'N° CONS', 'NOK by Type')
        
        return fig, fig

    ######################################################
    # 2nd Graph : Machining: NOK by Operator per N° CONS #
    ######################################################

    @app.callback(
        [
        Output('Machining: NOK by Operator per N° CONS', 'figure'),
        Output('Machining: NOK by Operator per N° CONS (bis)', 'figure'),
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
        df_smc_cons = extract_cons_tool(df_smc)
        filtered_df = filter_dataframe(df_smc_cons, input_values)
        title = generate_title(input_values, "Machining: NOK by Operator per N° CONS")

        filtered_df['NOK'] = filtered_df[['C', 'O', 'U']].sum(axis=1)
        df_Operator = filtered_df.groupby(['N° CONS', 'Operator'])[['NOK']].sum().reset_index()

        fig = go.Figure()
        unique_hues = df_Operator['Operator'].unique()
        COLOR_DICT_OPERATOR = load_color_dict_operator(df_smc)
        for hue in unique_hues:
            df_subset = df_Operator[df_Operator['Operator'] == hue]
            fig.add_trace(go.Bar(x=df_subset['N° CONS'], y=df_subset['NOK'], name=str(hue), opacity=0.65, marker=dict(color=COLOR_DICT_OPERATOR.get(hue, 'black')), hovertemplate='%{y:.0f}'))
        fig.update_xaxes(tick0=0, dtick=1, title_standoff=30)
        fig.update_layout(height=400, autosize=False, legend=dict(orientation="v", x=1.2, y=1), title='<b>' + title + '</b>', title_y=0.95, barmode='stack', xaxis_title='N° CONS', yaxis_title='NOK by Operator', xaxis_tickangle=315, hovermode="x unified")
        
        return fig, fig

    ######################################################
    # 3rd Graph : Machining: NOK (%) by Type per N° CONS #
    ######################################################

    @app.callback(
        [
        Output('Machining: NOK (%) by Type per N° CONS', 'figure'),
        Output('Machining: NOK (%) by Type per N° CONS (bis)', 'figure'),
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
        df_smc_cons = extract_cons_tool(df_smc)
        LIST_CONS_LISTS = load_cons_list(df_smc)
        filtered_df = filter_dataframe(df_smc, input_values)
        filtered_df_CONS = filter_dataframe(df_smc_cons, input_values)
        title = generate_title(input_values, "Machining: NOK (%) by Type per N° CONS")

        df_CONS = filtered_df_CONS.groupby('N° CONS')[['C', 'O', 'U']].sum().reset_index()
        df_CONS['OK CONS'] = 0
        df_CONS['NOK CONS'] = 0

        for equip, CONS_list in zip(EQUIPMENT_TYPES, LIST_CONS_LISTS):
            equip_df = filtered_df[filtered_df['Equipment'].str.contains(equip)]
            total_ok = equip_df['OK'].sum()
            total_nok = equip_df['NOK'].sum()
            for cons in CONS_list:
                df_CONS.loc[df_CONS['N° CONS']==str(cons), 'OK CONS'] += total_ok
                df_CONS.loc[df_CONS['N° CONS']==str(cons), 'NOK CONS'] += total_nok

        df_CONS['Total'] = df_CONS[['C', 'O', 'U']].sum(axis=1)
        df_CONS['NOK (%)'] = (df_CONS['Total'] / (df_CONS['OK CONS']+df_CONS['NOK CONS'])) * 100
        df_CONS['C (%)'] = (df_CONS['C'] / (df_CONS['OK CONS']+df_CONS['NOK CONS'])) * 100
        df_CONS['O (%)'] = (df_CONS['O'] / (df_CONS['OK CONS']+df_CONS['NOK CONS'])) * 100
        df_CONS['U (%)'] = (df_CONS['U'] / (df_CONS['OK CONS']+df_CONS['NOK CONS'])) * 100
        df_CONS.sort_values('N° CONS', ascending=True, inplace=True)
        ymax = 1.1* df_CONS['NOK (%)'].max()
        fig = go.Figure()
        for i in df_CONS.index:
            fig.add_trace(go.Scatterpolar(r=[df_CONS.loc[i, 'NOK (%)'], df_CONS.loc[i, 'C (%)'], df_CONS.loc[i, 'O (%)'], df_CONS.loc[i, 'U (%)']], theta=['NOK (%)', 'C (%)', 'O (%)', 'U (%)'], fill='toself', name=df_CONS.loc[i, 'N° CONS']))
        fig.update_layout(height=400, polar=dict(radialaxis=dict(visible=True, range=[0, ymax])), showlegend=True, title='<b>' + title + '</b>')
        
        return fig, fig

    #######################################################
    # 4th Graph : Machining: NOK by Equipment per N° CONS #
    #######################################################

    @app.callback(
        [
        Output('Machining: NOK by Equipment per N° CONS', 'figure'),
        Output('Machining: NOK by Equipment per N° CONS (bis)', 'figure'),
        ],
        [
        Input('Year Selector 4', 'value'),
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
        title = generate_title(input_values, "Machining: NOK by Equipment per N° CONS")

        filtered_df['NOK'] = filtered_df[['C', 'O', 'U']].sum(axis=1)
        df_Equipment = filtered_df.groupby(['N° CONS', 'Equipment'])[['NOK']].sum().reset_index()

        fig = go.Figure()
        unique_hues = df_Equipment['Equipment'].unique()
        for hue in unique_hues:
            df_subset = df_Equipment[df_Equipment['Equipment'] == hue]
            fig.add_trace(go.Bar(x=df_subset['N° CONS'], y=df_subset['NOK'], name=str(hue), opacity=0.65, marker=dict(color=COLOR_DICT_EQUIPMENT.get(hue[:4], 'black')), hovertemplate='%{y:.0f}'))
        fig.update_xaxes(tick0=0, dtick=1, title_standoff=30)
        fig.update_layout(height=400, autosize=False, legend=dict(orientation="v", x=1.2, y=1), title='<b>' + title + '</b>', title_y=0.95, barmode='stack', xaxis_title='N° CONS', yaxis_title='NOK by Equipment', xaxis_tickangle=315, hovermode="x unified")
        
        return fig, fig

def cons_layout(operator_show):
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
            # 1st Graph : Machining: NOK by Type per N° CONS #
            ##################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK by Type per N° CONS', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK by Type per N° CONS (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 1', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Selector 1', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Sort Selector 1', options=NOK_SORTING_LIST, value='NOK (%)')),
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
            # 2nd Graph : Machining: NOK by Operator per N° CONS #
            ######################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK by Operator per N° CONS', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK by Operator per N° CONS (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
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
            
            ######################################################
            # 3rd Graph : Machining: NOK (%) by Type per N° CONS #
            ######################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK (%) by Type per N° CONS', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK (%) by Type per N° CONS (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
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

            #######################################################
            # 4th Graph : Machining: NOK by Equipment per N° CONS #
            ####################################################### 

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK by Equipment per N° CONS', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open4", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK by Equipment per N° CONS (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 4', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Selector 4', options=YEAR_LIST, value=current_year)),
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
        ], className="mt-4"),
    ], className='main_div'),

    else:
        return html.Div(children=[

        html.Br(),
        html.P("Data comes from Intranet."),

        dbc.Row([               

            ##################################################
            # 1st Graph : Machining: NOK by Type per N° CONS #
            ##################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK by Type per N° CONS', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open1", className="mr-2"),
                    ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK by Type per N° CONS (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 1', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Selector 1', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Sort Selector 1', options=NOK_SORTING_LIST, value='NOK (%)')),
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
            # 3rd Graph : Machining: NOK (%) by Type per N° CONS #
            ######################################################

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK (%) by Type per N° CONS', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open3", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK (%) by Type per N° CONS (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 3', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Selector 3', options=YEAR_LIST, value=current_year)),
                                dbc.Col(dcc.Dropdown(id='Operator Dropdown 3', options=operator_label, placeholder="All Operators", value='All'), style={'display': 'none'}),
                                dbc.Col(dcc.Dropdown(id='Equipment Dropdown 3', options=equipment_label, placeholder="All Equipments", value = 'All')),
                                dbc.Col(dcc.Dropdown(id='Shift Dropdown 3', options=SHIFT_LABEL_LIST, value='All', placeholder="All shifts"),),
                            ]),
                            dcc.Dropdown(id='Weekday Dropdown 3', options=WEEKDAY_LABEL_LIST, multi=True, value=list(calendar.day_name)),
                            dbc.Col(dcc.Dropdown(id='Equipments Per Operator Dropdown 3', options=EQUIPMENTS_PER_OPERATOR_LABEL_LIST, multi=True, placeholder="All Equipments/Operator", value=EQUIPMENTS_PER_OPERATOR_LIST), style={'display': 'none'})
                        ]),
                    ),
                    dbc.ModalFooter(dbc.Button("Close", id="close3", className="ml-auto")),
                ], id="modal3", size="xl"),
            ], md=6),

        ], className="mt-4"),
            
        dbc.Row([
            
            #######################################################
            # 4th Graph : Machining: NOK by Equipment per N° CONS #
            ####################################################### 

            dbc.Col([
                CustomCard([
                    dbc.Col(dcc.Graph(id='Machining: NOK by Equipment per N° CONS', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                    dbc.Button("Open filter options", id="open4", className="mr-2"),
                ]),
                dbc.Modal([
                    dbc.ModalHeader("Filter Options"),
                    dbc.ModalBody(
                        CustomCard([
                            dcc.Graph(id='Machining: NOK by Equipment per N° CONS (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"margin": "auto", "display": "block"}),
                            html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 4', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                            dbc.Row([
                                dbc.Col(dcc.Dropdown(id='Year Selector 4', options=YEAR_LIST, value=current_year)),
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
        ], className="mt-4"),
    ], className='main_div'),