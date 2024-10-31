import sqlite3

import pandas as pd

from pathlib import Path

from dicts import OPERATION_DICT_RP

ofaS_PATH = Path("C:/Users/a22006/Desktop/Dashboard_hmsa/csv/ofas.csv") # Path("/Users/leondeligny/Desktop/Master/Dashboard_hmsa/ofas.csv")

ofaS_COLS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
ofaS_NAME = ["LOT_REFCOMPL", "LOT_RELEASED_QTY", "LOT_REJECT_RELEASED_QTY", "FAC_REFERENCE", "KEY", "SCS_STEP_NUMBER", "TAS_REF", "SCS_SHORT_DESCR", "TAL_RELEASE_QTY", "TAL_REJECTED_QTY", "TAL_BEGIN_REAL_DATE", "TAL_END_REAL_DATE"]

def rename_ops(group):
        ctrl_counter = 0
        lav_counter = 0
        new_descriptions = []
        for op in group['Operation']:
            if op == 'Operation 120':
                if ctrl_counter == 0:
                    new_descriptions.append('CCLACCLA')
                elif ctrl_counter == 1:
                    new_descriptions.append('100')
                else: # Handles all cases after the first and second
                    new_descriptions.append('50')
                ctrl_counter += 1
            elif op == 'Operation 70':
                if lav_counter == 0:
                    new_descriptions.append('LFLFLF')
                else:
                    new_descriptions.append('LTLTLT')
                lav_counter += 1
            else:
                new_descriptions.append(op) # doesn't change the non 'Operation 120'
        group['Operation'] = new_descriptions
        return group

def df_erp_load():
    # Connect to the PostgreSQL database
    conn = sqlite3.connect('database2.db')
    query = """
        select LOT_REFCOMPL as ofa, LOT_RELEASED_QTY, LOT_REJECT_RELEASED_QTY, FAC_REFERENCE, SCS_STEP_NUMBER, TAS_REF, SCS_SHORT_DESCR, TAL_RELEASE_QTY, TAL_REJECTED_QTY, TAL_BEGIN_REAL_DATE, TAL_END_REAL_DATE
        from ofas 
    """

    # Execute the query and load data into a DataFrame
    df_ofa_RP = pd.read_sql_query(query, conn) #df_ofa_RP = pd.read_csv(ofaS_PATH, delimiter=';', usecols=ofaS_COLS, names=ofaS_NAME, skiprows=1)
    
    df_ofa_RP = df_ofa_RP.drop(['LOT_RELEASED_QTY', 'LOT_REJECT_RELEASED_QTY'], axis=1)
    df_ofa_RP = df_ofa_RP.rename(columns={'SCS_STEP_NUMBER': 'Operation Step', 'SCS_SHORT_DESCR': 'Operation', 'LOT_REFCOMPL': 'ofa', 'FAC_REFERENCE': 'Equipment', 'TAL_BEGIN_REAL_DATE': 'Begin Date', 'TAL_END_REAL_DATE': 'End Date', 'TAL_RELEASE_QTY': 'OK', 'TAL_REJECTED_QTY': 'NOK'})
    temp_df = df_ofa_RP[df_ofa_RP['Operation Step'] == 10]
    ofa_with_10 = temp_df['ofa'].unique()

    df_ofa_RP = df_ofa_RP.groupby('ofa').apply(rename_ops)
    df_ofa_RP = df_ofa_RP.drop('ofa', axis=1)
    df_ofa_RP = df_ofa_RP.reset_index()
    df_ofa_RP = df_ofa_RP.drop('level_1', axis=1)
    df_ofa_RP = df_ofa_RP.sort_values(by=['ofa', 'Operation Step'], ascending=[False, False])
    df_ofa_RP['Operation'] = df_ofa_RP['Operation'].map(OPERATION_DICT_RP).fillna(df_ofa_RP['Operation'])

    cv_df = df_ofa_RP[df_ofa_RP['Operation'] == '50']
    ofa_with_cv = cv_df['ofa'].unique()

    df_ofa_RP['Validation ofa'] = False
    grouped = df_ofa_RP.groupby('ofa')
    for name, _ in grouped:
        base_name = name[:-2]
        if name.endswith('-2') or name.endswith('-3'):
            df_ofa_RP.loc[(df_ofa_RP['ofa'] == base_name + '-1') | (df_ofa_RP['ofa'] == base_name + '-2') | (df_ofa_RP['ofa'] == base_name + '-3'), 'Validation ofa'] = True
    df_ofa_RP['Validation ofa'] = df_ofa_RP['Validation ofa'].astype(int) # (df_ofa_RP['Validation ofa'] == 1) |

    ofa_to_drop = df_ofa_RP.loc[~df_ofa_RP['ofa'].isin(ofa_with_cv) | ~df_ofa_RP['ofa'].isin(ofa_with_10) | df_ofa_RP['Begin Date'].isna() | df_ofa_RP['End Date'].isna() | ((df_ofa_RP['Operation Step'] == 10) & (df_ofa_RP['Operation'] != 'Ten')) , 'ofa'].unique()
    df_ofa_RP = df_ofa_RP.loc[~df_ofa_RP['ofa'].isin(ofa_to_drop)]
    df_ofa_RP['NOK (%)'] = 100*(df_ofa_RP['NOK'] / (df_ofa_RP['OK'] + df_ofa_RP['NOK']))
    df_ofa_RP['Begin Date'] = pd.to_datetime(df_ofa_RP['Begin Date'], errors='coerce')
    df_ofa_RP['Week'] = df_ofa_RP['Begin Date'].dt.to_period('W-SAT').dt.week
    df_ofa_RP['Year'] = (df_ofa_RP['Begin Date'].dt.year).astype(int)

    return df_ofa_RP