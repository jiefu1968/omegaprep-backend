import json
from uuid import uuid4
from app.db.database import get_conn, init_db

def seed():
    init_db()
    conn = get_conn()

    questoes = [
        {
            "id": str(uuid4()),
            "escola": "ITA",
            "disciplina": "matematica",
            "ano": 2023,
            "numero": 1,
            "fase": 1,
            "enunciado": "Se log2(x) + log2(x-6) = 4, então x é igual a:",
            "alternativas": json.dumps(["A) 2","B) 4","C) 8","D) 10","E) 16"]),
            "gabarito": "C",
            "nivel": "medio",
            "tags": json.dumps(["logaritmo","equacao"]),
            "tem_imagem": 0
        },
        {
            "id": str(uuid4()),
            "escola": "ITA",
            "disciplina": "fisica",
            "ano": 2023,
            "numero": 1,
            "fase": 1,
            "enunciado": "Um corpo de massa 2kg é lançado verticalmente com velocidade inicial de 10m/s. Considerando g=10m/s², a altura máxima atingida é:",
            "alternativas": json.dumps(["A) 2,5m","B) 5m","C) 10m","D) 20m","E) 25m"]),
            "gabarito": "B",
            "nivel": "facil",
            "tags": json.dumps(["cinematica","lancamento vertical"]),
            "tem_imagem": 0
        },
        {
            "id": str(uuid4()),
            "escola": "FUVEST",
            "disciplina": "quimica",
            "ano": 2023,
            "numero": 1,
            "fase": 1,
            "enunciado": "O pH de uma solução aquosa de HCl 0,01 mol/L a 25°C é:",
            "alternativas": json.dumps(["A) 1","B) 2","C) 7","D) 12","E) 14"]),
            "gabarito": "B",
            "nivel": "facil",
            "tags": json.dumps(["pH","acido","solucao"]),
            "tem_imagem": 0
        },
        {
            "id": str(uuid4()),
            "escola": "ENEM",
            "disciplina": "biologia",
            "ano": 2023,
            "numero": 1,
            "fase": 1,
            "enunciado": "Na mitose, a divisão celular resulta em células-filhas com:",
            "alternativas": json.dumps(["A) Metade dos cromossomos","B) O dobro dos cromossomos","C) Mesmo número de cromossomos","D) Cromossomos recombinados","E) Nenhuma das anteriores"]),
            "gabarito": "C",
            "nivel": "facil",
            "tags": json.dumps(["mitose","divisao celular","citologia"]),
            "tem_imagem": 0
        },
        {
            "id": str(uuid4()),
            "escola": "IME",
            "disciplina": "matematica",
            "ano": 2022,
            "numero": 1,
            "fase": 1,
            "enunciado": "Quantos números inteiros positivos menores que 1000 são divisíveis por 3 ou por 5?",
            "alternativas": json.dumps(["A) 466","B) 467","C) 533","D) 534","E) 600"]),
            "gabarito": "C",
            "nivel": "medio",
            "tags": json.dumps(["combinatoria","divisibilidade","principio inclusao exclusao"]),
            "tem_imagem": 0
        },
    ]

    resolucoes = [
        {
            "questao_id": questoes[0]["id"],
            "passos": json.dumps([
                "Usar propriedade: log2(x) + log2(x-6) = log2(x·(x-6))",
                "Igualar a 4: log2(x(x-6)) = 4",
                "Converter: x(x-6) = 2⁴ = 16",
                "Expandir: x² - 6x - 16 = 0",
                "Fatorar: (x-8)(x+2) = 0",
                "x = 8 ou x = -2. Como x > 6, x = 8"
            ]),
            "conceito_chave": "Propriedade de soma de logaritmos",
            "dicas": "Sempre verifique o domínio: x > 0 e x-6 > 0, portanto x > 6",
            "erros_comuns": "Esquecer de verificar o domínio e aceitar x = -2 como resposta",
            "metodo_alternativo": "Substituir cada alternativa na equação original"
        },
        {
            "questao_id": questoes[1]["id"],
            "passos": json.dumps([
                "Na altura máxima, velocidade final = 0",
                "Usar v² = v0² - 2gh",
                "0 = 10² - 2 × 10 × h",
                "0 = 100 - 20h",
                "20h = 100",
                "h = 5m"
            ]),
            "conceito_chave": "Equação de Torricelli para lançamento vertical",
            "dicas": "Na altura máxima a velocidade sempre é zero",
            "erros_comuns": "Usar g positivo em vez de negativo, ou esquecer que v=0 no topo",
            "metodo_alternativo": "Usar energia cinética = energia potencial: mv²/2 = mgh"
        },
    ]

    for q in questoes:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO questoes
                (id,escola,disciplina,ano,numero,fase,enunciado,alternativas,gabarito,nivel,tags,tem_imagem)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (q["id"],q["escola"],q["disciplina"],q["ano"],q["numero"],
                  q["fase"],q["enunciado"],q["alternativas"],q["gabarito"],
                  q["nivel"],q["tags"],q["tem_imagem"]))
        except Exception as e:
            print(f"Erro questão: {e}")

    for r in resolucoes:
        try:
            rid = str(uuid4())
            conn.execute("""
                INSERT OR IGNORE INTO resolucoes
                (id,questao_id,passos,conceito_chave,dicas,erros_comuns,metodo_alternativo)
                VALUES (?,?,?,?,?,?,?)
            """, (rid,r["questao_id"],r["passos"],r["conceito_chave"],
                  r["dicas"],r["erros_comuns"],r["metodo_alternativo"]))
        except Exception as e:
            print(f"Erro resolução: {e}")

    conn.commit()
    conn.close()
    print(f"✅ {len(questoes)} questões inseridas!")
    print(f"✅ {len(resolucoes)} resoluções inseridas!")

if __name__ == "__main__":
    seed()
