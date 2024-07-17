"""
Module related to Micro-Machining > Mismatches.

Database name : hsma2.
Corresponding CSV files : uu_tracking.csv.
"""

import datetime

import pandas as pd

from dash import html
from dash import dash_table

from smc_load import load_df_OFA_mismatch

def mismatches():
    df_OFA_mismatch = load_df_OFA_mismatch()
    current_year = datetime.datetime.now().year

    return html.Div(children=[
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df_OFA_mismatch.columns],
        data=df_OFA_mismatch.to_dict('records'),
        style_data={'whiteSpace': 'normal'},
        style_cell={'height': 'auto'},
        style_cell_conditional=[
            {'if': {'column_id': c}, 'backgroundColor': 'white', 'color': 'black'} for c in df_OFA_mismatch.columns],
        style_data_conditional=[
            {'if': {'row_index': 'odd'},'backgroundColor': 'white'},
            {'if': {'filter_query': '{{Year}} = {}'.format(current_year)}, 'backgroundColor': 'red', 'color': 'white'},
        ],
        style_header={
            'backgroundColor': 'white',
            'color': 'black',
            'fontWeight': 'bold',
            },
        ),
    ])
