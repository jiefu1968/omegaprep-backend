import asyncio
from app.rag.agente import orquestrador_stream

async def teste():
    print("Testando agente de questões...\n")
    resposta = ""
    async for chunk in orquestrador_stream(
        modo="questoes",
        pergunta="explique logaritmos",
        escola="ITA",
        disciplina="matematica"
    ):
        if chunk.startswith("data: ") and "[DONE]" not in chunk:
            resposta += chunk[6:]

    print(resposta[:500])
    print("\n✅ Agente funcionando!")

asyncio.run(teste())
