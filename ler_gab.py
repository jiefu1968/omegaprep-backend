import fitz
doc = fitz.open('/Users/jefersonchagas/Desktop/ITA VESTIBULAR 2008-2025/ITA 2017/gabarito_2017.pdf')
for i, p in enumerate(doc):
    print(f"--- pagina {i+1} ---")
    print(p.get_text())
