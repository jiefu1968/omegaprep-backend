from app.db.database import get_conn, init_db
import json, uuid
init_db()

TEXTO33 = '''[TEXTO: If there is any doubt about the persistent power of literature in the face of digital culture, it should be banished by the recent climb of George Orwell's 1984 up the Amazon Movers and Shakers list. There is much that's resonant for us in Orwell's dystopia in the face of Edward Snowden's revelations about the NSA. We look to 1984 as a clear cautionary tale, even a prophecy, of systematic abuse of power taken to the end of the line. However, after THE END of his dystopian novel 1984, George Orwell includes another chapter, an appendix, called The Principles of Newspeak. Since it has the trappings of a tedious scholarly treatise, readers often skip the appendix. But it changes our whole understanding of the novel. Written from some unspecified point in the future, it suggests that Big Brother was eventually defeated. The victory is attributed not to individual rebels or to The Brotherhood, an anonymous resistance group, but rather to language itself. The appendix details Oceania's attempt to replace Oldspeak, or English, with Newspeak, a linguistic shorthand that reduces the world of ideas to a set of simple, stark words. The whole aim of Newspeak is to narrow the range of thought. It will render dissent literally impossible, because there will be no words in which to express it. Fonte: FROST, Laura. Qz.com, 2019.]'''

TEXTO36 = '''[TEXTO: Of course they're fake videos, everyone can see they're not real. All the same, they really did say those things, didn't they? These are the words of Vivienne Rook, the fictional politician played by Emma Thompson in the brilliant dystopian BBC TV drama Years and Years. The episode in question, set in 2027, tackles the subject of deepfakes - videos in which a living person's face and voice are digitally manipulated to say anything the programmer wants. Rook perfectly sums up the problem with these videos - even if you know they are fake, they leave a lingering impression. And her words are all the more compelling because deepfakes are real and among us already. Last year, several deepfake porn videos emerged online, appearing to show celebrities such as Emma Watson, Gal Gadot and Taylor Swift in explicit situations. In some cases, the deepfakes are almost indistinguishable from the real thing - which is particularly worrying for politicians and other people in the public eye. Videos that may initially have been created for laughs could easily be misinterpreted by viewers. Earlier this year, for example, a digitally altered video appeared to show Nancy Pelosi, the speaker of the US House of Representatives, slurring drunkenly through a speech. The video was widely shared on Facebook and YouTube, before being tweeted by President Donald Trump with the caption: PELOSI STAMMERS THROUGH NEWS CONFERENCE. The video was debunked, but not before it had been viewed millions of times. Trump has still not deleted the tweet, which has been retweeted over 30,000 times. The current approach of social media companies is to filter out and reduce the distribution of deepfake videos, rather than outright removing them - unless they are pornographic. This can result in victims suffering severe reputational damage, not to mention ongoing humiliation and ridicule from viewers. Deepfakes are one of the most alarming trends I have witnessed as a Congresswoman to date, said US Congresswoman Yvette Clarke. If the American public can be made to believe and trust altered videos of presidential candidates, our democracy is in grave danger. We need to work together to stop deepfakes from becoming the defining feature of the 2020 elections. Of course, it's not just democracy that is at risk, but also the economy, the legal system and even individuals themselves. Clarke warns that, if deepfake technology continues to evolve without a check, video evidence could lose its credibility during trials. It is not hard to imagine it being used by disgruntled ex-lovers, employees and random people on the internet to exact revenge and ruin people's reputations. The software for creating these videos is already widely available. Fonte: CURTIS, Sophie. Mirror.co.uk, 2019.]'''

TEXTO39 = '''[TEXTO: About seven years ago, three researchers at the University of Toronto built a system that could analyze thousands of photos and teach itself to recognize everyday objects, like dogs, cars and flowers. The system was so effective that Google bought the tiny start-up these researchers were only just getting off the ground. And soon, their system sparked a technological revolution. Suddenly, machines could see in a way that was not possible in the past. This made it easier for a smartphone app to search your personal photos and find the images you were looking for. It accelerated the progress of driverless cars and other robotics. And it improved the accuracy of facial recognition services, for social networks like Facebook and for the country's law enforcement agencies. But soon, researchers noticed that these facial recognition services were less accurate when used with women and people of color. Activists raised concerns over how companies were collecting the huge amounts of data needed to train these kinds of systems. Others worried these systems would eventually lead to mass surveillance or autonomous weapons. Fonte: MATZ, Cade. NYTimes.com, 2019.]'''

QUESTOES = {
    33: (TEXTO33, 'De acordo com o texto, em geral, os leitores do clássico 1984, de George Orwell, dispensam a leitura do apêndice da obra porque'),
    34: ('', 'No trecho but rather, to language itself, o termo rather pode ser substituído, sem alteração de sentido, por'),
    35: ('', 'De acordo com o texto, é incorreto afirmar que'),
    36: (TEXTO36, 'De acordo com o texto, é correto afirmar que'),
    37: ('', 'No trecho it\'s not just democracy that is at risk, but also the economy, a expressão sublinhada expressa uma ideia de'),
    38: ('', 'De acordo com a congressista Yvette Clarke, pelos diversos riscos representados pelos vídeos deepfake, é necessário'),
    39: (TEXTO39, 'De acordo com as informações do texto, selecione a alternativa que melhor complete a afirmação: The new system proved to be less precise when'),
    40: ('', 'Analise as afirmações de I a IV em destaque.'),
}

conn = get_conn()
total = 0
for numero, (texto, enunciado) in QUESTOES.items():
    enunciado_final = texto + ' ' + enunciado if texto else enunciado
    rows = conn.execute('''
        SELECT id FROM questoes
        WHERE escola='ITA' AND ano=2020 AND fase='1'
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
            VALUES (?,'ITA','ingles',2020,?,'1',?,'[]','','dificil','["ingles"]',0)
        ''', (str(uuid.uuid4()), numero, enunciado_final))
        total += 1
        print(f'Q{numero}: inserido')

conn.commit()
conn.close()
print(f'\nTotal: {total} processadas')
