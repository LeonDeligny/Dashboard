"""
Module related to the layout of the Post Processing scraps.
"""

import dash_bootstrap_components as dbc, dash.dependencies as ddp

from dash import html

from post_processing.ofa_overall import register_ofa_overall_callbacks, ofa_overall_layout
from post_processing.pre_deburring import register_pre_deburring_callbacks, pre_deburring_layout
from post_processing.deburring import register_deburring_callbacks, deburring_layout
from post_processing.dimensional import register_dimensional_callbacks, dimensional_layout
from post_processing.sorting import register_sorting_callbacks, sorting_layout
from post_processing.release_AQL import register_release_AQL_callbacks, release_AQL_layout
from post_processing.release import register_release_callbacks, release_layout
from post_processing.visual import register_visual_callbacks, visual_layout
from post_processing.visual_AQL import register_visual_AQL_callbacks, visual_AQL_layout

def post_processing_layout():
    return html.Div(children=[dbc.Tabs(id='tabs-pp', active_tab='Overall', children=[
                                    
                                    dbc.Tab(label='Overall', tab_id='Overall'),

                                    dbc.Tab(label='0: Pre-Deburring', tab_id='Pre-Deburring',),
                                    dbc.Tab(label='20: Deburring', tab_id='Deburring',),
                                    dbc.Tab(label='50: Dimensional AQL', tab_id='Dimensional AQL'),
                                    dbc.Tab(label='60: Dimensional 100%', tab_id='Dimensional 100%'),

                                    dbc.Tab(label='71: Release AQL', tab_id='Release AQL'),
                                    dbc.Tab(label='72: Release 100%', tab_id='Release 100%'),

                                    dbc.Tab(label='100: Visual', tab_id='Visual Control'),
                                    dbc.Tab(label='101: Visual AQL', tab_id='Visual AQL'),

                                ], className='custom-tabs-container'),
            html.Div(
                id='tabs-content-pp',
                className='custom-tabs-content',
            )
    ])

def register_post_processing_layout_callbacks(app):

    register_ofa_overall_callbacks(app)
    register_pre_deburring_callbacks(app)
    register_deburring_callbacks(app)
    register_dimensional_callbacks(app)
    register_sorting_callbacks(app)
    register_release_AQL_callbacks(app)
    register_release_callbacks(app)
    register_visual_callbacks(app)
    register_visual_AQL_callbacks(app)

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
        elif (tab == 'Pre-Deburring') and (search == '?admin'):
            return pre_deburring_layout(operator_show = True)
        elif (tab == 'Deburring') and (search == '?admin'):
            return deburring_layout(operator_show = True)
        elif (tab == 'Dimensional AQL') and (search == '?admin'):
            return dimensional_layout(operator_show = True)
        elif (tab == 'Dimensional 100%') and (search == '?admin'):
            return sorting_layout(operator_show = True)
        elif (tab == 'Release AQL') and (search == '?admin'):
            return release_AQL_layout(operator_show = True)
        elif (tab == 'Release 100%') and (search == '?admin'):
            return release_layout(operator_show = True)
        elif (tab == 'Visual Control') and (search == '?admin'):
            return visual_layout(operator_show = True)
        elif (tab == 'Visual AQL') and (search == '?admin'):
            return visual_AQL_layout(operator_show = False)
        elif tab == 'Pre-Deburring':
            return pre_deburring_layout(operator_show = False)
        elif tab == 'Deburring':
            return deburring_layout(operator_show = False)
        elif tab == 'Dimensional AQL':
            return dimensional_layout(operator_show = False)
        elif tab == 'Dimensional 100%':
            return sorting_layout(operator_show = False)
        elif tab == 'Release AQL':
            return release_AQL_layout(operator_show = False)
        elif tab == 'Release 100%':
            return release_layout(operator_show = False)
        elif tab == 'Visual Control':
            return visual_layout(operator_show = False)
        elif tab == 'Visual AQL':
            return visual_AQL_layout(operator_show = False)