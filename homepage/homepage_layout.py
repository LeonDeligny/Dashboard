from dash import html

from utils import PASSWORD

def home_layout():
    return html.Div(children=[
            html.P("How to use : toggle mouse on the left to open sidebar."),
            html.P("How to understand the data: In a production environment, there are differents operations or steps for manufacturing a part. The list of the different operations are denoted by 0, 10, 20, 50, 60, 100. We separate the operation 10 from the others for a more detailed analysis."),
            html.P("If a part is not a scrap it is denoted by OK, and otherwise denoted by NOK (Not OK)."),
            html.P("All graphs are dynamic and updated automatically from the database. Filter options can be applied for a more detailed analysis of the data."),
            html.P(f"Since some data may be confidential, the password {PASSWORD}"),
        ]
        )