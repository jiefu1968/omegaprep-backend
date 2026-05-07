"""
Processa TODAS as provas do ITA automaticamente.
"""
import os
import subprocess
from pathlib import Path

BASE = Path("/Users/jefersonchagas/Desktop/ITA VESTIBULAR 2008-2025")
DEST = Path("/Users/jefersonchagas/MeusProjetos/omegaprep-backend/static/provas/ita")

# Mapeamento de nomes de arquivo para disciplina
def detectar_disciplina(nome: str) -> str:
    n = nome.lower()
    if "fisica" in n or "física" in n:       return "fisica"
    if "matematica" in n or "matemática" in n: return "matematica"
    if "quimica" in n or "química" in n:     return "quimica"
    if "portugues" in n or "português" in n: return "portugues"
    if "ingles" in n or "inglês" in n:       return "ingles"
    if "redacao" in n or "redação" in n:     return "redacao"
    if "fase1" in n or "fase_1" in n:        return "multiplas"
    return None

def detectar_fase(nome: str) -> int:
    if "2f" in nome or "fase2" in nome or "fase_2" in nome:
        return 2
    return 1

def processar_ano(ano: int):
    pasta = BASE / f"ITA {ano}"
    if not pasta.exists():
        print(f"Pasta não encontrada: {pasta}")
        return

    print(f"\n{'='*50}")
    print(f"Processando ITA {ano}")
    print(f"{'='*50}")

    # Cria pasta de destino
    dest_ano = DEST / str(ano)
    dest_ano.mkdir(parents=True, exist_ok=True)

    # Lista PDFs ignorando gabarito
    pdfs = [f for f in pasta.glob("*.pdf")
            if "gabarito" not in f.name.lower()
            and "resolucao" not in f.name.lower()
            and "resolução" not in f.name.lower()]

    if not pdfs:
        print(f"  Nenhum PDF encontrado em {pasta}")
        return

    for pdf in sorted(pdfs):
        disciplina = detectar_disciplina(pdf.stem)
        fase = detectar_fase(pdf.stem)

        if disciplina is None:
            print(f"  Pulando {pdf.name} — disciplina não identificada")
            continue

        # Copia para pasta do projeto
        dest = dest_ano / pdf.name
        if not dest.exists():
            import shutil
            shutil.copy2(pdf, dest)

        print(f"\n  Arquivo: {pdf.name}")
        print(f"  Disciplina: {disciplina} | Fase: {fase}")

        # Executa o processador
        cmd = [
            "python", "processar_prova.py",
            "--arquivo", str(dest),
            "--escola", "ITA",
            "--ano", str(ano),
            "--disciplina", disciplina,
            "--fase", str(fase)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Mostra apenas o resumo
        for line in result.stdout.split('\n'):
            if 'Total' in line or 'Erro' in line or 'questões' in line.lower():
                print(f"  {line}")
        
        if result.returncode != 0:
            print(f"  ERRO: {result.stderr[-200:]}")

if __name__ == "__main__":
    import sys
    
    # Anos para processar
    if len(sys.argv) > 1:
        anos = [int(a) for a in sys.argv[1:]]
    else:
        anos = list(range(2008, 2026))

    print("OmegaPrep — Processador de Provas ITA")
    print(f"Anos: {anos[0]} a {anos[-1]}")
    print(f"Total: {len(anos)} anos\n")

    total_geral = 0
    for ano in anos:
        processar_ano(ano)

    print(f"\n{'='*50}")
    print("Processamento concluído!")
    print(f"{'='*50}")
