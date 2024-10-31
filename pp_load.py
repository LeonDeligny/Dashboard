import ast, sqlite3

import pandas as pd, numpy as np

from pathlib import Path
from datetime import datetime

from dicts import SHIFT_DICT, OPERATION_DICT_PP

from utils import fix_operator, assign_team, assign_weekday, returns_defaults_dict
from smc_load import load_df_equip_by_ofa
from filters import apply_filter_query

current_year = datetime.now().year

PP_COLS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
PP_NAME = ["ofa", "Date", "Operator", "Collaborator", "Shift", "Operation", "OK", "NOK", "Type", "Comments"]

PP_TRACKING_PATH = Path("C:/Users/a22006/Desktop/Dashboard_hmsa/pp_tracking.csv") # Path("/Users/leondeligny/Desktop/Master/Dashboard_hmsa/pp_tracking.csv") # PP_TRACKING_PATH = Path("Z:\\data\\pp_tracking.csv")

def load_pp_data(input_values):
    # Connect to the PostgreSQL database
    conn = sqlite3.connect('database1.db')
    query = """
        select ofa, dte, uusr, usr, shift, ope, qty_ok, qty_ko, defaults, comments
        from pp_tracking 
    """

    filtered_query = apply_filter_query(query, input_values)

    # Execute the query and load data into a DataFrame
    df = pd.read_sql_query(filtered_query, conn) # df = pd.read_csv(PP_TRACKING_PATH, delimiter=';', usecols=PP_COLS, names=PP_NAME, skiprows=1)

    df.columns = PP_NAME
    
    # Close the connection
    conn.close()

    df = df[df['Date'].notna()]
    df.reset_index(drop=True, inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
    df['Year'] = (df['Date'].dt.year).astype(int)
    df['Type'] = df['Type'].fillna('')
    df['Comments'] = df['Comments'].fillna('')
    df['Operator'] = df['Operator'].fillna('NA')
    df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
    #df = df.groupby(["ofa", "Date", "Operator", "Collaborator", "Shift", "Operation"]).agg({'OK': 'sum','NOK': 'sum','Type': ' '.join,'Comments': ' '.join}).reset_index()
    operators_set = set(df['Operator'])
    df['Operator'] = df['Operator'].apply(lambda x: fix_operator(x, operators_set))
    df['Week'] = np.where((df['Date'].dt.dayofweek == 6) & (df['Shift'] != 2), (df['Date'] + pd.DateOffset(days=-1)).dt.to_period('W-SAT').dt.week,df['Date'].dt.to_period('W-SAT').dt.week)

    df['Team'] = df.apply(assign_team, axis=1)
    df['Shift'] = df['Shift'].map(SHIFT_DICT)
    df['Operation'] = df['Operation'].map(OPERATION_DICT_PP)
    df['Weekday'] = df.apply(assign_weekday, axis=1)
    df['Week'] = df['Week'].dropna().astype(int)
    df_equip_by_ofa = load_df_equip_by_ofa()
    df_equip_by_ofa['Equipment List'] = df_equip_by_ofa['Equipment List'].apply(lambda x: ', '.join(x))
    df['Equipment'] = df['ofa'].map(df_equip_by_ofa.set_index('ofa')['Equipment List'])
    df['Equipment'] = df['Equipment'].astype(str)
    week_options = df["Week"].astype(int).unique().tolist()
    df = df.sort_values(by=['Date', 'Shift'], ascending=[False, False])

    def replace_keys(d, mapping):
        return {mapping.get(k, k): v for k, v in d.items()}
    
    DEFAULTS_DICT = returns_defaults_dict()

    df['Type'] = df['Type'].apply(lambda x: replace_keys(ast.literal_eval(x), DEFAULTS_DICT) if isinstance(x, str) and x else x)    
    
    return df, week_options

def load_df_zero(input_values):
    df, _ = load_pp_data(input_values)
    df = df[df['Operation']=='0']
    return df

def load_df_twenty(input_values):
    df, _ = load_pp_data(input_values)
    df = df[df['Operation']=='20']
    return df

def load_df_fifty(input_values):
    df, _ = load_pp_data(input_values)
    df = df[df['Operation']=='50']
    return df

def load_df_sixty(input_values):
    df, _ = load_pp_data(input_values)
    df = df[df['Operation']=='60']
    return df

def load_df_seventy_one(input_values):
    df, _ = load_pp_data(input_values)
    df = df[df['Operation']=='71']
    return df

def load_df_seventy_two(input_values):
    df, _ = load_pp_data(input_values)
    df = df[df['Operation']=='72']
    return df

def load_df_hundred(input_values):
    df, _ = load_pp_data(input_values)
    df = df[df['Operation']=='100']
    return df

def load_df_hundred_one(input_values):
    df, _ = load_pp_data(input_values)
    df = df[df['Operation']=='101']
    return df