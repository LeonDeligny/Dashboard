"""
Module related to all the different dictionnaries and colour mappings used.
"""
import datetime, calendar, csv, hashlib, psycopg2

import pandas as pd, dash_bootstrap_components as dbc


def CustomCard(children, **kwargs):
    card_kwargs = {"className": "custom-card"}
    card_kwargs.update(kwargs)

    return dbc.Card(children, **card_kwargs)

###########
# Weekday #
###########

WEEKDAY_LABEL_LIST = [{'label': day, 'value': day} for day in list(calendar.day_name)]

WEEKDAY_DICT = {"Monday": 0, "Tuesday": 1, "Wednesday":2, "Thursday":3, "Friday":4, 'Saturday':5, 'Sunday':6}

############
# Sortings #
############

NOK_SORTING_LIST = [{'label': 'Sort by Total NOK', 'value': 'NOK'},
                    {'label': 'Sort by NOK (%)', 'value': 'NOK (%)'},
                    {'label': 'Sort by C (%)', 'value': 'C (%)'},
                    {'label': 'Sort by O (%)', 'value': 'O (%)'},
                    {'label': 'Sort by U (%)', 'value': 'U (%)'},
                    {'label': 'Sort Alphabetically', 'value': 'alphabet'}
                ]

#######################
# Equipments/Operator #
#######################

EQUIPMENTS_PER_OPERATOR_LIST = [1,2,3,4,4,5,6,7]

EQUIPMENTS_PER_OPERATOR_LABEL_LIST = [{'label': str(i)+' Equip/Op', 'value': i} for i in EQUIPMENTS_PER_OPERATOR_LIST]

########
# Week #
########

WEEK_LIST = list(range(1, 53))

WEEK_DICT = {str(week): str(week) for week in WEEK_LIST}

#############
# Equipment #
#############

# List of type of equipments.
EQUIPMENT_TYPES = ['A620HOR', 'A700HOR', 'A720HOR']

# Dictionary mapping an equipment type to its corresponding colour.
COLOR_DICT_EQUIPMENT = {
    "A620": "#e1c9b9", 
    'A620 (%)': '#b5998d', 
    
    "A700": "#15695f", 
    'A700 (%)': '#104b45', 
    
    "A720": " #f48686", 
    'A720 (%)': '#c65f5f'
}

########
# Ilot #
########

# List of different Ilots.
ILOT_LIST = ['Ilot1', 'Ilot2', 'Ilot3', 'Ilot4']

# List of equipments belonging to Ilot i.
ILOT1LIST = ['A720HOR034', 'A720HOR035', 'A700HOR018-1', 'A700HOR018-3', 'A700HOR019-1', 'A700HOR019-3']
ILOT2LIST = ['A720HOR036', 'A720HOR037', 'A700HOR032-1', 'A700HOR032-3', 'A700HOR033-1', 'A700HOR033-3']
ILOT3LIST = ['A720HOR038', 'A720HOR039', 'A700HOR034-1', 'A700HOR34-3', 'A700HOR035-1', 'A700HOR035-3']
ILOT4LIST = ['A620HOR006', 'A620HOR015', 'A620HOR030', 'A620HOR029']

# Dictionary mapping an Ilot to it's list.
ILOT_DICT  = {'Ilot1': ILOT1LIST, 'Ilot2': ILOT2LIST, 'Ilot3': ILOT3LIST, 'Ilot4': ILOT4LIST}

#########
# Shift #
#########

# Dictionary mapping shift integer to shift string.
SHIFT_DICT = {0: 'Morning', 1: 'Afternoon', 2: 'Night', 3: 'Week-End'}

INV_SHIFT_DICT = {'Morning': 0, 'Afternoon':1, 'Night': 2, 'Week-End': 3}

# List of the different shifts in order during the day.
SHIFT_LIST = ["Night", "Morning", "Afternoon"]

# Dictionary mapping shift to it's start time in hours.
SHIFT_START = {'Morning': '05:00', 'Afternoon': '14:00', 'Night': '22:00'}

# Dictionary mapping shift to it's HEX colour.
SHIFT_COLOR_DICT = {"Morning": "#FFDF00", "Afternoon": "#1E90FF", "Night": "#800080"}

SHIFT_LABEL_LIST = [{'label': 'All Shifts', 'value': 'All'}] + [{'label': i, 'value': i} for i in SHIFT_LIST]

########
# Team #
########

TEAM_COLOR = {
    '0': '#440d31', 
    'Team 0 (%)': '#300021',

    '1': '#088da5',
    'Team 1 (%)': '#06677b', 

    '2': '#50a85e', 
    'Team 2 (%)': '#387441',

    '3': 'black',     
    'Team 3 (%)': 'black' 
}

########
# Tool #
########

# CONS returns the tool type
TOOL_DICT = {
    '609': 'FE', 
    '610': 'FE', 
    '611': 'Foret',
    '613': 'FT', 
    '615': 'FT', 
    '614': 'FB', 
    '618': 'FB', 
    '617': 'Fraise en Bout', 
    '651': 'FF', 
    '653': 'FF', 
    '654': 'FF', 
    '655': 'Foret', 
    '656': 'Micro Foret', 
    '657': 'Micro Foret', 
    '671': 'Tronconneur',
    '695': 'Fraise en Bout', 
    '697': 'Fraise Torique',
    '699': 'Foret a Pointer',
    '700': 'Foret Etager',
    '701': 'Foret Etager',
    '715': 'Micro Foret', 
}

COLOR_DICT_TOOL = {
    'FE': '#FF0000',
    'FT': '#FF7F00',
    'FB': '#FFFF00',
    'Fraise en Bout': '#00FF00',
    'FF': '#00FFFF', 
    'Foret': '#0000FF',
    'Micro Foret': '#8B00FF',
    'Tronconneur': '#FF1493', 
    'Fraise Torique': '#FF4500',
    'Foret a Pointer': '#FFD700',
    'Foret Etager': '#3CB371',
}

COLOR_DICT_CONS = {
    '609': '#FF0000',
    '610': '#FF7F00',
    '613': '#FFFF00', 
    '615': '#00FF00',
    '614': '#00FFFF',
    '618': '#0000FF', 
    '617': '#8B00FF',
    '695': '#FF1493',
    '651': '#FF4500',
    '653': '#FFD700',
    '654': '#3CB371',
    '611': '#40E0D0',
    '655': '#4169E1',
    '656': '#EE82EE',
    '657': '#FFA07A',
    '715': '#6A5ACD',
    '671': '#2E8B57',
    '697': '#B22222',
    '699': '#4682B4',
    '700': '#6B8E23',
    '701': '#5F9EA0' 
}

COLOR_DICT = {
    'C': '#1f77b4', 
    'C (%)': '#154360',

    'O': '#ff7f0e', 
    'O (%)': '#cc6600',

    'U': '#2ca02c', 
    'U (%)': '#1f7a1f',

    'R': '#d62728', 
    'R (%)': '#8B0000',

    'A': '#9467bd', 
    'A (%)': '#674c80',

    'NOK (%)': '#353935', 
}

###################
# Post Processing #
###################

OPERATION_DICT_PP = {
    0: 'Pre-Deburring',
    10: 'Machining', 
    20: 'Deburring', 
    50: 'Dimensional', 
    60: 'Sorting',
    71: 'Release AQL',
    72: 'Release 100%',
    100: 'Visual', 
    101: 'Visual AQL',
}

# Unique list of operations
OPERATIONS_LIST = ['Pre-Deburring', 'Machining', 'Deburring', 'Dimensional', 'Sorting', 'Release AQL', 'Release 100%', 'Visual', 'Visual AQL'] #list(set(list(OPERATION_DICT_PP.values()))) 

OPERATION_DICT_RP = {
    'Opération TOURNER': 'Machining',
    'Opération CONDITIONNER': 'Processing', 
    'Opération LAVER': 'Wash',
    'Opération TRIER': 'Sorting',
    'OP_CTR+RAPPORT': 'Control+Report',
    'Opération POLIR / TROVALISER': 'Polish',
    'Opération EBAVURER': 'Deburring',
}

'''
DEFAULTS_COLOR_DICT = {
    "6 Trous Ext. A": "#FF0000",
    "6 Trous M": "#FF0000",
    "6 Trous AM": "#FF0000",

    "Diam. Int. M": "#00FFFF",
    "Diam. 0.457mm AM/B": "#00FFFF",
    "Diam. 2.083 AM": "#00FFFF",

    "Petite Colerette AM": "#8B00FF",
    "Colerette M": "#8B00FF",
    "Grande Colerette": "#8B00FF",

    "Paroi Ext. A": "#FF7F00",
    "Paroi Triangle A": "#FF7F00",

    "Trous Transverseaux B": "#0000EE",
    "Trous Transversaux A": "#0000FF",

    "Arche Coups": "#6A5ACD",
    "Arche Plat": "#6A5ACD",

    "3 Trous AM": "#483D8B",
    "3 Trous Deburring": "#483D8B",
    "3 Trous Rayures": "#483D8B",
    "3 Trous D": "#483D8B",

    "Bosselage": "#1E90FF",

    "Pièce A": "#007FFF",

    "Autre": "#2E8B57",

    "Mors": "#3CB371",

    "Triangle D": "#f8f5f5",

    "Pièce Perdue": "#FFC0CB",

    "Dimensionnel": "#3CB371",

    "Manque Usinage": "#90EE90",

    'Ébavurage': "#ADD8E6",
    'Cheminée': "#00008B",
}
'''

'''
DEFAULTS_DICT = {

    'd00' : 'Autre',
    'd01' : '6 Trous Ext. A',
    'd02' : '3 Trous AM',
    'd03' : '6 Trous M',
    'd04' : 'Ø 2.083 AM',
    'd05' : 'Ø Int. M',
    'd06' : 'Petite Colerette AM',
    'd07' : 'Colerette M',
    'd08' : 'Ø 0.457mm AM/B',
    'd09' : 'Mors',
    'd10' : '6 Trous AM',

    'd11' : 'Paroi Ext. A',
    'd12' : 'Trous Trv. B',
    'd13' : 'Paroi Triangle A',
    'd14' : 'Bosselage',
    'd15' : 'Pièce A',
    'd16' : "Arche Coups",
    'd17' : 'Pièce Perdue',
    'd18' : 'Triangle D',
    'd19' : "Arche Plat",
    'd20' : '3 Trous E',

    'd21' : '3 Trous R',
    'd22' : 'Grande Colerette',
    'd23' : 'Trous Trv. A',
    'd24' : '3 Trous D',
    'd25' : 'Dimensionnel',
    'd26' : 'Manque Usinage',

    'd40': 'A10', 
    'd41': 'A20', 
    'd42': 'A30', 
    'd43': 'A100', 
    'd44': 'A120', 
    'd45': 'A210', 
    'd46': 'E10-E60',
    'd47': 'E91', 
    'd48': 'E120-E170', 
    'd49': 'B40', 
    'd50': 'B80', 
    'd51': 'B140', 
    'd52': 'B141', 
    'd53': 'B142', 
    'd54': 'C20',

    # Dimensions
    'd70': 'E10', 
    'd71': 'E20', 
    'd72': 'E30', 
    'd73': 'E40', 
    'd74': 'E50', 
    'd75': 'E60', 
    'd76': 'E70', 
    'd77': 'E81', 
    'd78': 'E91', 
    'd79': 'E101', 
    'd80': 'E111',
    'd81': 'A20', 
    'd82': 'A30', 
    'd83': 'A50', 
    'd84': 'B80', 
    'd85': 'B170', 
    'd86': 'B171', 
    'd87': 'B172', 
    'd88': 'C20',

    # Opération 00
    'd100': 'Ébavurage', 
    'd101': 'Cheminée',
}
'''

################
# Global Graph #
################

COLOR_DICT_GLOBAL = {
    "NOK Deburring": "#e1c9b9", 
    'NOK Deburring (%)': '#b5998d', 

    "NOK Visual Control": "#15695f", 
    'NOK Visual Control (%)': '#104b45', 

    "NOK Machining": " #f48686", 
    'NOK Machining (%)': '#c65f5f'
}