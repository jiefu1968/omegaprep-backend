"""
Script para processar PDFs de provas do ITA e inserir no banco.
"""
import argparse
import base64
import json
import re
import sys
from pathlib import Path
from uuid import uuid4

import fitz
from dotenv import load_dotenv

load_dotenv()

from app.llm import get_claude
from app.config import CLAUDE_MODEL
from app.db.database import get_conn, init_db

PROMPT_EXTRAIR = """Você está analisando uma página de prova do ITA.

Extraia TODAS as questões visíveis nesta página.

Retorne SOMENTE um JSON válido neste formato:
{
  "questoes": [
    {
      "numero": 1,
      "disciplina": "fisica",
      "enunciado": "texto completo do enunciado sem aspas duplas internas",
      "alternativas": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
      "tem_imagem": false,
      "nivel": "dificil"
    }
  ]
}

REGRAS CRÍTICAS:
- disciplina: matematica, fisica, quimica, portugues, ingles, redacao
- nivel: facil, medio ou dificil
- NO enunciado: use aspas simples em vez de aspas duplas
- NO enunciado: substitua aspas duplas " por '
- Se não houver questões: {"questoes": []}
- Retorne APENAS o JSON puro, sem markdown, sem ```json, sem texto
"""

def limpar_json(texto: str) -> str:
    """Tenta limpar e corrigir JSON malformado."""
    # Remove markdown
    texto = texto.replace("```json", "").replace("```", "").strip()
    
    # Tenta parsear direto
    try:
        json.loads(texto)
        return texto
    except:
        pass
    
    # Tenta extrair apenas o bloco JSON
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    if match:
        try:
            candidato = match.group()
            json.loads(candidato)
            return candidato
        except:
            pass
    
    # Tenta corrigir aspas duplas dentro de strings
    try:
        # Encontra o array de questoes e tenta reconstruir
        inicio = texto.find('"questoes"')
        if inicio > 0:
            # Pega só até o fechamento do último objeto completo
            partes = texto[:inicio-1] + '"questoes": []}'
            json.loads(partes)
            return partes
    except:
        pass
    
    return '{"questoes": []}'

def pdf_para_imagens(caminho_pdf: str) -> list:
    """Converte cada página do PDF em imagem base64."""
    doc = fitz.open(caminho_pdf)
    imagens = []
    for i, pagina in enumerate(doc):
        mat = fitz.Matrix(2.0, 2.0)
        pix = pagina.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        img_b64 = base64.standard_b64encode(img_bytes).decode()
        imagens.append({"pagina": i + 1, "b64": img_b64})
        print(f"  Página {i+1}/{len(doc)} convertida")
    doc.close()
    return imagens

def extrair_questoes_da_pagina(img_b64: str, escola: str, ano: int,
                                disciplina: str, fase: int) -> list:
    """Envia imagem para Claude Vision e extrai questões."""
    claude = get_claude()

    prompt = PROMPT_EXTRAIR
    if disciplina == "multiplas":
        prompt += f"\nEste arquivo contém múltiplas disciplinas. Identifique a disciplina de cada questão."
    else:
        prompt += f"\nEsta é uma prova de {disciplina} do {escola} {ano}, fase {fase}."

    try:
        resposta = claude.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_b64
                        }
                    },
                    {"type": "text", "text": prompt}
                ]
            }]
        )

        texto = resposta.content[0].text.strip()
        texto_limpo = limpar_json(texto)
        dados = json.loads(texto_limpo)
        questoes = dados.get("questoes", [])
        
        if questoes:
            print(f"  {len(questoes)} questões encontradas")
        
        return questoes

    except json.JSONDecodeError as e:
        print(f"  Erro JSON (página pulada): {e}")
        # Tenta uma segunda vez com prompt mais simples
        return retentar_extracao(img_b64, escola, ano, disciplina, fase)
    except Exception as e:
        print(f"  Erro Claude Vision: {e}")
        return []

def retentar_extracao(img_b64: str, escola: str, ano: int,
                       disciplina: str, fase: int) -> list:
    """Segunda tentativa com prompt mais simples."""
    claude = get_claude()
    print(f"  Tentando novamente...")
    
    prompt_simples = f"""Analise esta página de prova de {disciplina} do {escola} {ano}.

Liste cada questão encontrada. Para cada uma retorne JSON:
{{"questoes": [{{"numero": N, "disciplina": "{disciplina}", "enunciado": "texto aqui usando aspas simples", "alternativas": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."], "tem_imagem": false, "nivel": "medio"}}]}}

Use apenas aspas simples dentro dos textos. Retorne só o JSON."""

    try:
        resposta = claude.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                    {"type": "text", "text": prompt_simples}
                ]
            }]
        )
        texto = limpar_json(resposta.content[0].text.strip())
        dados = json.loads(texto)
        questoes = dados.get("questoes", [])
        if questoes:
            print(f"  Segunda tentativa: {len(questoes)} questões encontradas")
        return questoes
    except Exception as e:
        print(f"  Segunda tentativa falhou: {e}")
        return []

def salvar_questoes(questoes: list, escola: str, ano: int, fase: int) -> int:
    """Salva questões no banco de dados."""
    conn = get_conn()
    salvas = 0

    for q in questoes:
        try:
            qid = str(uuid4())
            conn.execute("""
                INSERT OR IGNORE INTO questoes
                (id, escola, disciplina, ano, numero, fase, enunciado,
                 alternativas, gabarito, nivel, tags, tem_imagem)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                qid,
                escola,
                q.get("disciplina", "matematica"),
                ano,
                q.get("numero", 0),
                fase,
                q.get("enunciado", ""),
                json.dumps(q.get("alternativas", []), ensure_ascii=False),
                "",
                q.get("nivel", "medio"),
                json.dumps([q.get("disciplina", "")], ensure_ascii=False),
                1 if q.get("tem_imagem") else 0
            ))
            salvas += 1
        except Exception as e:
            print(f"  Erro ao salvar questão {q.get('numero')}: {e}")

    conn.commit()
    conn.close()
    return salvas

def processar_arquivo(caminho: str, escola: str, ano: int,
                       disciplina: str, fase: int):
    """Processa um arquivo PDF completo."""
    print(f"\nProcessando: {Path(caminho).name}")
    print(f"Escola: {escola} | Ano: {ano} | Disciplina: {disciplina} | Fase: {fase}")

    if not Path(caminho).exists():
        print(f"Arquivo não encontrado: {caminho}")
        return 0

    print("Convertendo PDF em imagens...")
    imagens = pdf_para_imagens(caminho)
    print(f"{len(imagens)} páginas convertidas\n")

    total = 0
    for img in imagens:
        print(f"Analisando página {img['pagina']}...")
        questoes = extrair_questoes_da_pagina(
            img["b64"], escola, ano, disciplina, fase
        )
        if questoes:
            salvas = salvar_questoes(questoes, escola, ano, fase)
            print(f"  {salvas} questões salvas")
            total += salvas

    print(f"\nTotal: {total} questões inseridas no banco!")
    return total

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arquivo",    required=True)
    parser.add_argument("--escola",     default="ITA")
    parser.add_argument("--ano",        required=True, type=int)
    parser.add_argument("--disciplina", required=True)
    parser.add_argument("--fase",       default=1, type=int)
    args = parser.parse_args()

    init_db()
    processar_arquivo(
        caminho=args.arquivo,
        escola=args.escola,
        ano=args.ano,
        disciplina=args.disciplina,
        fase=args.fase
    )
