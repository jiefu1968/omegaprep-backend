import fitz

BASE = '/Users/jefersonchagas/Desktop/omegaprep vestibulares/VESTIBULARES /EMBRAER/'

for nome in ['EMBRAER 2024 1.pdf', 'EMBRAER 2024 2.pdf', 'EMBRAER 2025  1a.pdf', 'EMBRAER 2025  1b.pdf', 'EMBRAER 2025 2.pdf']:
    doc = fitz.open(BASE + nome)
    print(f"\n=== {nome} === {len(doc)} páginas")
    for i in range(min(3, len(doc))):
        texto = doc[i].get_text()[:200]
        if texto.strip():
            print(f"  pg{i+1}: {texto[:100]}")
    doc.close()
