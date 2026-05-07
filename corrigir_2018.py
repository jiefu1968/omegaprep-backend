from app.db.database import get_conn, init_db
init_db()

GABARITO_2018 = {
    'fisica':     {1:'E',2:'C',3:'C',4:'B',5:'A',6:'C',7:'B',8:'E',9:'E',10:'D',11:'E',12:'D',13:'D',14:'B',15:'C',16:'A',17:'B',18:'A',19:'A',20:'C'},
    'ingles':     {1:'B',2:'D',3:'C',4:'B',5:'C',6:'C',7:'D',8:'D',9:'A',10:'E',11:'C',12:'A',13:'E',14:'D',15:'B',16:'A',17:'E',18:'B',19:'D',20:'E'},
    'portugues':  {21:'B',22:'D',23:'E',24:'E',25:'B',26:'D',27:'C',28:'E',29:'C',30:'E',31:'C',32:'A',33:'E',34:'C',35:'A',36:'D',37:'B',38:'B',39:'A',40:'E'},
    'matematica': {1:'A',2:'C',3:'B',4:'A',5:'B',6:'E',7:'C',8:'D',9:'E',10:'C',11:'D',12:'B',13:'E',14:'B',15:'D',16:'D',17:'A',18:'A',19:'E',20:'E'},
    'quimica':    {1:'C',2:'E',3:'A',4:'ANULADA',5:'D',6:'C',7:'D',8:'C',9:'E',10:'E',11:'A',12:'B',13:'C',14:'C',15:'A',16:'E',17:'B',18:'D',19:'D',20:'B'},
}

conn = get_conn()
total = 0
for disc, gab in GABARITO_2018.items():
    for numero, resposta in gab.items():
        rows = conn.execute("""
            SELECT id FROM questoes
            WHERE escola='ITA' AND ano=2018 AND fase='1'
            AND disciplina=? AND numero=?
        """, (disc, numero)).fetchall()
        for row in rows:
            conn.execute("UPDATE questoes SET gabarito=? WHERE id=?", (resposta, row['id']))
            total += 1

conn.commit()
conn.close()
print(f"2018 corrigido: {total} questões atualizadas")
