"""
Corrige gabaritos no banco lendo PDFs por posição de coluna.
Uso: python corrigir_gabaritos.py [--executar]
"""
import fitz
import re
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

NORMALIZAR = {
    'física': 'fisica', 'fisica': 'fisica',
    'química': 'quimica', 'quimica': 'quimica',
    'matemática': 'matematica', 'matematica': 'matematica',
    'inglês': 'ingles', 'ingles': 'ingles',
    'português': 'portugues', 'portugues': 'portugues',
}

def extrair_gabarito_por_colunas(caminho: str) -> dict:
    """Retorna { disciplina: { numero_absoluto: resposta } }"""
    doc = fitz.open(caminho)
    page = doc[0]
    words = page.get_text("words")

    colunas = {}
    for w in words:
        x0, y0, x1, y1, text, *_ = w
        nome = NORMALIZAR.get(text.lower().strip())
        if nome:
            colunas[(x0 + x1) / 2] = nome

    if not colunas:
        doc.close()
        return {}

    linhas = {}
    for w in words:
        x0, y0, x1, y1, text, *_ = w
        text = text.strip()
        if not text:
            continue
        y_key = round(y0 / 5) * 5
        if y_key not in linhas:
            linhas[y_key] = {}
        linhas[y_key][x0] = text

    gabarito_raw = {disc: {} for disc in colunas.values()}

    for y_key in sorted(linhas.keys()):
        linha = linhas[y_key]
        items = sorted(linha.items())
        for x_num, text_num in items:
            if not re.match(r'^\d+$', text_num):
                continue
            numero = int(text_num)
            if numero < 1 or numero > 200:
                continue
            resposta = None
            for x_resp, text_resp in items:
                if x_num < x_resp < x_num + 80:
                    r = text_resp.strip().upper()
                    if r in ['A', 'B', 'C', 'D', 'E', '*']:
                        resposta = r if r != '*' else 'ANULADA'
                        break
            if resposta is None:
                continue
            dist_min = float('inf')
            disc_col = None
            for cx, disc in colunas.items():
                dist = abs(x_num - cx)
                if dist < dist_min:
                    dist_min = dist
                    disc_col = disc
            if disc_col and dist_min < 80:
                gabarito_raw[disc_col][numero] = resposta

    doc.close()
    return {k: v for k, v in gabarito_raw.items() if v}


def numero_minimo_no_banco(conn, ano: int, fase: str, disciplina: str) -> int:
    """Retorna o menor número de questão no banco para essa combinação."""
    row = conn.execute("""
        SELECT MIN(CAST(numero AS INTEGER)) as min_num
        FROM questoes
        WHERE escola='ITA' AND ano=? AND fase=? AND disciplina=?
    """, (ano, fase, disciplina)).fetchone()
    return row['min_num'] if row and row['min_num'] else 1


def atualizar_banco(gabarito_por_disc: dict, ano: int, fase: str, executar: bool) -> tuple:
    from app.db.database import get_conn
    conn = get_conn()
    atualizadas = 0
    nao_encontradas = 0

    for disciplina, gabarito in gabarito_por_disc.items():
        # Detecta se o banco usa numeração contínua ou relativa para essa disciplina
        min_banco = numero_minimo_no_banco(conn, ano, fase, disciplina)
        min_gab = min(gabarito.keys()) if gabarito else 1

        # Se o banco começa do mesmo número que o gabarito → sem offset
        # Se o banco começa do 1 mas o gabarito começa de outro → aplica offset
        if min_banco == 1 and min_gab > 1:
            offset = min_gab - 1
        else:
            offset = 0

        for numero_abs, resposta in gabarito.items():
            numero_banco = numero_abs - offset

            rows = conn.execute("""
                SELECT id, gabarito FROM questoes
                WHERE escola='ITA' AND ano=? AND fase=?
                AND disciplina=? AND numero=?
            """, (ano, fase, disciplina, numero_banco)).fetchall()

            if not rows:
                nao_encontradas += 1
                continue

            for row in rows:
                if row['gabarito'] != resposta:
                    if executar:
                        conn.execute(
                            "UPDATE questoes SET gabarito=? WHERE id=?",
                            (resposta, row['id'])
                        )
                    atualizadas += 1

    if executar:
        conn.commit()
    conn.close()
    return atualizadas, nao_encontradas


def processar_ano(base: Path, ano: int, executar: bool) -> None:
    for fase_label, nome_arquivo in [('1', f'gabarito_{ano}.pdf'), ('2', f'gabarito_{ano}_2fase.pdf')]:
        gab_path = base / f"ITA {ano}" / nome_arquivo
        if not gab_path.exists():
            continue

        gabarito = extrair_gabarito_por_colunas(str(gab_path))
        if not gabarito:
            print(f"  {ano} fase{fase_label}: nenhum gabarito extraído")
            continue

        print(f"  {ano} fase{fase_label}: {list(gabarito.keys())}")
        for disc, gab in gabarito.items():
            nums = sorted(gab.keys())
            print(f"    {disc}: {len(gab)}q nums={nums[0]}-{nums[-1]}")

        n, erros = atualizar_banco(gabarito, ano, fase_label, executar)
        status = "atualizadas" if executar else "seriam atualizadas"
        print(f"    → {n} {status}", end="")
        if erros:
            print(f" | ⚠ {erros} não encontradas no banco")
        else:
            print()


def main():
    import sys
    executar = '--executar' in sys.argv
    base = Path('/Users/jefersonchagas/Desktop/ITA VESTIBULAR 2008-2025')

    from app.db.database import init_db
    init_db()

    print("=" * 55)
    print(f"MODO: {'EXECUÇÃO' if executar else 'DIAGNÓSTICO'}")
    print("=" * 55)

    for ano in range(2008, 2026):
        if not (base / f"ITA {ano}").exists():
            continue
        processar_ano(base, ano, executar)

    if not executar:
        print("\n[Rode com --executar para aplicar]")


if __name__ == '__main__':
    main()
