"""
Module related to the different graphs in Post Processing > OFA Overall.

Database name : PCERP (Oracle) & hsma2.
"""

import datetime

import dash_bootstrap_components as dbc, plotly.graph_objects as go, pandas as pd

from dash import html, dcc
from dash.dependencies import Input, Output

from pp_load import load_pp_data
from erp_load import df_erp_load
from generate_plots import generate_grouped_bar_plot
from filters import filter_dataframe, generate_title
from dicts import CustomCard, COLOR_DICT_EQUIPMENT, WEEK_DICT, OPERATIONS_LIST, COLOR_DICT
from utils import load_operator_label, load_equipment_label, extract_type

def register_ofa_overall_callbacks(app):

    ###################################################################
    # 1st Graph : NOK (%) from each Machining Equipment per Operation #
    ###################################################################

    @app.callback(
        [
        Output('NOK (%) from each Machining Equipment per Op', 'figure'),
        Output('NOK (%) from each Machining Equipment per Op (bis)', 'figure'),
        ],
        [
        Input('Year Dropdown 1', 'value'),
        Input('Week Selector 1', 'value'),
        Input('Equipment Dropdown 1', 'value'),
        ]
    )
    def update_1(selected_year, selected_week, equipment_value):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': equipment_value}
        df_erp = df_erp_load()
        title = generate_title(input_values, "NOK (%) from each Machining Equipment per Op")

        df_erp['Operation'] = pd.Categorical(df_erp['Operation'], categories=OPERATIONS_LIST, ordered=True)
        #df_erp = df_erp[df_erp['Operation'].isin(OPERATIONS_LIST)]

        mapping = df_erp[df_erp['Operation'] == 'Machining'].set_index('OFA')['Equipment'].to_dict()
        df_erp['Equipment'] = df_erp['OFA'].map(mapping).where(df_erp['OFA'].isin(mapping), df_erp['Equipment'])
        final_df = filter_dataframe(df_erp, input_values)
        final_df = final_df.groupby(['Operation', 'Equipment']).agg({'NOK': 'sum', 'OK': 'sum'}).reset_index()
        final_df['NOK (%)'] = 100*(final_df['NOK'] / (final_df['OK'] + final_df['NOK']))

        fig = go.Figure()
        for equip, grp in final_df.groupby('Equipment'):
            fig.add_trace(go.Bar(hovertemplate='%{y:.2f}', x = grp['Operation'], y = grp['OK'], name=equip, yaxis='y1', marker_color=COLOR_DICT_EQUIPMENT[equip[:4]], opacity=0.65))
            if equip[:4] == 'A620':
                fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', x = grp['Operation'], y = grp['NOK (%)'], mode='lines+markers', name=equip + ' (%)', yaxis='y2', marker_color=COLOR_DICT_EQUIPMENT[equip[:4] + ' (%)'], visible='legendonly' ))
            else:
                fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', x = grp['Operation'], y = grp['NOK (%)'], mode='lines+markers', name=equip + ' (%)', yaxis='y2', marker_color=COLOR_DICT_EQUIPMENT[equip[:4] + ' (%)'] ))

        ymax = 1.1* final_df['NOK (%)'].max()
        fig.update_xaxes(type='category', categoryorder='array', categoryarray=OPERATIONS_LIST)
        fig.update_layout(barmode='stack', height=400, title='<b>' + title + '</b>', hovermode="x unified", xaxis_title="Operations"),
        fig.update_layout(yaxis=dict(title='OK', side='left'), yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False, range=[0,ymax]), autosize=True, legend=dict(orientation="v", x=1.2, y=1))
        fig.update_xaxes(tick0=0, dtick=1, tickangle=315, title_standoff=30)
        return fig, fig

    ###################################################################
    # 2nd Graph : NOK (%) from each Machining Equipment per Operation #
    ###################################################################

    @app.callback(
        [
        Output('NOK (%) of each Type per Op', 'figure'),
        Output('NOK (%) of each Type per Op (bis)', 'figure'),
        ],
        [
        Input('Year Dropdown 2', 'value'),
        Input('Week Selector 2', 'value'),
        Input('Equipment Dropdown 2', 'value'),
        ]
    )
    def update_2(selected_year, selected_week, equipment_value):
        input_values = {'Year': selected_year, 'Week': selected_week, 'Equipment': equipment_value}
        title = generate_title(input_values, "NOK (%) of each Type per Op")

        df_pp, _ = load_pp_data(input_values)
        df_pp_type = extract_type(df_pp)

        filtered_df = filter_dataframe(df_pp, input_values)
        filtered_df_type = filter_dataframe(df_pp_type, input_values)

        filtered_df_overall = filtered_df_type.groupby(['Operation', 'Type'])[['NOK by Type']].sum().reset_index()
        filtered_df['NOK (%)'] = 100*(filtered_df['NOK'] / (filtered_df['OK'] + filtered_df['NOK']))

        fig = generate_grouped_bar_plot(filtered_df_overall, 'Operation', 'Type', title, 'Operations', 'NOK by Type')
        fig.update_xaxes(type='category', categoryorder='array', categoryarray=OPERATIONS_LIST)

        all_weeks = OPERATIONS_LIST
        OK_Total = filtered_df.groupby('Operation')['OK'].sum()
        NOK_Total = filtered_df.groupby('Operation')['NOK'].sum()

        OK_Total = OK_Total.reindex(all_weeks, fill_value=1)
        NOK_Total = NOK_Total.reindex(all_weeks, fill_value=0)
        NOK_Ratio = (NOK_Total / (OK_Total + NOK_Total)) * 100
        
        team_ratio_df = pd.DataFrame({'Operation': all_weeks, 'NOK (%)': NOK_Ratio.values})
        fig.add_trace(go.Scatter(hovertemplate='%{y:.2f}', mode="markers+lines",  x=team_ratio_df['Operation'], y=team_ratio_df['NOK (%)'], name='NOK (%)', yaxis='y2', line=dict(color=COLOR_DICT['NOK (%)'])))
        if NOK_Ratio.size > 0:
            ymax = 1.1* NOK_Ratio.values.max()
            fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', range=[0, ymax], overlaying='y', showgrid=False))
        else: fig.update_layout(yaxis2=dict(title='NOK (%)', side='right', overlaying='y', showgrid=False))


        return fig, fig



def ofa_overall_layout():
    current_year = datetime.datetime.now().year
    current_week = datetime.datetime.now().isocalendar()[1]
    equipment_label = load_equipment_label()
    current_week_list = [current_week, current_week]
    # List of years from 2023 to the current year.
    YEAR_LIST = list(range(2023, datetime.datetime.now().year + 1))

    return html.Div(children=[

    html.Br(),
    html.P("Left graph's data comes from ERP, and right graph's data comes from Intranet."),
     
    dbc.Row([               

        ############################################################
        # 1st Graph : NOK (%) from each Machining Equipment per Op #
        ############################################################

        dbc.Col([
            CustomCard([
                dbc.Col(dcc.Graph(id='NOK (%) from each Machining Equipment per Op', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                dbc.Button("Open filter options", id="open1", className="mr-2"),
                ]),
            dbc.Modal([
                dbc.ModalHeader("Filter Options"),
                dbc.ModalBody(
                    CustomCard([
                        dcc.Graph(id='NOK (%) from each Machining Equipment per Op (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                        html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 1', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                        dbc.Row([
                            dbc.Col(dcc.Dropdown(id='Year Dropdown 1', options=YEAR_LIST, value=current_year)),
                            dbc.Col(dcc.Dropdown(id='Equipment Dropdown 1', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                        ]),
                    ]),
                ),
                dbc.ModalFooter(dbc.Button("Close", id="close1", className="ml-auto"))
            ], id="modal1", size="xl",),
        ], md=6),
    
        #########################################################
        # 2nd Graph : NOK (%) of each Type per Op #
        #########################################################

        dbc.Col([
            CustomCard([
                dbc.Col(dcc.Graph(id='NOK (%) of each Type per Op', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}), className='p-0', style={"flexGrow": "1"}),
                dbc.Button("Open filter options", id="open2", className="mr-2"),
                ]),
            dbc.Modal([
                dbc.ModalHeader("Filter Options"),
                dbc.ModalBody(
                    CustomCard([
                        dcc.Graph(id='NOK (%) of each Type per Op (bis)', clickData=None, config={'scrollZoom':True, 'displayModeBar': False}, style={"flexGrow": "1"}),
                        html.Label(["Week Selector", dcc.RangeSlider(id='Week Selector 2', min=1, max=52, step=1, value=current_week_list, marks=WEEK_DICT)], style={'marginLeft': '20px', 'fontWeight': 'bold'}),
                        dbc.Row([
                            dbc.Col(dcc.Dropdown(id='Year Dropdown 2', options=YEAR_LIST, value=current_year)),
                            dbc.Col(dcc.Dropdown(id='Equipment Dropdown 2', options=equipment_label, placeholder="All Equipments", value = 'All'), ),
                        ]),
                    ]),
                ),
                dbc.ModalFooter(dbc.Button("Close", id="close2", className="ml-auto"))
            ], id="modal2", size="xl",),
        ], md=6),

    ], className="mt-4"),
], className='main_div'),