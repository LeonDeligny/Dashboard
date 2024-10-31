"""
Module related to all the different dictionnaries and colour mappings used.
"""
import calendar

import dash_bootstrap_components as dbc

def CustomCard(children, **kwargs):
    card_kwargs = {"className": "custom-card"}
    card_kwargs.update(kwargs)

    return dbc.Card(children, **card_kwargs)

#############
# Equipment #
#############

EQUIPMENT_TYPES = ['Equipment1', 'Equipment2', 'Equipment3']

# Dictionary mapping an equipment type to its corresponding colour.
COLOR_DICT_EQUIPMENT = {
    "Equipment1": "#e1c9b9", 
    'Equipment1 (%)': '#b5998d', 
    
    "Equipment2": "#15695f", 
    'Equipment2 (%)': '#104b45', 
    
    "Equipment3": " #f48686", 
    'Equipment3 (%)': '#c65f5f'
}


###########
# Weekday #
###########

WEEKDAY_LABEL_LIST = [{'label': day, 'value': day} for day in list(calendar.day_name)]

WEEKDAY_DICT = {"Monday": 0, "Tuesday": 1, "Wednesday":2, "Thursday":3, "Friday":4, 'Saturday':5, 'Sunday':6}

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

###################
# Post Processing #
###################

OPERATION_DICT_PP = {
    0: '0',
    10: '10', 
    20: '20', 
    50: '50', 
    60: '60',
    71: '71',
    72: '72',
    100: '100', 
    101: '101',
}

# Unique list of operations
OPERATIONS_LIST = ['0', '10', '20', '50', '60', '71', '72', '100', '101'] #list(set(list(OPERATION_DICT_PP.values()))) 

OPERATION_DICT_RP = {
    'Operation 10': '10',
    'Operation 110': '110', 
    'Operation 70': '70',
    'Operation 60': '60',
    'Operation 120': '120',
    'Operation 30': '30',
    'Operation 20': '20',
}

################
# Global Graph #
################

COLOR_DICT_GLOBAL = {
    "NOK 20": "#e1c9b9", 
    'NOK 20 (%)': '#b5998d', 

    "NOK 100": "#15695f", 
    'NOK 100 (%)': '#104b45', 

    "NOK 10": " #f48686", 
    'NOK 10 (%)': '#c65f5f'
}