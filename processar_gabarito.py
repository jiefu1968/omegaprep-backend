"""
Extrai gabaritos dos PDFs do ITA usando texto puro (sem Claude Vision).
"""
import re
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import fitz
from app.db.database import get_conn, init_db

def extrair_texto_pdf(caminho: str) -> str:
    doc = fitz.open(caminho)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text() + "\n"
    doc.close()
    return texto

def parsear_gabarito(texto: str) -> dict:
    """
    Extrai pares numero→resposta do texto do gabarito.
    Formato típico ITA:
    12
    D
    24
    C
    """
    gabarito = {}
    linhas = [l.strip() for l in texto.split('\n') if l.strip()]
    
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        
        # Verifica se é um número de questão
        if re.match(r'^\d+$', linha):
            numero = int(linha)
            # Próxima linha deve ser a resposta
            if i + 1 < len(linhas):
                prox = linhas[i+1].strip().upper()
                if prox in ['A', 'B', 'C', 'D', 'E']:
                    gabarito[numero] = prox
                    i += 2
                    continue
        
        # Formato alternativo: "01 A" ou "1. A" na mesma linha
        match = re.match(r'^(\d+)[\.\s\)]+([ABCDE])\b', linha)
        if match:
            numero = int(match.group(1))
            resposta = match.group(2)
            gabarito[numero] = resposta
        
        # Formato: "1-A" ou "1:A"
        match2 = re.match(r'^(\d+)[-:]\s*([ABCDE])\b', linha)
        if match2:
            numero = int(match2.group(1))
            resposta = match2.group(2)
            gabarito[numero] = resposta
        
        i += 1
    
    return gabarito

def detectar_disciplinas_por_numero(ano: int) -> dict:
    """
    Mapeia número da questão para disciplina baseado no padrão ITA.
    ITA 1ª fase: questões numeradas sequencialmente por disciplina.
    """
    # Padrão geral ITA fase 1 (pode variar por ano)
    # Tipicamente: 1-30 física, 31-60 química, etc.
    # Como varia muito, deixamos como 'geral' e buscamos por número
    return {}

def atualizar_gabaritos_banco(gabarito: dict, escola: str, ano: int) -> int:
    """Atualiza gabaritos no banco buscando por número da questão."""
    conn = get_conn()
    atualizadas = 0
    
    for numero, resposta in gabarito.items():
        try:
            # Atualiza todas as questões com este número neste ano
            # (independente de disciplina pois o gabarito é unificado)
            result = conn.execute("""
                UPDATE questoes SET gabarito = ?
                WHERE escola = ? AND ano = ? AND numero = ?
            """, (resposta, escola, ano, numero))
            atualizadas += result.rowcount
        except Exception as e:
            print(f"  Erro Q{numero}: {e}")
    
    conn.commit()
    conn.close()
    return atualizadas

def processar_todos_gabaritos():
    base = Path("/Users/jefersonchagas/Desktop/ITA VESTIBULAR 2008-2025")
    init_db()
    
    total_geral = 0
    
    for ano in range(2008, 2026):
        pasta = base / f"ITA {ano}"
        if not pasta.exists():
            continue
        
        # Procura arquivo de gabarito
        gabaritos = (
            list(pasta.glob("gabarito*.pdf")) +
            list(pasta.glob("*gabarito*.pdf")) +
            list(pasta.glob("Gabarito*.pdf"))
        )
        
        if not gabaritos:
            print(f"ITA {ano}: sem gabarito")
            continue
        
        for gab in sorted(gabaritos):
            print(f"\nITA {ano}: {gab.name}")
            
            texto = extrair_texto_pdf(str(gab))
            gabarito = parsear_gabarito(texto)
            
            if not gabarito:
                print(f"  ⚠️ Nenhum gabarito extraído — verifique o formato")
                # Mostra amostra do texto para diagnóstico
                print(f"  Amostra: {texto[:200]}")
                continue
            
            print(f"  {len(gabarito)} respostas encontradas")
            print(f"  Amostra: {dict(list(gabarito.items())[:5])}")
            
            atualizadas = atualizar_gabaritos_banco(gabarito, "ITA", ano)
            print(f"  ✅ {atualizadas} questões atualizadas")
            total_geral += atualizadas
    
    print(f"\n{'='*40}")
    print(f"Total geral: {total_geral} questões com gabarito")

if __name__ == "__main__":
    processar_todos_gabaritos()
