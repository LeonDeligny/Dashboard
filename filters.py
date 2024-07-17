"""
Module related to filtering dataframes.
"""

import pandas as pd
import calendar

from dicts import ILOT_LIST, ILOT_DICT, EQUIPMENT_TYPES, INV_SHIFT_DICT, EQUIPMENTS_PER_OPERATOR_LIST

def filter_operator(df, operator_value):
    if operator_value != 'All':
        df = df[df['Operator'] == operator_value]
    return df

def filter_shift(df, shift_value):
    if shift_value != 'All':
        df = df[df['Shift'] == shift_value]
    return df

def filter_equipment(df, equipment_value):
    if equipment_value != 'All':
        if equipment_value in ['A620HOR', 'A700HOR', 'A720HOR']:
            df = df[df['Equipment'].str.contains(equipment_value)]
        elif equipment_value in ['Ilot1', 'Ilot2', 'Ilot3', 'Ilot4']:
            df = df[df['Equipment'].isin(ILOT_DICT[equipment_value])]
        else:
            df = df[df['Equipment'] == equipment_value]
    return df

def filter_eq_per_operator(df, equipment_per_operator):
    df = df[df['#Equipments/Operator'].isin(equipment_per_operator)]
    return df

def filter_weekday(df, weekday_value):
    df = df[df['Weekday'].isin(weekday_value)]
    return df

def filter_operator_per_eq(df, operator_per_equipment):
    df = df[df['#Operators/Equipment'].isin(operator_per_equipment)]
    return df

def filter_team(df, team_value):
    if team_value != 'All':
        df = df[df['Team'] == team_value]
    return df

def filter_eq_per_ilot(df, equipment_per_ilot):
    df = df[df['#Equipments/Ilot'].isin(equipment_per_ilot)]
    return df

def filter_op_per_ilot(df, operator_per_ilot):
    df = df[df['#Operators/Ilot'].isin(operator_per_ilot)]
    return df

def generate_title(input_values, base_title):
    def get_filter_values(input_vals):
        return [f'{k}:{v}' for k, v in input_vals.items() 
                if v and v != 'All' and v != EQUIPMENTS_PER_OPERATOR_LIST 
                and v != list(calendar.day_name) and k != 'Week' and k != 'Year']

    selected_year = input_values['Year']
    selected_week_start, selected_week_end = input_values['Week']
    if selected_week_start != selected_week_end:
        title = f'{base_title} for weeks {selected_week_start} to {selected_week_end} and year {selected_year}'
    else:
        title = f'{base_title} for week {selected_week_start} and year {selected_year}'
    
    filter_values = get_filter_values(input_values)
    if filter_values:
        title += f'<br><sub> Filters: {", ".join(map(str, filter_values))}</sub>'
    return title

def filter_dataframe(data_frame, input_values):
    def filter_by_column(df, col_name, condition, transform=lambda x: x):
        if col_name in input_values and input_values[col_name] != 'All':
            return df[df[col_name] == transform(input_values[col_name])]
        return df

    def filter_by_range(df, col_name, range_vals):
        start, end = range_vals
        return df[df[col_name].between(start, end)]

    data_frame = filter_by_column(data_frame, 'Year', input_values['Year'])
    data_frame = filter_by_range(data_frame, 'Week', input_values['Week'])

    if 'Shift' in input_values:
        data_frame = filter_by_column(data_frame, 'Shift', input_values['Shift'], transform=lambda x: x)
    
    if 'Operator' in input_values:
        data_frame = filter_by_column(data_frame, 'Operator', input_values['Operator'])
    
    if 'Weekday' in input_values and input_values['Weekday']:
        data_frame = data_frame[data_frame['Weekday'].isin(input_values['Weekday'])]

    if 'Equipment' in input_values and input_values['Equipment'] != 'All':
        equipment = input_values['Equipment']
        if equipment in EQUIPMENT_TYPES:
            data_frame = data_frame[data_frame['Equipment'].str.contains(equipment)]
        elif equipment in ILOT_LIST:
            data_frame = data_frame[data_frame['Equipment'].isin(ILOT_DICT[equipment])]
        else:
            data_frame = data_frame[data_frame['Equipment'] == equipment]

    if 'Equipments per Operator' in input_values:
        if '#Equipments/Operator' not in data_frame.columns:
            data_frame = data_frame.sort_values(by=['Date', 'Shift'], ascending=[False, False])
            df_equipment_per_operator = data_frame.groupby(['Date', 'Shift', 'Operator'])['Equipment'].nunique().reset_index(name='#Equipments/Operator')
            data_frame = pd.merge(data_frame, df_equipment_per_operator, on=['Date', 'Shift', 'Operator'])
        data_frame = data_frame[data_frame['#Equipments/Operator'].isin(input_values['Equipments per Operator'])]

    return data_frame

def apply_filter_query(query, input_values):
    start_week, end_week = input_values['Week']

    # Start to filter on Year and Week (Two features that are ALWAYS present in every db).
    filtered_query = query + (  
        f"WHERE EXTRACT(YEAR FROM dte) = {input_values['Year']} "
        f"AND EXTRACT(wEEK FROM dte) BETWEEN {start_week} AND {end_week}"
    )

    if 'Shift' in input_values and input_values['Shift'] != 'All':
        filtered_query += f"AND shift = '{input_values['Shift']}'"

    filtered_query += ";"

    return filtered_query