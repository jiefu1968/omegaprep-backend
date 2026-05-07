from app.db.database import get_conn, init_db
init_db()

TEXTO = """[TEXTO: A hundred years ago this weekend, a group of young artists and writers organised what they called the Modern Art Week in the new and grandiose municipal theatre in São Paulo. In fact, it lasted only for three evenings. It included a show of modernist painting, lectures, poetry recitals and music by Heitor Villa-Lobos, who was to become Brazil's best-known composer. It has since come to be seen as the founding moment of modern Brazilian artistic culture. Its centenary has brought both commemoration and some criticism. The event took place in São Paulo, then a fast-industrialising frontier city that was starting to rival Rio de Janeiro, the capital at the time, where the staid cultural establishment was based. The Brazilian modernists had their contradictions. The would-be revolutionaries were also dandies, the scions of the coffee-growing aristocracy, and they were close to the political oligarchy that ran São Paulo and Brazil. Even so, they were disrupters. The week 'was a declaration of cultural independence, that we are not simply a clumsy copy of something else', says Eduardo Giannetti, a Brazilian philosopher. The modernists' aims were later formalised in a Manifesto Antropófago (Cannibal Manifesto), written by one of the poets, Oswald de Andrade. This sought to address the dilemma of how to be a Brazilian modern artist when modernism was a European import. The answer: 'Absorption of the sacred enemy. To transform him into a totem.' In other words, Brazilians would not simply reproduce other models but digest them and turn them into something that was their own. The group embraced a national identity that, at least in theory, included black and indigenous Brazilians and their beliefs, and tropical fauna and flora. It was cultural nationalism, but of an open-minded, cosmopolitan and non-xenophobic kind. That was important. Across Latin America, modernist writers and artists were forging new national identities. As the innovative 1920s degenerated into the ideological conflicts of the 1930s, some would embrace communism and others creole fascism in its many variants. The Brazilian modernists would radicalise politically and be co-opted, too, by Getúlio Vargas, Brazil's nation-builder, who ruled for much of 1930 to 1954, by turns an autocrat and a democrat. — Fonte: How the 'Cannibal Manifesto' changed Brazil. The Economist, 2022.]"""

QUESTOES = {
    34: TEXTO + " In the second paragraph, the sentence 'Even so, they were disrupters' means that they were disrupters although",
    35: TEXTO + " The third paragraph of the text",
    36: TEXTO + " No trecho do quarto parágrafo 'That was important', o termo 'that' destacado em itálico sublinhado refere-se a",
}

conn = get_conn()
total = 0
for numero, enunciado in QUESTOES.items():
    rows = conn.execute("""
        SELECT id, enunciado FROM questoes
        WHERE escola='ITA' AND ano=2023 AND fase='1'
        AND disciplina='ingles' AND numero=?
    """, (numero,)).fetchall()
    for row in rows:
        conn.execute("UPDATE questoes SET enunciado=? WHERE id=?", (enunciado, row['id']))
        total += 1
        print(f"Q{numero}: atualizado ({len(row['enunciado'])}→{len(enunciado)} chars)")

conn.commit()
conn.close()
print(f"\nTotal: {total} questões atualizadas")
