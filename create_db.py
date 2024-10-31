import sqlite3

import pandas as pd

# Load the CSV data
df = pd.read_csv('csv/ofas.csv', sep=';') # "ofa"; "dte"; "uusr"; "usr"; "shift"; "ope"; "qty_ok"; "qty_ko"; "defaults"; "comments"

# Define the SQLite database
conn = sqlite3.connect('database2.db')
cursor = conn.cursor()

# Drop the table if it already exists
cursor.execute('DROP TABLE IF EXISTS ofas')

# Create the table
cursor.execute('''
CREATE TABLE ofas (
    LOT_REFCOMPL TEXT, 
    LOT_RELEASED_QTY INTEGER,
    LOT_REJECT_RELEASED_QTY INTEGER,
    FAC_REFERENCE TEXT,
    SCS_STEP_NUMBER INTEGER,
    TAS_REF TEXT,
    SCS_SHORT_DESCR TEXT,
    TAL_RELEASE_QTY INTEGER,
    TAL_REJECTED_QTY INTEGER,
    TAL_BEGIN_REAL_DATE TEXT,
    TAL_END_REAL_DATE TEXT
)
''')

# Process the DataFrame and insert data into the database
for index, row in df.iterrows():
    cursor.execute('''
        INSERT INTO ofas (LOT_REFCOMPL, LOT_RELEASED_QTY, LOT_REJECT_RELEASED_QTY, FAC_REFERENCE, SCS_STEP_NUMBER, TAS_REF, SCS_SHORT_DESCR, TAL_RELEASE_QTY, TAL_REJECTED_QTY, TAL_BEGIN_REAL_DATE, TAL_END_REAL_DATE)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
            row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4], row.iloc[5], 
            row.iloc[6], row.iloc[7], row.iloc[8], row.iloc[9], row.iloc[10]
        ))

# Commit the transaction and close the connection
conn.commit()
conn.close()

# Load the CSV data
df = pd.read_csv('csv/pp_tracking.csv', sep=';') # ofa; dte; uusr; usr; shift; ope; qty_ok; qty_ko; defaults; comments

# Define the SQLite database
conn = sqlite3.connect('database1.db')
cursor = conn.cursor()

# Drop the table if it already exists
cursor.execute('DROP TABLE IF EXISTS pp_tracking')

# Create the table
cursor.execute('''
CREATE TABLE pp_tracking (
    ofa TEXT,
    dte TEXT,
    uusr TEXT,
    usr TEXT,
    shift INTEGER,
    ope TEXT,
    qty_ok INTEGER,
    qty_ko INTEGER,
    defaults TEXT,
    comments TEXT
)
''')

# Process the DataFrame and insert data into the database
for index, row in df.iterrows():
    cursor.execute('''
        INSERT INTO pp_tracking (ofa, dte, uusr, usr, shift, ope, qty_ok, qty_ko, defaults, comments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4], row.iloc[5], 
          row.iloc[6], row.iloc[7], row.iloc[8], row.iloc[9]
          ))
        

# Commit the transaction and close the connection
conn.commit()
conn.close()


# Load the CSV data
df = pd.read_csv('csv/defaults.csv', sep=';') # "def_id"; "def_name"; "def_descr"; "def_domain";

# Define the SQLite database
conn = sqlite3.connect('database1.db')
cursor = conn.cursor()

# Drop the table if it already exists
cursor.execute('DROP TABLE IF EXISTS prod_defaults')

# Create the table
cursor.execute('''
CREATE TABLE prod_defaults (
    def_id INT,
    def_name TEXT,
    def_descr TEXT,
    def_domain TEXT
)
''')

# Process the DataFrame and insert data into the database
for index, row in df.iterrows():
    cursor.execute('''
        INSERT INTO prod_defaults (def_id, def_name, def_descr, def_domain)
        VALUES (?, ?, ?, ?)
    ''', (row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3]
        ))

# Commit the transaction and close the connection
conn.commit()
conn.close()

# Load the CSV data
df = pd.read_csv('csv/pp_tracking.csv', sep=';')

# Define the SQLite database
conn = sqlite3.connect('database1.db')
cursor = conn.cursor()

# Drop the table if it already exists
cursor.execute('DROP TABLE IF EXISTS pp_tracking')

# Create the table
cursor.execute('''
CREATE TABLE pp_tracking (
    ofa TEXT,
    dte TEXT,
    uusr TEXT,
    usr TEXT,
    shift INTEGER,
    ope TEXT,
    qty_ok INTEGER,
    qty_ko INTEGER,
    defaults TEXT,
    comments TEXT
)
''')

# Process the DataFrame and insert data into the database
for index, row in df.iterrows():
    cursor.execute('''
        INSERT INTO pp_tracking (ofa, dte, uusr, usr, shift, ope, qty_ok, qty_ko, defaults, comments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4], row.iloc[5], 
          row.iloc[6], row.iloc[7], row.iloc[8], row.iloc[9]
        )
    )

# Commit the transaction and close the connection
conn.commit()
conn.close()

# Load the CSV data
df = pd.read_csv('csv/smc_tracking.csv', sep=';') # id; usr; dte; shift; pdc; qty_ok; qty_ko; d0; d1; d2; d3; d4; d5; d6; comments; ofa; week; defaults

# Define the SQLite database
conn = sqlite3.connect('database1.db')
cursor = conn.cursor()

# Drop the table if it already exists
cursor.execute('DROP TABLE IF EXISTS uu_tracking')

# Create the table
cursor.execute('''
CREATE TABLE uu_tracking (
    id INTEGER,
    usr TEXT,
    dte TEXT,
    shift INTEGER,
    pdc TEXT,
    qty_ok INTEGER,
    qty_ko INTEGER,
    d0 INTEGER,
    d1 INTEGER,
    d2 INTEGER,
    d3 INTEGER,
    d4 INTEGER,
    d5 INTEGER,
    d6 INTEGER,
    comments TEXT,
    ofa TEXT,
    week TEXT,
    defaults TEXT
)
''')

# Process the DataFrame and insert data into the database
for index, row in df.iterrows():
    cursor.execute('''
        INSERT INTO uu_tracking (id, usr, dte, shift, pdc, qty_ok, qty_ko, d0, d1, d2, d3, d4, d5, d6, comments, ofa, week, defaults)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4], row.iloc[5], 
          row.iloc[6], row.iloc[7], row.iloc[8], row.iloc[9], row.iloc[10], row.iloc[11], 
          row.iloc[12], row.iloc[13], row.iloc[14], row.iloc[15], row.iloc[16], row.iloc[17]
        )
    )

# Commit the transaction and close the connection
conn.commit()
conn.close()