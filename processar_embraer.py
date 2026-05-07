"""
Processa provas EMBRAER com Claude Vision.
Uso: python processar_embraer.py --ano 2023 [--executar]
"""
import argparse, base64, json, re, sys
from pathlib import Path
from uuid import uuid4
import fitz
from dotenv import load_dotenv
load_dotenv()
from app.llm import get_claude
from app.db.database import get_conn, init_db

BASE = '/Users/jefersonchagas/Desktop/omegaprep vestibulares/VESTIBULARES /EMBRAER/'

MAPEAMENTO = {
    2014: [
        {'caderno': 1,  'pg_inicio': 1,  'pg_fim': 20, 'q_inicio': 1,  'q_fim': 31},
        {'caderno': 2,  'pg_inicio': 1,  'pg_fim': 17, 'q_inicio': 32, 'q_fim': 60},
    ],
    2015: [
        {'caderno': 3,  'pg_inicio': 1,  'pg_fim': 20, 'q_inicio': 1,  'q_fim': 34},
        {'caderno': 4,  'pg_inicio': 1,  'pg_fim': 17, 'q_inicio': 35, 'q_fim': 60},
    ],
    2016: [
        {'caderno': 5,  'pg_inicio': 5,  'pg_fim': 20, 'q_inicio': 1,  'q_fim': 34},
        {'caderno': 6,  'pg_inicio': 1,  'pg_fim': 17, 'q_inicio': 35, 'q_fim': 60},
    ],
    2017: [
        {'caderno': 7,  'pg_inicio': 1,  'pg_fim': 20, 'q_inicio': 1,  'q_fim': 28},
        {'caderno': 8,  'pg_inicio': 1,  'pg_fim': 20, 'q_inicio': 29, 'q_fim': 60},
    ],
    2018: [
        {'caderno': 9,  'pg_inicio': 7,  'pg_fim': 19, 'q_inicio': 1,  'q_fim': 30},
        {'caderno': 10, 'pg_inicio': 1,  'pg_fim': 20, 'q_inicio': 31, 'q_fim': 56},
        {'caderno': 11, 'pg_inicio': 1,  'pg_fim': 3,  'q_inicio': 57, 'q_fim': 60},
    ],
    2019: [
        {'caderno': 11, 'pg_inicio': 11, 'pg_fim': 19, 'q_inicio': 1,  'q_fim': 20},
        {'caderno': 12, 'pg_inicio': 1,  'pg_fim': 20, 'q_inicio': 21, 'q_fim': 48},
        {'caderno': 13, 'pg_inicio': 1,  'pg_fim': 9,  'q_inicio': 49, 'q_fim': 60},
    ],
    2020: [
        {'caderno': 13, 'pg_inicio': 17, 'pg_fim': 20, 'q_inicio': 1,  'q_fim': 8},
        {'caderno': 14, 'pg_inicio': 1,  'pg_fim': 20, 'q_inicio': 9,  'q_fim': 44},
        {'caderno': 15, 'pg_inicio': 1,  'pg_fim': 10, 'q_inicio': 45, 'q_fim': 60},
    ],
    2021: [
        {'caderno': 15, 'pg_inicio': 17, 'pg_fim': 20, 'q_inicio': 1,  'q_fim': 7},
        {'caderno': 16, 'pg_inicio': 1,  'pg_fim': 20, 'q_inicio': 8,  'q_fim': 44},
        {'caderno': 17, 'pg_inicio': 1,  'pg_fim': 9,  'q_inicio': 45, 'q_fim': 60},
    ],
    2022: [
        {'caderno': 17, 'pg_inicio': 13, 'pg_fim': 20, 'q_inicio': 1,  'q_fim': 17},
        {'caderno': 18, 'pg_inicio': 1,  'pg_fim': 20, 'q_inicio': 18, 'q_fim': 47},
        {'caderno': 19, 'pg_inicio': 1,  'pg_fim': 3,  'q_inicio': 48, 'q_fim': 50},
    ],
    2023: [
        {'caderno': 19, 'pg_inicio': 11, 'pg_fim': 20, 'q_inicio': 1,  'q_fim': 21},
        {'caderno': 20, 'pg_inicio': 1,  'pg_fim': 13, 'q_inicio': 22, 'q_fim': 50},
    ],
}

GABARITOS = {
    2014: {1:'C',2:'D',3:'B',4:'A',5:'B',6:'C',7:'C',8:'A',9:'D',10:'A',11:'C',12:'B',13:'B',14:'A',15:'D',16:'C',17:'B',18:'C',19:'A',20:'D',21:'C',22:'B',23:'D',24:'B',25:'A',26:'B',27:'C',28:'A',29:'D',30:'C',31:'D',32:'D',33:'B',34:'A',35:'A',36:'D',37:'C',38:'D',39:'A',40:'D',41:'C',42:'B',43:'B',44:'A',45:'C',46:'B',47:'C',48:'A',49:'B',50:'C',51:'B',52:'A',53:'C',54:'D',55:'C',56:'B',57:'A',58:'B',59:'D',60:'C'},
    2015: {1:'B',2:'C',3:'A',4:'D',5:'D',6:'B',7:'C',8:'A',9:'D',10:'A',11:'C',12:'B',13:'C',14:'A',15:'D',16:'B',17:'B',18:'C',19:'D',20:'A',21:'C',22:'A',23:'D',24:'B',25:'A',26:'B',27:'C',28:'C',29:'A',30:'C',31:'B',32:'A',33:'C',34:'D',35:'D',36:'A',37:'B',38:'C',39:'D',40:'B',41:'D',42:'A',43:'B',44:'B',45:'C',46:'C',47:'A',48:'C',49:'A',50:'D',51:'B',52:'D',53:'C',54:'D',55:'C',56:'B',57:'B',58:'A',59:'B',60:'A'},
    2016: {1:'D',2:'A',3:'C',4:'B',5:'A',6:'B',7:'D',8:'C',9:'B',10:'A',11:'C',12:'D',13:'D',14:'C',15:'B',16:'A',17:'C',18:'B',19:'D',20:'A',21:'C',22:'B',23:'D',24:'B',25:'A',26:'D',27:'A',28:'C',29:'B',30:'D',31:'B',32:'C',33:'D',34:'A',35:'C',36:'C',37:'D',38:'A',39:'D',40:'C',41:'C',42:'B',43:'A',44:'C',45:'D',46:'D',47:'B',48:'C',49:'ANULADA',50:'B',51:'B',52:'B',53:'D',54:'C',55:'D',56:'C',57:'B',58:'A',59:'A',60:'C'},
    2017: {1:'D',2:'C',3:'A',4:'B',5:'A',6:'D',7:'C',8:'B',9:'C',10:'A',11:'D',12:'B',13:'A',14:'B',15:'D',16:'C',17:'B',18:'A',19:'C',20:'D',21:'C',22:'A',23:'C',24:'CD',25:'B',26:'B',27:'B',28:'D',29:'A',30:'A',31:'D',32:'A',33:'A',34:'C',35:'D',36:'A',37:'D',38:'A',39:'B',40:'C',41:'C',42:'B',43:'A',44:'C',45:'B',46:'C',47:'B',48:'B',49:'D',50:'B',51:'B',52:'A',53:'C',54:'C',55:'A',56:'D',57:'D',58:'B',59:'D',60:'B'},
    2018: {1:'D',2:'D',3:'B',4:'A',5:'C',6:'A',7:'D',8:'B',9:'C',10:'A',11:'C',12:'B',13:'D',14:'A',15:'D',16:'C',17:'B',18:'C',19:'A',20:'B',21:'B',22:'C',23:'D',24:'A',25:'C',26:'A',27:'C',28:'B',29:'D',30:'B',31:'A',32:'C',33:'B',34:'C',35:'B',36:'D',37:'A',38:'C',39:'D',40:'B',41:'D',42:'A',43:'D',44:'A',45:'D',46:'C',47:'B',48:'C',49:'A',50:'B',51:'B',52:'A',53:'D',54:'C',55:'A',56:'A',57:'D',58:'B',59:'D',60:'B'},
    2019: {1:'B',2:'D',3:'C',4:'D',5:'A',6:'C',7:'A',8:'B',9:'D',10:'B',11:'C',12:'B',13:'C',14:'A',15:'C',16:'D',17:'B',18:'A',19:'D',20:'A',21:'C',22:'A',23:'D',24:'B',25:'D',26:'D',27:'B',28:'A',29:'C',30:'B',31:'D',32:'B',33:'D',34:'C',35:'A',36:'D',37:'B',38:'A',39:'C',40:'B',41:'C',42:'D',43:'A',44:'B',45:'C',46:'A',47:'B',48:'D',49:'B',50:'C',51:'B',52:'A',53:'D',54:'A',55:'A',56:'D',57:'A',58:'C',59:'C',60:'B'},
    2020: {1:'B',2:'C',3:'D',4:'A',5:'D',6:'C',7:'A',8:'D',9:'C',10:'A',11:'B',12:'C',13:'D',14:'A',15:'B',16:'C',17:'B',18:'A',19:'B',20:'D',21:'C',22:'A',23:'B',24:'D',25:'B',26:'C',27:'D',28:'A',29:'B',30:'D',31:'C',32:'C',33:'B',34:'B',35:'D',36:'D',37:'A',38:'C',39:'D',40:'A',41:'B',42:'C',43:'C',44:'B',45:'A',46:'A',47:'C',48:'C',49:'D',50:'B',51:'B',52:'A',53:'D',54:'A',55:'C',56:'B',57:'A',58:'C',59:'C',60:'D'},
    2021: {1:'D',2:'C',3:'A',4:'C',5:'B',6:'D',7:'A',8:'A',9:'D',10:'C',11:'B',12:'C',13:'D',14:'B',15:'A',16:'C',17:'B',18:'A',19:'B',20:'D',21:'C',22:'A',23:'D',24:'C',25:'B',26:'B',27:'D',28:'C',29:'A',30:'B',31:'D',32:'B',33:'B',34:'A',35:'C',36:'A',37:'C',38:'D',39:'D',40:'A',41:'B',42:'A',43:'C',44:'C',45:'D',46:'B',47:'C',48:'A',49:'B',50:'D',51:'B',52:'C',53:'D',54:'B',55:'A',56:'B',57:'C',58:'A',59:'D',60:'A'},
    2022: {1:'C',2:'B',3:'A',4:'A',5:'B',6:'D',7:'C',8:'A',9:'B',10:'D',11:'D',12:'C',13:'B',14:'A',15:'D',16:'D',17:'B',18:'C',19:'D',20:'A',21:'B',22:'C',23:'D',24:'B',25:'A',26:'B',27:'D',28:'C',29:'A',30:'A',31:'B',32:'D',33:'C',34:'D',35:'C',36:'A',37:'B',38:'D',39:'A',40:'C',41:'B',42:'C',43:'A',44:'D',45:'D',46:'A',47:'C',48:'D',49:'D',50:'B'},
    2023: {1:'C',2:'B',3:'D',4:'A',5:'A',6:'C',7:'D',8:'B',9:'B',10:'D',11:'A',12:'C',13:'A',14:'C',15:'D',16:'C',17:'B',18:'D',19:'A',20:'B',21:'A',22:'D',23:'C',24:'B',25:'A',26:'C',27:'C',28:'B',29:'A',30:'D',31:'A',32:'A',33:'B',34:'A',35:'A',36:'C',37:'B',38:'D',39:'A',40:'C',41:'C',42:'B',43:'A',44:'B',45:'D',46:'C',47:'A',48:'D',49:'C',50:'B'},
}

PROMPT = """Você está analisando uma página de prova da EMBRAER (processo seletivo).
Extraia TODAS as questões visíveis nesta página.

REGRAS:
- disciplina: use uma destas: portugues, matematica, ciencias_humanas, ciencias_naturais, ingles, redacao
- Detecte a disciplina pelo conteúdo da questão
- Inclua o enunciado COMPLETO com todos os textos de apoio
- Use aspas simples dentro dos textos, nunca aspas duplas
- Se não houver questões: {"questoes": []}

Retorne SOMENTE JSON válido:
{
  "questoes": [
    {
      "numero": 1,
      "disciplina": "matematica",
      "enunciado": "texto completo da questão",
      "alternativas": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "tem_imagem": false
    }
  ]
}"""

def pdf_para_imagens(caminho, pg_inicio, pg_fim):
    doc = fitz.open(caminho)
    imagens = []
    for i in range(pg_inicio - 1, min(pg_fim, len(doc))):
        mat = fitz.Matrix(2.0, 2.0)
        pix = doc[i].get_pixmap(matrix=mat)
        b64 = base64.b64encode(pix.tobytes("png")).decode()
        imagens.append({'pagina': i + 1, 'b64': b64})
    doc.close()
    return imagens

def limpar_json(texto):
    texto = texto.replace("```json", "").replace("```", "").strip()
    try:
        json.loads(texto)
        return texto
    except:
        match = re.search(r'\{.*\}', texto, re.DOTALL)
        if match:
            try:
                json.loads(match.group())
                return match.group()
            except:
                pass
    return '{"questoes": []}'

def extrair_questoes(img_b64):
    claude = get_claude()
    try:
        resp = claude.messages.create(
            model='claude-opus-4-5',
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                    {"type": "text", "text": PROMPT}
                ]
            }]
        )
        texto = limpar_json(resp.content[0].text.strip())
        return json.loads(texto).get("questoes", [])
    except Exception as e:
        print(f"    Erro: {e}")
        return []

def salvar_questoes(questoes, ano, gabaritos, executar):
    if not executar:
        return len(questoes)
    conn = get_conn()
    salvas = 0
    for q in questoes:
        numero = q.get("numero")
        if not numero:
            continue
        # Verifica se já existe
        existe = conn.execute(
            "SELECT id FROM questoes WHERE escola='EMBRAER' AND ano=? AND numero=?",
            (ano, numero)
        ).fetchone()
        if existe:
            continue
        gabarito = gabaritos.get(int(numero), '')
        conn.execute("""
            INSERT INTO questoes
            (id, escola, disciplina, ano, numero, fase, enunciado, alternativas, gabarito, nivel, tags, tem_imagem)
            VALUES (?, 'EMBRAER', ?, ?, ?, 1, ?, ?, ?, 'medio', ?, ?)
        """, (
            str(uuid4()),
            q.get("disciplina", ""),
            ano,
            numero,
            q.get("enunciado", ""),
            json.dumps(q.get("alternativas", []), ensure_ascii=False),
            gabarito,
            json.dumps([q.get("disciplina", "")], ensure_ascii=False),
            1 if q.get("tem_imagem") else 0
        ))
        salvas += 1
    conn.commit()
    conn.close()
    return salvas

def processar_ano(ano, executar):
    segmentos = MAPEAMENTO.get(ano)
    if not segmentos:
        print(f"Ano {ano} não mapeado.")
        return

    gabaritos = GABARITOS.get(ano, {})
    print(f"\n{'='*50}")
    print(f"EMBRAER {ano} — {len(gabaritos)} questões com gabarito")
    print(f"Modo: {'EXECUÇÃO' if executar else 'DIAGNÓSTICO'}")

    total = 0
    for seg in segmentos:
        n = seg['caderno']
        nome = 'Caderno-de-Provas embraer 1.pdf' if n == 1 else f'Caderno-de-Provas-EMBRAER {n}.pdf'
        caminho = BASE + nome
        print(f"\n  Caderno {n} | Q{seg['q_inicio']}-Q{seg['q_fim']} | pgs {seg['pg_inicio']}-{seg['pg_fim']}")

        imagens = pdf_para_imagens(caminho, seg['pg_inicio'], seg['pg_fim'])
        for img in imagens:
            print(f"    Página {img['pagina']}...", end=' ')
            questoes = extrair_questoes(img['b64'])
            # Filtra questões dentro do range do segmento
            questoes_validas = [q for q in questoes
                               if q.get('numero') and seg['q_inicio'] <= int(q['numero']) <= seg['q_fim']]
            if questoes_validas:
                salvas = salvar_questoes(questoes_validas, ano, gabaritos, executar)
                print(f"{len(questoes_validas)} questões ({salvas} salvas)")
                total += salvas
            else:
                print("0 questões")

    print(f"\n  Total {ano}: {total} questões salvas")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ano", type=int)
    parser.add_argument("--todos", action="store_true")
    parser.add_argument("--executar", action="store_true")
    args = parser.parse_args()

    init_db()

    if args.todos:
        for ano in sorted(MAPEAMENTO.keys()):
            processar_ano(ano, args.executar)
    elif args.ano:
        processar_ano(args.ano, args.executar)
    else:
        print("Use --ano 2023 ou --todos. Adicione --executar para salvar.")

if __name__ == "__main__":
    main()
# ADICIONAR ao MAPEAMENTO (cole após o 2023):
#     2024: [
#         {'caderno': '2024 1',  'pg_inicio': 5,  'pg_fim': 20, 'q_inicio': 1,  'q_fim': 35},
#         {'caderno': '2024 2',  'pg_inicio': 1,  'pg_fim': 9,  'q_inicio': 36, 'q_fim': 50},
#     ],
#     2025: [
#         {'caderno': '2025 1a', 'pg_inicio': 5,  'pg_fim': 9,  'q_inicio': 1,  'q_fim': 15},
#         {'caderno': '2025 1b', 'pg_inicio': 1,  'pg_fim': 10, 'q_inicio': 16, 'q_fim': 35},
#         {'caderno': '2025 2',  'pg_inicio': 1,  'pg_fim': 9,  'q_inicio': 36, 'q_fim': 50},
#     ],
