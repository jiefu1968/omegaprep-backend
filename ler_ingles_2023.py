import fitz
doc = fitz.open('/Users/jefersonchagas/Desktop/ITA VESTIBULAR 2008-2025/ITA 2023/2023_fase1.pdf')
for i, p in enumerate(doc):
    texto = p.get_text()
    if 'Modern Art' in texto or 'disrupt' in texto or 'aristocr' in texto or 'INGLÊS' in texto:
        print(f'\n=== PAGINA {i+1} ===')
        print(texto)
