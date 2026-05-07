from app.db.database import get_conn, init_db
import json, uuid
init_db()

TEXTO = '''[TEXTO: A picture of Brighton beach in 1976, featured in the Guardian a few weeks ago, appeared to show an alien race. Almost everyone was slim. I mentioned it on social media, then went on holiday. When I returned, I found that people were still debating it. The heated discussion prompted me to read more. How have we grown so fat, so fast? To my astonishment, almost every explanation proposed in the thread turned out to be untrue. The obvious explanation, many on social media insisted, is that we're eating more. So here's the first big surprise: we ate more in 1976. According to government figures, we currently consume an average of 2,130 kilocalories a day, a figure that appears to include sweets and alcohol. But in 1976, we consumed 2,280 kcal excluding alcohol and sweets, or 2,590 kcal when they're included. I have found no reason to disbelieve the figures. So what has happened? The light begins to dawn when you look at the nutrition figures in more detail. Yes, we ate more in 1976, but differently. Today, we buy half as much fresh milk per person, but five times more yoghurt, three times more ice cream and 39 times as many dairy desserts. We buy half as many eggs as in 1976, but a third more breakfast cereals and twice the cereal snacks; half the total potatoes, but three times the crisps. While our direct purchases of sugar have sharply declined, the sugar we consume in drinks and confectionery is likely to have rocketed. In other words, the opportunities to load our food with sugar have boomed. As some experts have long proposed, this seems to be the issue. The shift has not happened by accident. As Jacques Peretti argued in his film The Men Who Made Us Fat, food companies have invested heavily in designing products that use sugar to bypass our natural appetite control mechanisms, and in packaging and promoting these products to break down what remains of our defenses, including through the use of subliminal scents. They employ an army of food scientists and psychologists to trick us into eating more than we need, while their advertisers use the latest findings in neuroscience to overcome our resistance. They hire biddable scientists and thinktanks to confuse us about the causes of obesity. Above all, just as the tobacco companies did with smoking, they promote the idea that weight is a question of personal responsibility. After spending billions on overriding our willpower, they blame us for failing to exercise it. To judge by the debate the 1976 photograph triggered, it works. There are no excuses. Take responsibility for your own lives, people! No one force feeds you junk food, it's personal choice. We're not lemmings. More alarmingly, according to a paper in the Lancet, more than 90% of policymakers believe that personal motivation is a strong or very strong influence on the rise of obesity. Such people propose no mechanism by which the 61% of English people who are overweight or obese have lost their willpower. But this improbable explanation seems immune to evidence. Perhaps this is because obesophobia is often a fatly-disguised form of snobbery. In most rich nations, obesity rates are much higher at the bottom of the socioeconomic scale. They correlate strongly with inequality, which helps to explain why the UK's incidence is greater than in most European and OECD nations. The scientific literature shows how the lower spending power, stress, anxiety and depression associated with low social status makes people more vulnerable to bad diets. Just as jobless people are blamed for structural unemployment, and indebted people are blamed for impossible housing costs, fat people are blamed for a societal problem. But yes, willpower needs to be exercised - by governments. Yes, we need personal responsibility - on the part of policymakers. And yes, control needs to be exerted - over those who have discovered our weaknesses and ruthlessly exploit them. Adaptado de: The Guardian, ago. 2018.]'''

QUESTOES = {
    25: (TEXTO, 'De acordo com o texto, em comparação com 1976, atualmente nós compramos'),
    26: ('', 'De acordo com o texto, é correto afirmar que'),
    27: ('', 'De acordo com o texto,'),
    28: ('', 'De acordo com o texto, é correto afirmar que o autor sustenta que'),
    29: ('', 'Assinale a alternativa que pode substituir as na sentença As Jacques Peretti argued in his film The Men Who Made Us Fat, food companies have invested heavily in designing products [...] mantendo o mesmo sentido do texto e a correção gramatical.'),
}

conn = get_conn()
total = 0
for numero, (texto, enunciado) in QUESTOES.items():
    enunciado_final = texto + ' ' + enunciado if texto else enunciado
    rows = conn.execute('''
        SELECT id FROM questoes
        WHERE escola='ITA' AND ano=2019 AND fase='1'
        AND disciplina='ingles' AND numero=?
    ''', (numero,)).fetchall()
    if rows:
        for row in rows:
            conn.execute('UPDATE questoes SET enunciado=? WHERE id=?', (enunciado_final, row['id']))
            total += 1
            print(f'Q{numero}: atualizado')
    else:
        conn.execute('''
            INSERT INTO questoes (id,escola,disciplina,ano,numero,fase,enunciado,alternativas,gabarito,nivel,tags,tem_imagem)
            VALUES (?,'ITA','ingles',2019,?,'1',?,'[]','','dificil','["ingles"]',0)
        ''', (str(uuid.uuid4()), numero, enunciado_final))
        total += 1
        print(f'Q{numero}: inserido')

conn.commit()
conn.close()
print(f'\nTotal: {total} processadas')
