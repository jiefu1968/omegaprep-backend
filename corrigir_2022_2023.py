from app.db.database import get_conn, init_db
init_db()

GABARITOS = {
    2022: {
        'fisica':    {1:'B',2:'D',3:'ANULADA',4:'A',5:'C',6:'C',7:'E',8:'ANULADA',9:'A',10:'B',11:'E',12:'A',13:'C',14:'A',15:'B'},
        'portugues': {16:'C',17:'E',18:'A',19:'E',20:'E',21:'B',22:'B',23:'B',24:'ANULADA',25:'C',26:'A',27:'D',28:'D',29:'C',30:'E'},
        'ingles':    {31:'C',32:'A',33:'B',34:'C',35:'B',36:'C',37:'D',38:'B',39:'E',40:'A'},
        'matematica':{41:'B',42:'E',43:'C',44:'A',45:'D',46:'E',47:'D',48:'C',49:'D',50:'A',51:'C',52:'A',53:'C',54:'C',55:'C'},
        'quimica':   {56:'D',57:'D',58:'B',59:'A',60:'ANULADA',61:'B',62:'D',63:'B',64:'A',65:'D',66:'E',67:'B',68:'B',69:'E',70:'A'},
    },
    2023: {
        'fisica':    {1:'D',2:'E',3:'E',4:'C',5:'C',6:'ANULADA',7:'B',8:'C',9:'E',10:'E',11:'B',12:'D'},
        'portugues': {13:'E',14:'B',15:'B',16:'E',17:'A',18:'ANULADA',19:'B',20:'D',21:'B',22:'E',23:'A',24:'C'},
        'ingles':    {25:'A',26:'D',27:'D',28:'B',29:'B',30:'E',31:'D',32:'B',33:'B',34:'B',35:'D',36:'C'},
        'matematica':{37:'C',38:'E',39:'B',40:'C',41:'B',42:'D',43:'D',44:'A',45:'B',46:'E',47:'A',48:'C'},
        'quimica':   {49:'E',50:'C',51:'B',52:'D',53:'D',54:'A',55:'A',56:'C',57:'E',58:'B',59:'A',60:'B'},
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
