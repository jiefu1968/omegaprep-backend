from app.db.database import get_conn, init_db
init_db()

GABARITO_2016 = {
    'fisica':     {1:'E',2:'C',3:'D',4:'ANULADA',5:'A',6:'C',7:'D',8:'A',9:'C',10:'D',11:'D',12:'C',13:'C',14:'A',15:'C',16:'D',17:'C',18:'C',19:'A',20:'E'},
    'ingles':     {1:'E',2:'C',3:'B',4:'C',5:'E',6:'A',7:'C',8:'C',9:'A',10:'B',11:'C',12:'A',13:'D',14:'D',15:'D',16:'E',17:'B',18:'E',19:'B',20:'A'},
    'portugues':  {21:'B',22:'D',23:'E',24:'C',25:'A',26:'C',27:'D',28:'B',29:'A',30:'D',31:'B',32:'C',33:'A',34:'E',35:'E',36:'B',37:'D',38:'E',39:'C',40:'C'},
    'matematica': {1:'B',2:'D',3:'ANULADA',4:'B',5:'D',6:'D',7:'B',8:'A',9:'A',10:'D',11:'C',12:'B',13:'E',14:'D',15:'C',16:'A',17:'B',18:'E',19:'E',20:'D'},
    'quimica':    {1:'A',2:'E',3:'ANULADA',4:'E',5:'C',6:'C',7:'D',8:'D',9:'D',10:'B',11:'A',12:'A',13:'C',14:'D',15:'E',16:'C',17:'B',18:'B',19:'D',20:'ANULADA'},
}

conn = get_conn()
total = 0
for disc, gab in GABARITO_2016.items():
    for numero, resposta in gab.items():
        rows = conn.execute("""
            SELECT id FROM questoes
            WHERE escola='ITA' AND ano=2016 AND fase='1'
            AND disciplina=? AND numero=?
        """, (disc, numero)).fetchall()
        for row in rows:
            conn.execute("UPDATE questoes SET gabarito=? WHERE id=?", (resposta, row['id']))
            total += 1

conn.commit()
conn.close()
print(f"2016 corrigido: {total} questões atualizadas")
