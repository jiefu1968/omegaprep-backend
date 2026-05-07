"""
Processa provas EMBRAER 2024 e 2025 com Claude Vision.
Uso: python processar_embraer_2024_2025.py --ano 2024 --executar
"""
import argparse, base64, json, re
from pathlib import Path
from uuid import uuid4
import fitz
from dotenv import load_dotenv
load_dotenv()
from app.llm import get_claude
from app.db.database import get_conn, init_db

BASE = '/Users/jefersonchagas/Desktop/omegaprep vestibulares/VESTIBULARES /EMBRAER/'

MAPEAMENTO = {
    2024: [
        {'arquivo': 'EMBRAER 2024 1.pdf',  'pg_inicio': 5,  'pg_fim': 20, 'q_inicio': 1,  'q_fim': 35},
        {'arquivo': 'EMBRAER 2024 2.pdf',  'pg_inicio': 1,  'pg_fim': 9,  'q_inicio': 36, 'q_fim': 50},
    ],
    2025: [
        {'arquivo': 'EMBRAER 2025  1a.pdf', 'pg_inicio': 5,  'pg_fim': 9,  'q_inicio': 1,  'q_fim': 15},
        {'arquivo': 'EMBRAER 2025  1b.pdf', 'pg_inicio': 1,  'pg_fim': 10, 'q_inicio': 16, 'q_fim': 35},
        {'arquivo': 'EMBRAER 2025 2.pdf',   'pg_inicio': 1,  'pg_fim': 9,  'q_inicio': 36, 'q_fim': 50},
    ],
}

GABARITOS = {
    2024: {26:'A',27:'B',28:'D',29:'B',30:'B',31:'C',32:'D',33:'C',34:'C',35:'A',36:'D',37:'A',38:'A',39:'B',40:'D'},
    2025: {26:'C',27:'C',28:'B',29:'D',30:'B',31:'B',32:'D',33:'A',34:'B',35:'D',36:'C',37:'B',38:'A',39:'B',40:'D'},
}

PROMPT = """Você está analisando uma página de prova da EMBRAER (processo seletivo).
Extraia TODAS as questões visíveis nesta página.

REGRAS:
- disciplina: portugues, matematica, ciencias_humanas, ciencias_naturais, ingles, redacao
- Detecte a disciplina pelo conteúdo
- Inclua enunciado COMPLETO com textos de apoio
- Use aspas simples dentro dos textos
- Se não houver questões: {"questoes": []}

Retorne SOMENTE JSON válido:
{
  "questoes": [
    {
      "numero": 1,
      "disciplina": "matematica",
      "enunciado": "texto completo",
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
    print(f"EMBRAER {ano} | gabaritos parciais: {len(gabaritos)}q")
    print(f"Modo: {'EXECUÇÃO' if executar else 'DIAGNÓSTICO'}")

    total = 0
    for seg in segmentos:
        caminho = BASE + seg['arquivo']
        print(f"\n  {seg['arquivo']} | Q{seg['q_inicio']}-Q{seg['q_fim']} | pgs {seg['pg_inicio']}-{seg['pg_fim']}")
        imagens = pdf_para_imagens(caminho, seg['pg_inicio'], seg['pg_fim'])
        for img in imagens:
            print(f"    Página {img['pagina']}...", end=' ')
            questoes = extrair_questoes(img['b64'])
            validas = [q for q in questoes
                      if q.get('numero') and seg['q_inicio'] <= int(q['numero']) <= seg['q_fim']]
            if validas:
                salvas = salvar_questoes(validas, ano, gabaritos, executar)
                print(f"{len(validas)} questões ({salvas} salvas)")
                total += salvas
            else:
                print("0 questões")

    print(f"\n  Total {ano}: {total} questões salvas")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ano", type=int, choices=[2024, 2025])
    parser.add_argument("--todos", action="store_true")
    parser.add_argument("--executar", action="store_true")
    args = parser.parse_args()
    init_db()
    if args.todos:
        for ano in [2024, 2025]:
            processar_ano(ano, args.executar)
    elif args.ano:
        processar_ano(args.ano, args.executar)
    else:
        print("Use --ano 2024 ou --todos. Adicione --executar para salvar.")

if __name__ == "__main__":
    main()
