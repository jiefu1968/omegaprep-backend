from app.db.database import get_conn, init_db
init_db()

GABARITO_2017 = {
    'fisica':     {1:'A',2:'A',3:'D',4:'E',5:'B',6:'E',7:'ANULADA',8:'D',9:'D',10:'B',11:'C',12:'C',13:'C',14:'B',15:'A',16:'D',17:'A',18:'B',19:'E',20:'ANULADA'},
    'ingles':     {1:'C',2:'A',3:'D',4:'C',5:'A',6:'D',7:'C',8:'A',9:'B',10:'E',11:'D',12:'D',13:'B',14:'E',15:'A',16:'B',17:'D',18:'B',19:'E',20:'C'},
    'portugues':  {21:'E',22:'E',23:'D',24:'A',25:'C',26:'A',27:'C',28:'E',29:'C',30:'E',31:'A',32:'C',33:'B',34:'A',35:'E',36:'B',37:'C',38:'D',39:'E',40:'E'},
    'matematica': {1:'A',2:'A',3:'D',4:'B',5:'C',6:'C',7:'C',8:'E',9:'A',10:'C',11:'A',12:'E',13:'A',14:'B',15:'D',16:'A',17:'D',18:'B',19:'E',20:'E'},
    'quimica':    {1:'A',2:'B',3:'D',4:'D',5:'A',6:'D',7:'C',8:'A',9:'E',10:'E',11:'E',12:'C',13:'E',14:'D',15:'C',16:'D',17:'A',18:'B',19:'C',20:'B'},
}

conn = get_conn()
total = 0
for disc, gab in GABARITO_2017.items():
    for numero, resposta in gab.items():
        rows = conn.execute("""
            SELECT id FROM questoes
            WHERE escola='ITA' AND ano=2017 AND fase='1'
            AND disciplina=? AND numero=?
        """, (disc, numero)).fetchall()
        for row in rows:
            conn.execute("UPDATE questoes SET gabarito=? WHERE id=?", (resposta, row['id']))
            total += 1

conn.commit()
conn.close()
print(f"2017 corrigido: {total} questões atualizadas")
