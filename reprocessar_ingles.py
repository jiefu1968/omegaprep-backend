"""
Reprocessa questões de inglês do ITA com Claude Vision.
Atualiza enunciados incluindo os textos-base (reading passages).
Uso: python reprocessar_ingles.py --ano 2015
     python reprocessar_ingles.py --todos
"""
import argparse
import base64
import json
import re
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import fitz
from app.llm import get_claude
from app.config import CLAUDE_MODEL
from app.db.database import get_conn, init_db

PROMPT_INGLES = """Você está analisando uma página de prova de INGLÊS do ITA.

IMPORTANTE: Provas de inglês têm TEXTOS-BASE (reading passages) seguidos de questões sobre eles.

Para cada questão encontrada, inclua no campo "enunciado":
1. O texto-base completo (se a questão depende de um texto, inclua o texto inteiro antes da pergunta)
2. A pergunta em si
3. Use o formato: [TEXTO: ...texto completo...] Pergunta: ...pergunta...

Se várias questões compartilham o mesmo texto-base, repita o texto em cada questão.
Se a questão não tem texto-base (gramática, vocabulário isolado), inclua só a pergunta.

Retorne SOMENTE JSON válido:
{
  "questoes": [
    {
      "numero": 25,
      "enunciado": "[TEXTO: The article discusses...] According to the text...",
      "alternativas": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
      "tem_imagem": false
    }
  ]
}

Use aspas simples dentro dos textos. Retorne APENAS o JSON, sem markdown."""


def pdf_para_imagens(caminho: str) -> list:
    doc = fitz.open(caminho)
    imagens = []
    for i, pagina in enumerate(doc):
        mat = fitz.Matrix(2.0, 2.0)
        pix = pagina.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        b64 = base64.b64encode(img_bytes).decode()
        imagens.append({"pagina": i + 1, "b64": b64})
    doc.close()
    return imagens


def limpar_json(texto: str) -> str:
    texto = texto.replace("```json", "").replace("```", "").strip()
    try:
        json.loads(texto)
        return texto
    except:
        pass
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    if match:
        try:
            json.loads(match.group())
            return match.group()
        except:
            pass
    return '{"questoes": []}'


def extrair_questoes(img_b64: str) -> list:
    claude = get_claude()
    try:
        resposta = claude.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=8000,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                    {"type": "text", "text": PROMPT_INGLES}
                ]
            }]
        )
        texto = limpar_json(resposta.content[0].text.strip())
        dados = json.loads(texto)
        return dados.get("questoes", [])
    except Exception as e:
        print(f"  Erro na extração: {e}")
        return []


def atualizar_enunciados(questoes: list, ano: int, fase: int) -> int:
    """Atualiza enunciados no banco — só questões com enunciado curto."""
    conn = get_conn()
    atualizadas = 0

    for q in questoes:
        numero = q.get("numero")
        enunciado = q.get("enunciado", "").strip()

        if not numero or not enunciado or len(enunciado) < 50:
            continue

        # Busca a questão no banco
        rows = conn.execute("""
            SELECT id, enunciado FROM questoes
            WHERE escola='ITA' AND disciplina='ingles'
            AND ano=? AND fase=? AND numero=?
        """, (ano, fase, numero)).fetchall()

        for row in rows:
            enunciado_atual = row['enunciado'] or ''
            # Só atualiza se o novo enunciado for mais completo
            if len(enunciado) > len(enunciado_atual):
                conn.execute(
                    "UPDATE questoes SET enunciado=? WHERE id=?",
                    (enunciado, row['id'])
                )
                atualizadas += 1
                print(f"    Q{numero}: {len(enunciado_atual)}→{len(enunciado)} chars")

    conn.commit()
    conn.close()
    return atualizadas


def processar_ano(ano: int):
    base = Path('/Users/jefersonchagas/Desktop/ITA VESTIBULAR 2008-2025')

    # Detecta arquivo de inglês
    pasta = base / f"ITA {ano}"
    if not pasta.exists():
        print(f"{ano}: pasta não encontrada")
        return

    # Anos com arquivo separado de inglês
    arquivo_ingles = pasta / f"ingles_{ano}.pdf"
    # Anos com arquivo unificado de fase 1
    arquivo_fase1 = pasta / f"{ano}_fase1.pdf"

    if arquivo_ingles.exists():
        caminho = str(arquivo_ingles)
        print(f"\n{ano}: usando {arquivo_ingles.name}")
    elif arquivo_fase1.exists():
        caminho = str(arquivo_fase1)
        print(f"\n{ano}: usando {arquivo_fase1.name} (fase1 unificada)")
    else:
        print(f"\n{ano}: nenhum arquivo encontrado")
        return

    imagens = pdf_para_imagens(caminho)
    print(f"  {len(imagens)} páginas")

    total = 0
    for img in imagens:
        print(f"  Página {img['pagina']}...")
        questoes = extrair_questoes(img["b64"])
        questoes_ingles = [q for q in questoes if str(q.get("numero", "")).isdigit()]
        if questoes_ingles:
            n = atualizar_enunciados(questoes_ingles, ano, 1)
            print(f"    {n} enunciados atualizados")
            total += n

    print(f"  Total {ano}: {total} atualizados")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ano", type=int)
    parser.add_argument("--todos", action="store_true")
    args = parser.parse_args()

    init_db()

    if args.todos:
        for ano in range(2008, 2026):
            processar_ano(ano)
    elif args.ano:
        processar_ano(args.ano)
    else:
        print("Use --ano 2015 ou --todos")


if __name__ == "__main__":
    main()
