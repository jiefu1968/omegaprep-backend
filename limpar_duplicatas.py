import sqlite3, shutil, sys, os
from datetime import datetime

DB_PATH = os.path.expanduser("~/MeusProjetos/omegaprep-backend/omegaprep.db")

def conectar():
    if not os.path.exists(DB_PATH):
        print(f"ERRO: Banco não encontrado em {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def diagnosticar(conn):
    cursor = conn.cursor()
    print("\n" + "="*60)
    print("DIAGNOSTICO DE DUPLICATAS — OmegaPrep")
    print("="*60)
    cursor.execute("SELECT COUNT(*) FROM questoes")
    total = cursor.fetchone()[0]
    print(f"\nTotal de questoes no banco: {total}")
    cursor.execute("""
        SELECT escola, disciplina, ano, fase, COUNT(*) as total
        FROM questoes GROUP BY escola, disciplina, ano, fase
        HAVING COUNT(*) > 30 ORDER BY escola, ano, disciplina
    """)
    suspeitos = cursor.fetchall()
    if suspeitos:
        print(f"\nGrupos com mais de 30 questoes:")
        print(f"  {'Escola':<8} {'Disciplina':<15} {'Ano':<6} {'Fase':<6} {'Total'}")
        print("  " + "-"*50)
        for escola, disc, ano, fase, tot in suspeitos:
            print(f"  {escola:<8} {disc:<15} {str(ano):<6} {str(fase or 'unica'):<6} {tot}")
    cursor.execute("""
        SELECT escola, disciplina, ano, fase, enunciado, COUNT(*) as cnt,
               GROUP_CONCAT(id) as ids
        FROM questoes GROUP BY escola, disciplina, ano, fase, enunciado
        HAVING COUNT(*) > 1 ORDER BY escola, ano, disciplina
    """)
    dups = cursor.fetchall()
    print(f"\nDuplicatas por enunciado identico: {len(dups)} grupos")
    ids_deletar = set()
    for escola, disc, ano, fase, enunciado, cnt, ids_str in dups:
        ids = ids_str.split(",")
        manter = ids[0]
        deletar = ids[1:]
        ids_deletar.update(deletar)
        print(f"  {escola} {disc} {ano} fase={fase} | manter={manter} | deletar {len(deletar)} registro(s)")
    cursor.execute("""
        SELECT escola, disciplina, ano, fase, numero, COUNT(*) as cnt,
               GROUP_CONCAT(id) as ids
        FROM questoes GROUP BY escola, disciplina, ano, fase, numero
        HAVING COUNT(*) > 1 ORDER BY escola, ano, disciplina
    """)
    dups2 = cursor.fetchall()
    print(f"\nDuplicatas por numero identico: {len(dups2)} grupos")
    for escola, disc, ano, fase, num, cnt, ids_str in dups2:
        ids = ids_str.split(",")
        manter = ids[0]
        deletar = ids[1:]
        for d in deletar:
            ids_deletar.add(d)
        print(f"  {escola} {disc} {ano} fase={fase} num={num} | deletar {len(deletar)} registro(s)")
    print(f"\n{'='*60}")
    print(f"Total a deletar: {len(ids_deletar)}")
    print(f"Restara no banco: {total - len(ids_deletar)}")
    print(f"{'='*60}")
    return list(ids_deletar)

def main():
    conn = conectar()
    try:
        ids = diagnosticar(conn)
        if "--executar" not in sys.argv:
            print("\n[DIAGNOSTICO APENAS — nada foi alterado]")
            print("Para limpar: python limpar_duplicatas.py --executar\n")
            return
        if not ids:
            print("Nada a deletar.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bkp = DB_PATH.replace(".db", f"_backup_{ts}.db")
        shutil.copy2(DB_PATH, bkp)
        print(f"\nBackup salvo: {bkp}")
        cursor = conn.cursor()
        for i in range(0, len(ids), 500):
            batch = ids[i:i+500]
            cursor.execute(f"DELETE FROM questoes WHERE id IN ({','.join('?'*len(batch))})", batch)
        conn.commit()
        cursor.execute("VACUUM")
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM questoes")
        print(f"Concluido! Restaram {cursor.fetchone()[0]} questoes.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
