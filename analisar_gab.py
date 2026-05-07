import fitz

doc = fitz.open('/Users/jefersonchagas/Desktop/ITA VESTIBULAR 2008-2025/ITA 2019/gabarito_2019.pdf')
page = doc[0]
words = page.get_text("words")
print("CABECALHOS (y < 300):")
for w in words:
    x0, y0, x1, y1, text, *_ = w
    if y0 < 300:
        print(f"  x={x0:.0f} y={y0:.0f}  '{text}'")
print("\nPRIMEIRAS 40 ENTRADAS:")
count = 0
for w in words:
    x0, y0, x1, y1, text, *_ = w
    if y0 >= 300:
        print(f"  x={x0:.0f} y={y0:.0f}  '{text}'")
        count += 1
        if count >= 40:
            break
