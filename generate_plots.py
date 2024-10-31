import plotly.graph_objects as go, pandas as pd

from smc_load import load_color_dict_operator

from dicts import SHIFT_COLOR_DICT, COLOR_DICT_EQUIPMENT

from utils import returns_defaults_color_dict

def generate_trace(df_, x, hues, color_dict, trace_type='bar'):
    traces = []
    for hue in hues:
        if trace_type == 'bar':
            traces.append(go.Bar(x=df_[x], y=df_[hue], name=str(hue), hovertemplate='%{y:.0f}', marker_color=color_dict[hue], opacity=0.65, width=0.8))
        elif trace_type == 'scatter':
            traces.append(go.Scatter(x=df_[x], y=df_[hue], yaxis='y2', name=hue+' (%)', mode="markers+lines", hovertemplate='%{y:.2f}', line=dict(color=color_dict[hue+' (%)']), visible='legendonly'))
    return traces

def add_ceil_trace(fig, df_, x, title, ceil_value, color='red'):
    fig.add_trace(go.Scatter(x=df_[x], y=[ceil_value]*len(df_[x]), yaxis='y2', name='Ceil NOK (%)', mode="lines", hovertemplate='%{y:.2f}', line=dict(color=color, dash='dash'), visible='legendonly'))

def update_layout(x, df_, fig, title, xlabel, ylabel, xlabel_rotation, max_value=None):
    layout = dict(
        height=400,
        autosize=False,
        legend=dict(orientation="v", x=1.2, y=1),
        title=f'<b>{title}</b>',
        title_y=0.95,
        barmode='stack',
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        xaxis_tickangle=xlabel_rotation,
        hovermode="x unified",
    )
    if max_value:
        layout['yaxis2'] = dict(title='NOK (%)', side='right', range=[0, 1.1*max_value], overlaying='y', showgrid=False)
    fig.update_layout(**layout)

def generate_grouped_bar_plot(df_, x, hue_col, title, xlabel, ylabel, xlabel_rotation=315, filtered_df=False):
    fig = go.Figure()
    if hue_col == 'Operator':
        unique_hues = filtered_df[hue_col].unique()
        for hue in unique_hues:
            df_subset = filtered_df[filtered_df[hue_col] == hue]
            color = load_color_dict_operator(df_subset).get(hue, 'black')
            fig.add_trace(go.Bar(x=df_subset[x], y=df_subset[ylabel], name=str(hue), opacity=0.65, marker=dict(color=color), hovertemplate='%{y:.0f}', width=0.8))
    else:
        unique_hues = df_[hue_col].unique()
        color_dict = {
            'Shift': SHIFT_COLOR_DICT,
            'Equipment': COLOR_DICT_EQUIPMENT,
            'Type': returns_defaults_color_dict()
        }.get(hue_col, {})
        for hue in unique_hues:
            df_subset = df_[df_[hue_col] == hue]
            color = color_dict.get(hue[:4] if hue_col == 'Equipment' else hue, 'black')
            fig.add_trace(go.Bar(x=df_subset[x], y=df_subset[ylabel], name=str(hue), opacity=0.65, marker=dict(color=color), hovertemplate='%{y:.0f}', width=0.8))
    
    if "N° CONS" not in title and "60" not in title:
        ceil_dict = {
            "20": 1,
            "Retoucher": 1,
            "Condtn": 0.1,
            "Trovalisation": 0.1,
            "Dimensionnel": 0.1,
            "60": 0.1,
            "Lavage": 0.1,
            "100 Control": 3.5
        }
        y_line = ceil_dict.get(next((key for key in ceil_dict if key in title), ''), 5)
        add_ceil_trace(fig, df_, x, title, y_line)
    update_layout(x, df_, fig, title, xlabel, ylabel, xlabel_rotation)
    fig.update_xaxes(tick0=0, dtick=1, title_standoff=30)
    if pd.api.types.is_integer(df_[x]):
        fig.update_xaxes(tick0=0, dtick=1, title_standoff=30, range=[df_[x].min(), df_[x].max()])

    return fig

def generate_bar_plot_no_hues(df_, x, title, xlabel, ylabel, xlabel_rotation=315):
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_[x],
        y=df_[ylabel],
        name=ylabel,
        marker_color='indianred',
        width=0.8
    ))
    update_layout(x, df_, fig, title, xlabel, ylabel, xlabel_rotation, None)
    fig.update_xaxes(tick0=0, dtick=1)
    if pd.api.types.is_integer(df_[x]):
        fig.update_xaxes(tick0=0, dtick=1, range=[df_[x].min(), df_[x].max()])

    return fig

def generate_custom_bar_plot(df, x, hue_col, title, xlabel, ylabel, xlabel_rotation=315):
    fig = go.Figure()
    unique_hues = df[hue_col].unique()
    color_dict = returns_defaults_color_dict()

    for hue in unique_hues:
        df_subset = df[df[hue_col] == hue]
        color = color_dict.get(hue, 'black')  # Default color if not found in the dictionary
        fig.add_trace(go.Bar(
            x=df_subset[x], 
            y=df_subset[ylabel], 
            name=str(hue), 
            opacity=0.65, 
            marker=dict(color=color), 
            hovertemplate='%{y:.0f}',
            width=0.8,
        ))

    update_layout(x, df, fig, title, xlabel, ylabel, xlabel_rotation)
    fig.update_xaxes(tick0=0, dtick=1)
    if pd.api.types.is_integer(df[x]):
        fig.update_xaxes(tick0=0, dtick=1, range=[df[x].min(), df[x].max()])

    return fig