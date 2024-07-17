import calendar, json, re, psycopg2, ast, csv, hashlib

import pandas as pd, numpy as np

###############
# Load Labels #
###############

SMC_NAME = ["Number", "Operator", "Date", "Shift", "Equipment", "OK", "NOK", 'A', 'C', 'O', 'R', 'M', 'U', 'd6', "Comments", "OFA", 'YW'] # Names of the columns we extract

def load_operator_label():
    conn = psycopg2.connect(
        dbname='hmsa2',
        user='hmsait',
        password='h46bh2j0',
        host='172.30.45.67',
    )

    query = """
                select distinct usr
                from uu_tracking 
            """

    # Execute the query and load data into a DataFrame
    df = pd.read_sql_query(query, conn) 

    # Close the connection
    conn.close()

    operator_label = [{'label': 'All Operators', 'value': 'All'}] + [{'label': i, 'value': i} for i in df['usr'] if isinstance(i, str)]

    return operator_label

def load_equipment_label():
    conn = psycopg2.connect(
        dbname='hmsa2',
        user='hmsait',
        password='h46bh2j0',
        host='172.30.45.67',
    )

    query = """
                select distinct pdc
                from uu_tracking 
            """

    # Execute the query and load data into a DataFrame
    df = pd.read_sql_query(query, conn) 

    # Close the connection
    conn.close()

    equipment_label = [{'label': 'All Equipments', 'value': 'All'},
                       {'label': 'A620HOR', 'value': 'A620HOR'}, 
                       {'label': 'A700HOR', 'value': 'A700HOR'}, 
                       {'label': 'A720HOR', 'value': 'A720HOR'},
                       ] + [{'label': i, 'value': i} for i in df['pdc'] if isinstance(i, str)]
    
    return equipment_label

#################
# Preprocessing #
#################

def fix_operator(operator, operators_set):
    """
    Args:
        operator (str): operator name
        operators_set (set): set of operator names
    Returns:
        operator (str): operator's name without the "T-" prefix if it exists
    """
    if isinstance(operator, str):
        if operator.startswith('T') and operator[1:] in operators_set:
            return operator[1:]
    return operator

def assign_team(df):
    if df['Operator'] in ['WWW', 'DRD', 'ESI']:
        return 3
    else:
        return (df['Week']+df['Shift'])%3
    
######################
# Feature Extraction #
######################

def assign_weekday(row):
    """
    Args:
        row (pd.Series): row of the dataframe
    Returns:
        weekday (str): name of the day of the week
    """
    try:
        weekday = calendar.day_name[row['Date'].dayofweek]
        shift = row['Shift']
        if shift == 2 or shift == 'Night':
            return calendar.day_name[(row['Date'] + pd.DateOffset(days=1)).dayofweek]
        else:
            return weekday
    except Exception as e:
        print(f"Error with row: {row}")
        print(f"Exception: {e}")
        return np.nan  # or return any other filler value denoting error

def standardize_equipment_name(equipment_list):
    """
    Args:
        equipment_list (list): list of equipment names
    Returns:
        unique_list (list): list of unique equipment names without the "-1", "-3" for the Trios Equipments
    """
    standardized_list = [re.sub(r'-\d+$', '', eq) for eq in equipment_list]
    unique_list = list(set(standardized_list))
    return unique_list

def dict_to_str(d):
    if d and isinstance(d, dict):
        if d == {}:
            stringified = '{}'
        else:
            stringified = json.dumps(d)
        return stringified
    else:
        return '{}'
    
def str_to_dict(dict_string):
    dict_string = dict_string.strip()
    if dict_string == '':
        return {}
    try:
        return json.loads(dict_string)
    except json.JSONDecodeError:
        print(f'Failed to parse: "{dict_string}"')
        return {}

def extract_type_smc(df):
    new_data = []
    for _, row in df.iterrows():
        if isinstance(row['Type'], str):
            if row['Type'].strip():  # Check if the string is not empty
                try:
                    nok_dict = ast.literal_eval(row['Type'])
                except (SyntaxError, ValueError) as e:
                    print(f"Error for row['Type']: {row['Type']} - {e}")
                    continue  # Skip the row if there's an error
            else:
                continue  # Skip the row if the string is empty
        else:
            nok_dict = row['Type']
        
        for type, nok_qty in {**nok_dict}.items():
            year = row['Year']
            week = row['Week']
            date = row['Date']
            equipment = row['Equipment']
            operator = row['Operator']
            shift = row['Shift']
            weekday = row['Weekday']
            ofa = row['OFA']
            ok = row['OK']
            nok = row['NOK']
            new_data.append([type, nok_qty if type in row['Type'] else 0, year, week, date, equipment, operator, shift, weekday, ofa, ok, nok])
    
    df_Type = pd.DataFrame(new_data, columns=['Type', 'NOK by Type', 'Year', 'Week', 'Date', 'Equipment', 'Operator', 'Shift', 'Weekday', 'OFA', 'OK', 'NOK'])
    df_Type = df_Type.groupby(['Type', 'Year', 'Week', 'Date', 'Equipment', 'Operator', 'Shift', 'Weekday', 'OFA'], as_index=False).sum()
    return df_Type

def extract_type(df):
    new_data = []
    for _, row in df.iterrows():
        if isinstance(row['Type'], str):
            if row['Type'].strip():  # Check if the string is not empty
                try:
                    nok_dict = ast.literal_eval(row['Type'])
                except (SyntaxError, ValueError) as e:
                    print(f"Error for row['Type']: {row['Type']} - {e}")
                    continue  # Skip the row if there's an error
            else:
                continue  # Skip the row if the string is empty
        else:
            nok_dict = row['Type']
        
        for type, nok_qty in {**nok_dict}.items():
            year = row['Year']
            week = row['Week']
            operation = row['Operation']
            equipment = row['Equipment']
            operator = row['Operator']
            collaborator = row['Collaborator']
            shift = row['Shift']
            weekday = row['Weekday']
            ofa = row['OFA']
            ok = row['OK']
            nok = row['NOK']
            new_data.append([type, nok_qty if type in row['Type'] else 0, year, week, operation, equipment, operator, collaborator, shift, weekday, ofa, ok, nok])
    
    df_Type = pd.DataFrame(new_data, columns=['Type', 'NOK by Type', 'Year', 'Week', 'Operation', 'Equipment', 'Operator', 'Collaborator', 'Shift', 'Weekday', 'OFA', 'OK', 'NOK'])
    df_Type = df_Type.groupby(['Type', 'Year', 'Week', 'Operation', 'Equipment', 'Operator', 'Collaborator', 'Shift', 'Weekday', 'OFA'], as_index=False).sum()
    return df_Type

def string_to_hex_color(s):
    # Convert the string to a hash
    hash_object = hashlib.md5(s.encode())
    # Get the hexadecimal representation of the hash
    hex_dig = hash_object.hexdigest()
    # Take the first 6 characters to form a hex color code
    hex_color = '#' + hex_dig[:6]
    return hex_color


def returns_defaults_color_dict() -> dict:
    # Initialize an empty dictionary
    DEFAULTS_COLOR_DICT = {}

    conn = psycopg2.connect(
            dbname='hmsa2',
            user='hmsait',
            password='h46bh2j0',
            host='172.30.45.67',
        )

    query = """
                select distinct def_descr
                from prod_defaults 
            """

    # Execute the query and load data into a DataFrame
    df = pd.read_sql_query(query, conn) 

    # Close the connection
    conn.close()

    DEFAULTS_COLOR_DICT = {value: string_to_hex_color(value) for value in df['def_descr']}

    return DEFAULTS_COLOR_DICT

def returns_defaults_dict() -> dict:
    # Initialize an empty dictionary
    DEFAULTS_DICT = {}

    conn = psycopg2.connect(
            dbname='hmsa2',
            user='hmsait',
            password='h46bh2j0',
            host='172.30.45.67',
        )

    query = """
                select def_name, def_descr
                from prod_defaults 
            """

    # Execute the query and load data into a DataFrame
    df = pd.read_sql_query(query, conn) 

    # Close the connection
    conn.close()

    DEFAULTS_DICT = {row['def_name']: row['def_descr'] for _, row in df.iterrows()}

    return DEFAULTS_DICT
