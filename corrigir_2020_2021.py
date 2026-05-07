from app.db.database import get_conn, init_db
init_db()

GABARITOS = {
    2020: {
        'fisica':    {1:'B',2:'E',3:'C',4:'A',5:'C',6:'D',7:'B',8:'A',9:'B',10:'E',11:'C',12:'ANULADA',13:'C',14:'E',15:'E'},
        'portugues': {16:'C',17:'B',18:'B',19:'D',20:'A',21:'B',22:'E',23:'D',24:'A',25:'D',26:'E',27:'B',28:'A',29:'D',30:'E'},
        'ingles':    {31:'D',32:'ANULADA',33:'B',34:'E',35:'D',36:'A',37:'D',38:'E',39:'D',40:'C'},
        'matematica':{41:'A',42:'D',43:'A',44:'C',45:'C',46:'B',47:'E',48:'B',49:'E',50:'D',51:'C',52:'C',53:'B',54:'A',55:'B'},
        'quimica':   {56:'D',57:'A',58:'E',59:'D',60:'ANULADA',61:'B',62:'D',63:'E',64:'D',65:'A',66:'E',67:'C',68:'E',69:'B',70:'A'},
    },
    2021: {
        'fisica':    {1:'B',2:'D',3:'B',4:'B',5:'C',6:'C',7:'E',8:'C',9:'B',10:'E',11:'E',12:'ANULADA',13:'D',14:'A',15:'E'},
        'portugues': {16:'D',17:'B',18:'D',19:'C',20:'E',21:'C',22:'A',23:'E',24:'D',25:'A',26:'C',27:'B',28:'C',29:'D',30:'B'},
        'ingles':    {31:'B',32:'C',33:'ANULADA',34:'E',35:'E',36:'B',37:'E',38:'A',39:'D',40:'C'},
        'matematica':{41:'D',42:'D',43:'E',44:'D',45:'D',46:'B',47:'C',48:'A',49:'B',50:'E',51:'A',52:'B',53:'B',54:'E',55:'C'},
        'quimica':   {56:'D',57:'B',58:'D',59:'E',60:'D',61:'B',62:'E',63:'A',64:'C',65:'C',66:'A',67:'E',68:'E',69:'A',70:'C'},
    }
}

conn = get_conn()
for ano, disciplinas in GABARITOS.items():
    total = 0
    for disc, gab in disciplinas.items():
        for numero, resposta in gab.items():
            rows = conn.execute("""
                SELECT id FROM questoes
                WHERE escola='ITA' AND ano=? AND fase='1'
                AND disciplina=? AND numero=?
            """, (ano, disc, numero)).fetchall()
            for row in rows:
                conn.execute("UPDATE questoes SET gabarito=? WHERE id=?", (resposta, row['id']))
                total += 1
    conn.commit()
    print(f"{ano} corrigido: {total} questões atualizadas")

conn.close()
