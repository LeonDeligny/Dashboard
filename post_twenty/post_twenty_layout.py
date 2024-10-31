"""
Module related to the layout of the Post Processing scraps.
"""

import dash_bootstrap_components as dbc, dash.dependencies as ddp

from dash import html

from post_twenty.ofa_overall import register_ofa_overall_callbacks, ofa_overall_layout
from post_twenty.zero import register_zero_callbacks, zero_layout
from post_twenty.twenty import register_twenty_callbacks, twenty_layout
from post_twenty.fifty import register_fifty_callbacks, fifty_layout
from post_twenty.sixty import register_sixty_callbacks, sixty_layout
from post_twenty.hundred import register_hundred_callbacks, hundred_layout
from utils import PASSWORD

def post_twenty_layout():
    return html.Div(children=[dbc.Tabs(id='tabs-pp', active_tab='Overall', children=[
                                    
                                    dbc.Tab(label='Overall', tab_id='Overall'),

                                    dbc.Tab(label='0: 0', tab_id='0',),
                                    dbc.Tab(label='20: 20', tab_id='20'),
                                    dbc.Tab(label='50: 50', tab_id='50'),
                                    dbc.Tab(label='60: 60', tab_id='60'),
                                    dbc.Tab(label='100: 100', tab_id='100'),

                                ], className='custom-tabs-container'),
            html.Div(
                id='tabs-content-pp',
                className='custom-tabs-content',
            )
    ])

def register_post_twenty_layout_callbacks(app):

    register_ofa_overall_callbacks(app)
    register_zero_callbacks(app)
    register_twenty_callbacks(app)
    register_fifty_callbacks(app)
    register_sixty_callbacks(app)
    register_hundred_callbacks(app)

    @app.callback(
        ddp.Output('tabs-content-pp', 'children'),
        [ 
        ddp.Input('tabs-pp', 'active_tab'),
        ddp.Input('url', 'search'),
        ]
    )
    def render_content_pp(tab, search):
        if tab == 'Overall':
            return ofa_overall_layout()
        elif (tab == '0') and (search == PASSWORD):
            return zero_layout(operator_show = True)
        elif (tab == '20') and (search == PASSWORD):
            return twenty_layout(operator_show = True)
        elif (tab == '50') and (search == PASSWORD):
            return fifty_layout(operator_show = True)
        elif (tab == '60') and (search == PASSWORD):
            return sixty_layout(operator_show = True)
        elif (tab == '100') and (search == PASSWORD):
            return hundred_layout(operator_show = True)
        elif tab == '0':
            return zero_layout(operator_show = False)
        elif tab == '20':
            return twenty_layout(operator_show = False)
        elif tab == '50':
            return fifty_layout(operator_show = False)
        elif tab == '60':
            return sixty_layout(operator_show = False)
        elif tab == '100':
            return hundred_layout(operator_show = False)