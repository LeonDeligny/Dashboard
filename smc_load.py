"""
Module related to loading (with CONS number), preprocessing, and cleaning from the dataset (with some feature extraction).
"""

import re, ast, psycopg2, datetime

import pandas as pd, numpy as np

from pathlib import Path

from dicts import EQUIPMENT_TYPES, TEAM_COLOR, TOOL_DICT, SHIFT_DICT
from utils import fix_operator, assign_team, assign_weekday, standardize_equipment_name, dict_to_str, returns_defaults_dict
from filters import apply_filter_query

SMC_COLS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17] # Columns we extract from the dataset
SMC_NAME = ["Number", "Operator", "Date", "Shift", "Equipment", "OK", "NOK", 'A', 'C', 'O', 'R', 'M', 'U', 'd6', "Comments", "OFA", 'YW', 'Type'] # Names of the columns we extract

SMC_TRACKING_PATH = Path("C:/Users/a22006/Desktop/Dashboard_hmsa/smc_tracking.csv") # Path("/Users/leondeligny/Desktop/Master/Dashboard_hmsa/smc_tracking.csv") # Path("/var/lib/hmsa/smc_tracking.csv") #
    
def load_df_smc(input_values):
    '''
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname='hmsa2',
        user='hmsait',
        password='h46bh2j0',
        host='172.30.45.67',
    )

    query = """
                select id, usr, dte, shift, pdc, qty_ok, qty_ko, d0, d1, d2, d3, d4, d5, d6,

                '"'||regexp_replace(regexp_replace(comment, '\n+',
                ' ', 'g'), '\r+', '', 'g')||'"' as
                comment,

                ofa, week_from(dte, shift) as week, defaults as Type from uu_tracking 
            """

    filtered_query = apply_filter_query(query, input_values)

    # Execute the query and load data into a DataFrame
    df = pd.read_sql_query(filtered_query, conn)

    df.columns = SMC_NAME

    # Close the connection
    conn.close()
    '''
    df = pd.read_csv(SMC_TRACKING_PATH, delimiter=';', usecols=SMC_COLS, names=SMC_NAME, skiprows=1)

    df = df[df['Date'].notna()]
    df.reset_index(drop=True, inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
    df['Year'] = (df['Date'].dt.year).astype(int)
    df['Type'] = df['Type'].fillna('')
    df['Comments'] = df['Comments'].fillna('')
    df['Operator'] = df['Operator'].fillna('NA')
    df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
    #df = df.groupby(["OFA", "Date", "Operator", "Collaborator", "Shift", "Operation"]).agg({'OK': 'sum','NOK': 'sum','Type': ' '.join,'Comments': ' '.join}).reset_index()
    operators_set = set(df['Operator'])
    df['Operator'] = df['Operator'].apply(lambda x: fix_operator(x, operators_set))
    df['Week'] = np.where((df['Date'].dt.dayofweek == 6) & (df['Shift'] != 2), (df['Date'] + pd.DateOffset(days=-1)).dt.to_period('W-SAT').dt.week,df['Date'].dt.to_period('W-SAT').dt.week)

    df['Team'] = df.apply(assign_team, axis=1)
    df['Shift'] = df['Shift'].map(SHIFT_DICT)
    df['Weekday'] = df.apply(assign_weekday, axis=1)
    df['Week'] = df['Week'].dropna().astype(int)
    df = df.sort_values(by=['Date', 'Shift'], ascending=[False, False])

    def replace_keys(d, mapping):
        return {mapping.get(k, k): v for k, v in d.items()}
    
    DEFAULTS_DICT = returns_defaults_dict()

    df['Type'] = df['Type'].apply(lambda x: replace_keys(ast.literal_eval(x), DEFAULTS_DICT) if isinstance(x, str) and x else x)    

    return df

def load_ofa_equipment():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname='hmsa2',
        user='hmsait',
        password='h46bh2j0',
        host='172.30.45.67',
    )

    query = """
                select dte, shift, pdc, ofa
                from uu_tracking 
                order by dte desc, shift desc
            """
    
    # Execute the query and load data into a DataFrame
    df = pd.read_sql_query(query, conn)

    df.columns = ['Date', 'Shift', 'Equipment', 'OFA']

    # Close the connection
    conn.close()

    return df


def load_color_dict_operator(df_smc):
    recent_operator_teams = df_smc.sort_values('Date').groupby('Operator').last()['Team'].reset_index()
    operators_by_teams = recent_operator_teams.sort_values('Team')['Operator']
    recent_teams = df_smc.sort_values('Date', ascending=True).drop_duplicates('Operator', keep='last')
    operators_by_teams = recent_teams.groupby("Team")["Operator"].unique().to_dict()
    COLOR_DICT_OPERATOR = {}
    for team, operators in operators_by_teams.items():
        team_color = TEAM_COLOR[str(int(team))]
        for operator in operators:
            COLOR_DICT_OPERATOR[operator] = team_color

    return COLOR_DICT_OPERATOR

def load_df_smc_data():
    df = load_ofa_equipment()
    df_equip_by_OFA = df.groupby('OFA')['Equipment'].unique().reset_index()
    df_equip_by_OFA.rename(columns={'Equipment': 'Equipment List'}, inplace=True)
    df_equip_by_OFA['Equipment List'] = df_equip_by_OFA['Equipment List'].apply(standardize_equipment_name)
    df_last_update = df.groupby('OFA')['Date'].max().reset_index() 
    df_last_update.rename(columns={'Date': 'Last Update'}, inplace=True) 
    df_equip_by_OFA = df_equip_by_OFA.merge(df_last_update, on='OFA')
    return df_equip_by_OFA

def load_df_OFA_mismatch():
    df_equip_by_OFA = load_df_smc_data()
    df_OFA_mismatch = df_equip_by_OFA[df_equip_by_OFA['Equipment List'].apply(lambda x: len(set(x)) > 1)]
    df_OFA_mismatch.loc[:, 'Equipment List'] = df_OFA_mismatch['Equipment List'].apply(lambda x: ', '.join(x))
    df_OFA_mismatch = df_OFA_mismatch.sort_values(by='Last Update', ascending=False)
    df_OFA_mismatch['Last Update'] = pd.to_datetime(df_OFA_mismatch['Last Update']).dt.strftime('%d-%m-%Y')    
    return df_OFA_mismatch

def load_df_equip_by_OFA():
    df_equip_by_OFA = load_df_smc_data()
    df_equip_by_OFA = df_equip_by_OFA[df_equip_by_OFA['Equipment List'].apply(lambda x: len(set(x)) == 1)]
    return df_equip_by_OFA

def load_df_smc_cons(df):
    l = len(df)
    df['Tool'] = ''
    df['C'] = [{} for _ in range(l)]
    df['O'] = [{} for _ in range(l)]
    df['U'] = [{} for _ in range(l)]
    df['Tool'] = ''
    for col in ['C', 'O', 'U']:
        df[col] = [{}]*l
        pattern = r'(#CONS-00)(\d+)(#)([COU])(#)(\d+)'

    def process_row(row):
        matches = re.findall(pattern, row.Comments)
        dic = {}
        c_dict = {}
        o_dict = {}
        u_dict = {}
        for match in matches:
            cons, type_let, qt_rebuts = match[1], match[3], match[5]
            type_Tool = TOOL_DICT.get(cons, 'NA')
            dic[cons] = type_Tool
            if type_let == "C": c_dict[cons] = (int(qt_rebuts), type_Tool)
            elif type_let == "O": o_dict[cons] = (int(qt_rebuts), type_Tool)
            elif type_let == "U": u_dict[cons] = (int(qt_rebuts), type_Tool)
        return pd.Series([', '.join(filter(None, set(dic.values()))), c_dict, o_dict, u_dict], index=['Tool', 'C','O','U'])

    df[['Tool', 'C','O','U']] = df.apply(process_row, axis=1)
    df = df.sort_values(by=['Date', 'Shift'], ascending=[False, False])
    return df

def load_df_smc_cons_mismatch():
    current_year = datetime.datetime.now().year
    current_week = datetime.datetime.now().isocalendar()[1]
    df_smc = load_df_smc({'Year': current_year, 'Week': (1, current_week)})
    df = load_df_smc_cons(df_smc)

    df_mismatch = pd.DataFrame()

    for _, row in df.iterrows():
        sum_rebuts = sum([val[0] for val in row['C'].values()] + [val[0] for val in row['O'].values()] + [val[0] for val in row['U'].values()] + list(row[['R', 'A']].values))
        if sum_rebuts != row['NOK']:
            df_mismatch = df_mismatch._append(row)

    if not df_mismatch.empty:
        df_mismatch['C'] = df_mismatch['C'].apply(dict_to_str)
        df_mismatch['O'] = df_mismatch['O'].apply(dict_to_str)
        df_mismatch['U'] = df_mismatch['U'].apply(dict_to_str)
        df_mismatch['Comments'] = df['Comments']
        df_mismatch['Date'] = df_mismatch['Date'].dt.strftime('%d-%m-%Y')
        df_mismatch = df_mismatch.drop(['OK', 'Weekday', 'Year'], axis=1)

    return df_mismatch

def extract_cons_tool(df_smc):
    df = load_df_smc_cons(df_smc)
    new_data_cons = []
    # new_data_Tool = []
    for _, row in df.iterrows():
        c_dict = ast.literal_eval(row['C']) if isinstance(row['C'], str) else row['C']
        o_dict = ast.literal_eval(row['O']) if isinstance(row['O'], str) else row['O']
        u_dict = ast.literal_eval(row['U']) if isinstance(row['U'], str) else row['U']
        for cons, qty_Tool in {**c_dict, **o_dict, **u_dict}.items():
            qty, tool = qty_Tool
            week = row['Week']
            equipment = row['Equipment']
            operator = row['Operator']
            shift = row['Shift']
            date = row['Date']
            weekday = row['Weekday']
            year = row['Year']
            new_data_cons.append([cons, qty if cons in row['C'] else 0, qty if cons in row['O'] else 0, qty if cons in row['U'] else 0, week, equipment, operator, shift, date, weekday, year])
            # new_data_Tool.append([tool, qty if cons in row['C'] else 0, qty if cons in row['O'] else 0, qty if cons in row['U'] else 0, week, equipment, operator, shift, weekday])

    df_cons = pd.DataFrame(new_data_cons, columns=['N° CONS', 'C', 'O', 'U', 'Week', 'Equipment', 'Operator', 'Shift', 'Date', 'Weekday', 'Year'])
    # df_tool = pd.DataFrame(new_data_Tool, columns=['Tool', 'C', 'O', 'U', 'Week', 'Equipment', 'Operator', 'Shift', 'Weekday'])

    df_cons['NOK'] = df_cons['C'] + df_cons['O'] + df_cons['U']
    # df_tool['NOK'] = df_tool['C'] + df_tool['O'] + df_tool['U']

    df_cons = df_cons.groupby(['N° CONS', 'Week', 'Equipment', 'Operator', 'Shift', 'Date', 'Weekday', 'Year'], as_index=False).sum()
    # df_tool = df_tool.groupby(['Tool', 'Week', 'Equipment', 'Operator', 'Shift', 'Weekday'], as_index=False).sum()

    return df_cons #, df_tool

def load_cons_list(df_smc):
    CONS_LISTS = {'A620HOR': set(), 'A700HOR': set(), 'A720HOR': set()}
    df_smc_cons = extract_cons_tool(df_smc)
    for equipment_key, cons_set in CONS_LISTS.items():
        for _, row in df_smc_cons.iterrows():
            if equipment_key in row['Equipment']:
                cons_set.add(int(row['N° CONS']))

    LIST_CONS_LISTS = [list(CONS_LISTS[equipment]) for equipment in EQUIPMENT_TYPES]
    return LIST_CONS_LISTS