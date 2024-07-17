"""
Module related to the layout of the micro-machining scraps.
"""

import dash_bootstrap_components as dbc

from dash import html
from dash.dependencies import Input, Output

from micro_machining.mismatches import mismatches
from micro_machining.now import register_now_callbacks, now_layout
#from micro_machining.cons import register_cons_callbacks, cons_layout
from micro_machining.week import register_week_callbacks, week_layout
from micro_machining.operator import register_operator_callbacks, operator_layout
from micro_machining.equipment import register_equipment_callbacks, equipment_layout
from micro_machining.shift import register_shift_callbacks, shift_layout
from micro_machining.weekday import register_weekday_callbacks, weekday_layout

def micro_machining_layout(operator_show):
    tabs_list = [
                dbc.Tab(label='Mismatches', tab_id='Mismatches'),
                dbc.Tab(label='Now', tab_id='Now'),
                #dbc.Tab(label='Tool', tab_id='Tool'),
                dbc.Tab(label='Trends', tab_id='Trends'),
                dbc.Tab(label='Equipment', tab_id='Equipment'),
                dbc.Tab(label='Shift', tab_id='Shift'),
                dbc.Tab(label='Weekday', tab_id='Weekday'),
            ]
    tabs_operator_list = tabs_list + [dbc.Tab(label='Operator', tab_id='Operator'),]

    if operator_show:
        return html.Div(children=[
            dbc.Tabs(id='tabs-op10',active_tab='Mismatches', 
                children=tabs_operator_list, className='custom-tabs-container'),

                html.Div(
                    id='tabs-content-op10',
                    className='custom-tabs-content'
                )
        ])
    else:
        return html.Div(children=[
            dbc.Tabs(id='tabs-op10',active_tab='Mismatches', 
                children=tabs_list, className='custom-tabs-container'),

                html.Div(
                    id='tabs-content-op10',
                    className='custom-tabs-content'
                )
        ])


def register_micro_machining_layout_callbacks(app):
    
    register_now_callbacks(app)
    #register_cons_callbacks(app)
    register_week_callbacks(app)
    register_operator_callbacks(app)
    register_equipment_callbacks(app)
    register_shift_callbacks(app)
    register_weekday_callbacks(app)

    @app.callback(
        Output('tabs-content-op10', 'children'),
        [
        Input('tabs-op10', 'active_tab'),
        Input('url', 'search'),
        ]
    )
    def render_content_op10(tab, search):
        if tab == 'Mismatches': return mismatches()
        elif (tab == 'Now') and (search  == "?admin"): return now_layout(operator_show = True)
        #elif (tab == 'Tool') and (search  == "?admin"): return cons_layout(operator_show = True)
        elif (tab == 'Trends') and (search  == "?admin"): return week_layout(operator_show = True)
        elif (tab == 'Operator') and (search  == "?admin"): return operator_layout(operator_show = True)
        elif (tab == 'Equipment') and (search  == "?admin"): return equipment_layout(operator_show = True)
        elif (tab == 'Shift') and (search  == "?admin"): return shift_layout(operator_show = True)
        elif (tab == 'Weekday') and (search  == "?admin"): return weekday_layout(operator_show = True)
        elif tab == 'Now' : return now_layout(operator_show = False)
        #elif tab == 'Tool': return cons_layout(operator_show = False)
        elif tab == 'Trends': return week_layout(operator_show = False)
        elif tab == 'Operator': return operator_layout(operator_show = False)
        elif tab == 'Equipment': return equipment_layout(operator_show = False)
        elif tab == 'Shift': return shift_layout(operator_show = False)
        elif tab == 'Weekday': return weekday_layout(operator_show = False)