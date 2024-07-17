#import cx_Oracle

import pandas as pd

from pathlib import Path

from dicts import OPERATION_DICT_RP

OFAS_PATH = Path("C:/Users/a22006/Desktop/Dashboard_hmsa/OFAs.csv") # Path("/Users/leondeligny/Desktop/Master/Dashboard_hmsa/OFAs.csv")

OFAS_COLS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
OFAS_NAME = ["LOT_REFCOMPL", "LOT_RELEASED_QTY", "LOT_REJECT_RELEASED_QTY", "FAC_REFERENCE", "KEY", "SCS_STEP_NUMBER", "TAS_REF", "SCS_SHORT_DESCR", "TAL_RELEASE_QTY", "TAL_REJECTED_QTY", "TAL_BEGIN_REAL_DATE", "TAL_END_REAL_DATE"]

def rename_ops(group):
        ctrl_counter = 0
        lav_counter = 0
        new_descriptions = []
        for op in group['Operation']:
            if op == 'Opération CONTROLER':
                if ctrl_counter == 0:
                    new_descriptions.append('Ctrl F')
                elif ctrl_counter == 1:
                    new_descriptions.append('Visual')
                else: # Handles all cases after the first and second
                    new_descriptions.append('Dimensional')
                ctrl_counter += 1
            elif op == 'Opération LAVER':
                if lav_counter == 0:
                    new_descriptions.append('Lavage F')
                else:
                    new_descriptions.append('Lavage Tribo')
                lav_counter += 1
            else:
                new_descriptions.append(op) # doesn't change the non 'Opération CONTROLER'
        group['Operation'] = new_descriptions
        return group

def df_erp_load():
    # 
    # '''# ODBC, DRIVER={oracle_12g_64bit}, Database=PCERP, DBQ=PCERP, UID=C_HERA, PWD=C_HERA
    # connection = pyodbc.connect("DRIVER={oracle_12g_64bit}, Database=PCERP, DBQ=PCERP, UID=C_HERA, PWD=C_HERA")
    # sql_statement = """select lot_refcompl, fac_reference, tal_begin_real_date, tal_end_real_date, tal_plan_qty,
    #                 tal_release_qty, tal_rejected_qty from fal_lot inner join fal_task_link using (fal_lot_id)
    #                 inner join fal_factory_floor using (fal_factory_floor_id) where gco_good_id in
    #                 (select gco_good_id from gco_good where goo_major_reference in ('PMCO-00589', 'PMCO-00223'))
    #                 and scs_short_descr like '%TOURNER%' order by 3 desc"""
    # df_OFA_to_PDC = pd.read_sql(sql_statement, connection)
    # print(df_OFA_to_PDC)
    # '''
    # connection = pyodbc.connect("DRIVER={oracle_12g_64bit}, Database=PCERP, DBQ=PCERP, UID=C_HERA, PWD=C_HERA")
    '''
    dsn = cx_Oracle.makedsn('172.30.45.32', '1521', 'PCERP')
    connection = cx_Oracle.connect('C_HERA', 'C_HERA', dsn)
    sql_statement_RP =  """
        select lot_refcompl, lot_released_qty, lot_reject_released_qty,
        fac_reference,  replace(replace(scs_short_descr,
        'Opération ', ''), 'Libération ', '')||'-'||fac_reference
        key, scs_step_number, tas_ref, scs_short_descr,
        tal_release_qty, tal_rejected_qty, tal_begin_real_date,
        tal_end_real_date -- fal_task_id

        from fal_lot inner join fal_task_link
        using (fal_lot_id) inner join gco_good
        using (gco_good_id) inner join fal_factory_floor
        using (fal_factory_floor_id) inner join fal_task
        using (fal_task_id)

        where  lot_plan_begin_dte >= to_date('20230101','YYYYMMDD')
        and goo_major_reference in ('PMCO-00223', 'PMCO-00589',
        'PMCO-00457')

        order by lot_refcompl desc, scs_step_number desc
        """
    df_OFA_RP = pd.read_sql(sql_statement_RP, connection) 
    '''

    df_OFA_RP = pd.read_csv(OFAS_PATH, delimiter=';', usecols=OFAS_COLS, names=OFAS_NAME, skiprows=1)
    
    df_OFA_RP = df_OFA_RP.drop(['LOT_RELEASED_QTY', 'LOT_REJECT_RELEASED_QTY'], axis=1)
    df_OFA_RP = df_OFA_RP.rename(columns={'SCS_STEP_NUMBER': 'Operation Step', 'SCS_SHORT_DESCR': 'Operation', 'LOT_REFCOMPL': 'OFA', 'FAC_REFERENCE': 'Equipment', 'TAL_BEGIN_REAL_DATE': 'Begin Date', 'TAL_END_REAL_DATE': 'End Date', 'TAL_RELEASE_QTY': 'OK', 'TAL_REJECTED_QTY': 'NOK'})
    temp_df = df_OFA_RP[df_OFA_RP['Operation Step'] == 10]
    ofa_with_10 = temp_df['OFA'].unique()

    df_OFA_RP = df_OFA_RP.groupby('OFA').apply(rename_ops)
    df_OFA_RP = df_OFA_RP.drop('OFA', axis=1)
    df_OFA_RP = df_OFA_RP.reset_index()
    df_OFA_RP = df_OFA_RP.drop('level_1', axis=1)
    df_OFA_RP = df_OFA_RP.sort_values(by=['OFA', 'Operation Step'], ascending=[False, False])
    df_OFA_RP['Operation'] = df_OFA_RP['Operation'].map(OPERATION_DICT_RP).fillna(df_OFA_RP['Operation'])

    cv_df = df_OFA_RP[df_OFA_RP['Operation'] == 'Dimensional']
    ofa_with_cv = cv_df['OFA'].unique()

    df_OFA_RP['Validation OFA'] = False
    grouped = df_OFA_RP.groupby('OFA')
    for name, _ in grouped:
        base_name = name[:-2]
        if name.endswith('-2') or name.endswith('-3'):
            df_OFA_RP.loc[(df_OFA_RP['OFA'] == base_name + '-1') | (df_OFA_RP['OFA'] == base_name + '-2') | (df_OFA_RP['OFA'] == base_name + '-3'), 'Validation OFA'] = True
    df_OFA_RP['Validation OFA'] = df_OFA_RP['Validation OFA'].astype(int) # (df_OFA_RP['Validation OFA'] == 1) |

    ofa_to_drop = df_OFA_RP.loc[(df_OFA_RP['Equipment'] == 'A700HOR') | (df_OFA_RP['Equipment'] == 'A620HOR029') | ~df_OFA_RP['OFA'].isin(ofa_with_cv) | ~df_OFA_RP['OFA'].isin(ofa_with_10) | df_OFA_RP['Begin Date'].isna() | df_OFA_RP['End Date'].isna() | ((df_OFA_RP['Operation Step'] == 10) & (df_OFA_RP['Operation'] != 'Machining')) , 'OFA'].unique()
    df_OFA_RP = df_OFA_RP.loc[~df_OFA_RP['OFA'].isin(ofa_to_drop)]
    df_OFA_RP['NOK (%)'] = 100*(df_OFA_RP['NOK'] / (df_OFA_RP['OK'] + df_OFA_RP['NOK']))
    df_OFA_RP['Begin Date'] = pd.to_datetime(df_OFA_RP['Begin Date'], errors='coerce')
    df_OFA_RP['Week'] = df_OFA_RP['Begin Date'].dt.to_period('W-SAT').dt.week
    df_OFA_RP['Year'] = (df_OFA_RP['Begin Date'].dt.year).astype(int)

    return df_OFA_RP