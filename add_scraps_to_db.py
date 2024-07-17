import psycopg2

conn = psycopg2.connect(
    dbname='hmsa2',
    user='hmsait',
    password='h46bh2j0',
    host='172.30.45.67',
)
cur = conn.cursor()

query = """
INSERT INTO prod_defaults (def_name, def_descr, def_domain, def_seq) VALUES 
('d200', 'arrachement mat. 3 Trous', 'uu10', 1),
('d201', 'arrachement mat. - fond ⌀ 2.083 mm', 'uu10', 1),
('d202', 'arrachement mat. - petite Colerette', 'uu10', 1),
('d203', 'arrachement mat. / bavure T1-T2-T3', 'uu10', 1),
('d204', 'E10-E120', 'uu10', 1),
('d205', 'bavures trous transverseaux', 'uu10', 1),
('d206', 'bosselage', 'uu10', 1),
('d207', 'coups dans l"arche', 'uu10', 1),
('d208', 'décalage triangle (≠ épaisseur paroi)', 'uu10', 1),
('d209', 'grande colerette écrasée / déformée', 'uu10', 1),
('d210', '3 trous décalés', 'uu10', 1),
('d211', '6 trous abimés extérieur', 'uu10', 1),
('d212', 'manque usinage (perçage, arche …)', 'uu10', 1),
('d213', 'marque 6 Trous E10-E60', 'uu10', 1),
('d214', 'marque 6 Trous E120-E170', 'uu10', 1),
('d215', 'marque ⌀ Intérieur E10-E60', 'uu10', 1),
('d216', 'marque ⌀ Intérieur E120-E170', 'uu10', 1),
('d217', 'marque colerette', 'uu10', 1),
('d218', 'marque de Mors', 'uu10', 1),
('d219', 'paroi extérieur abimée ⌀ 2.235 mm', 'uu10', 1),
('d220', 'paroi triangle abimée', 'uu10', 1),
('d221', 'plat dans l"arche', 'uu10', 1),
('d222', 'rayures dans les 3 trous', 'uu10', 1),
('d223', 'trou transversal abimé', 'uu10', 1),
('d224', 'pièce pliée abimée', 'uu10', 1),
('d225', 'autre - divers', 'uu10', 1);
"""

cur.execute(query)
conn.commit()

cur.close()
conn.close()
