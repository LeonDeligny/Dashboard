import networkx as nx
import datetime

from dash import html

from dicts import ILOT_DICT

def home_layout():
    return html.Div(children=[
            html.P("How to use : Sidebar on the left, toggle mouse on the left of the webpage and click on Scraps. Micro-Machining corresponds to op10, Post-processing correspond to the rest of the Operations."),
            html.Br(),
            html.P("For any inquiries, go see DWO or JZU."),
            html.Br(),
            html.P("Last Updated : 17th of July 2024."),
        ])


def create_graph(df_smc, equipment_lists):
    G = nx.Graph()
    filtered_df = df_smc[(df_smc['Year'] == datetime.datetime.now().year) & (df_smc['Week'] == datetime.datetime.now().isocalendar()[1])]

    for operator in filtered_df['Operator'].unique().tolist():
        G.add_node(operator, label=operator)
    for equipment_list in equipment_lists:
        df_ilot = filtered_df[filtered_df['Equipment'].isin(ILOT_DICT[equipment_list])]
        for weekday in filtered_df['Weekday'].unique():
            df_weekday = df_ilot[df_ilot['Weekday'] == weekday]
            for shift in df_weekday['Shift'].unique():
                df_shift = df_weekday[df_weekday['Shift'] == shift]
                for operator in df_shift['Operator'].unique():
                    if len(df_shift[df_shift['Operator'] == operator]['Equipment'].unique()) > 1:
                        if G.has_edge(operator, operator):
                            G[operator][operator]['weight'] += 1
                        else:
                            G.add_edge(operator, operator, weight = 1)
                for operator1 in df_shift['Operator'].unique():
                    for operator2 in df_shift['Operator'].unique():
                        if operator1 != operator2:
                            if G.has_edge(operator1, operator2):
                                G[operator1][operator2]['weight'] += 1
                            else:
                                G.add_edge(operator1, operator2, weight = 1)
    
    return G
