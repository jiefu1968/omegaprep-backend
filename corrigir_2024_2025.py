from app.db.database import get_conn, init_db
init_db()

conn = get_conn()

# 2024 fase 1
GAB_2024 = {
    'fisica':    {1:'D',2:'D',3:'C',4:'B',5:'B',6:'B',7:'E',8:'A',9:'E',10:'ANULADA',11:'C',12:'C'},
    'portugues': {13:'E',14:'D',15:'D',16:'B',17:'B',18:'B',19:'D',20:'C',21:'D',22:'D',23:'D',24:'C'},
    'ingles':    {25:'B',26:'A',27:'D',28:'C',29:'E',30:'D',31:'E',32:'C',33:'D',34:'C',35:'A',36:'B'},
    'matematica':{37:'B',38:'E',39:'A',40:'B',41:'D',42:'C',43:'E',44:'D',45:'C',46:'D',47:'A',48:'C'},
    'quimica':   {49:'C',50:'C',51:'E',52:'E',53:'D',54:'A',55:'A',56:'B',57:'C',58:'B',59:'D',60:'B'},
}
total = 0
for disc, gab in GAB_2024.items():
    for numero, resposta in gab.items():
        rows = conn.execute("SELECT id FROM questoes WHERE escola='ITA' AND ano=2024 AND fase='1' AND disciplina=? AND numero=?", (disc, numero)).fetchall()
        for row in rows:
            conn.execute("UPDATE questoes SET gabarito=? WHERE id=?", (resposta, row['id']))
            total += 1
conn.commit()
print(f"2024 fase1 corrigido: {total} questões")

# 2025 fase 1
GAB_2025_F1 = {
    'matematica':{1:'B',2:'E',3:'C',4:'D',5:'D',6:'B',7:'A',8:'E',9:'ANULADA',10:'D',11:'A',12:'C'},
    'fisica':    {13:'B',14:'A',15:'B',16:'D',17:'B',18:'ANULADA',19:'C',20:'D',21:'A',22:'B',23:'C',24:'E'},
    'quimica':   {25:'B',26:'A',27:'B',28:'C',29:'B',30:'D',31:'B',32:'A',33:'C',34:'D',35:'E',36:'C'},
    'ingles':    {37:'C',38:'B',39:'D',40:'B',41:'D',42:'A',43:'C',44:'E',45:'E',46:'B',47:'C',48:'E'},
}
total = 0
for disc, gab in GAB_2025_F1.items():
    for numero, resposta in gab.items():
        rows = conn.execute("SELECT id FROM questoes WHERE escola='ITA' AND ano=2025 AND fase='1' AND disciplina=? AND numero=?", (disc, numero)).fetchall()
        for row in rows:
            conn.execute("UPDATE questoes SET gabarito=? WHERE id=?", (resposta, row['id']))
            total += 1
conn.commit()
print(f"2025 fase1 corrigido: {total} questões")

# 2025 fase 2
GAB_2025_F2 = {
    'portugues': {1:'D',2:'E',3:'D',4:'A',5:'B',6:'C',7:'B',8:'B',9:'B',10:'A',11:'B',12:'A',13:'D',14:'B',15:'C'},
}
total = 0
for disc, gab in GAB_2025_F2.items():
    for numero, resposta in gab.items():
        rows = conn.execute("SELECT id FROM questoes WHERE escola='ITA' AND ano=2025 AND fase='2' AND disciplina=? AND numero=?", (disc, numero)).fetchall()
        for row in rows:
            conn.execute("UPDATE questoes SET gabarito=? WHERE id=?", (resposta, row['id']))
            total += 1
conn.commit()
print(f"2025 fase2 corrigido: {total} questões")

conn.close()
