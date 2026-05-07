import os
from groq import Groq
from app.llm import groq_client, get_claude
from app.config import GROQ_MODEL, CLAUDE_MODEL
from app.rag.prompts import prompt_visao, prompt_base, prompt_disciplina, prompt_modo
from app.rag.indexer import buscar_similares

def stream_groq(messages):
    clients = [groq_client]
    key2 = os.getenv("GROQ_API_KEY_2")
    if key2:
        clients.append(Groq(api_key=key2))
    for i, client in enumerate(clients):
        try:
            print(f"[AGENTE] Groq key {i+1}...")
            stream = client.chat.completions.create(
                model=GROQ_MODEL, messages=messages,
                temperature=0.2, max_tokens=4000, stream=True
            )
            return stream
        except Exception as e:
            print(f"[AGENTE] Groq key {i+1} falhou: {e}")
    return None

def stream_together(messages):
    key = os.getenv("TOGETHER_API_KEY")
    if not key:
        return None
    try:
        import together
        print("[AGENTE] Tentando Together AI...")
        client = together.Together(api_key=key)
        return client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=messages,
            temperature=0.2, max_tokens=4000, stream=True
        )
    except Exception as e:
        print(f"[AGENTE] Together falhou: {e}")
        return None

async def orquestrador_stream(
    modo, pergunta, escola, disciplina,
    nivel="medio", quantidade=5, fase=1,
    historico=None, imagem_b64=None, imagem_tipo="image/jpeg", gabarito=None
):
    print(f"[AGENTE] modo={modo} escola={escola} disciplina={disciplina} gabarito={gabarito} tem_imagem={imagem_b64 is not None}")

    instrucao_gabarito = ""
    if gabarito and gabarito.strip():
        instrucao_gabarito = f"""
## GABARITO OFICIAL
A resposta correta oficial é a alternativa **{gabarito.upper()}**.
OBRIGATÓRIO: Valide sua resolução contra o gabarito e confirme ou corrija."""

    if imagem_b64 is not None and len(imagem_b64) > 10:
        print("[AGENTE] Usando Claude Vision")
        system = prompt_visao() + instrucao_gabarito
        content = [
            {"type": "image", "source": {"type": "base64", "media_type": imagem_tipo, "data": imagem_b64}},
            {"type": "text", "text": f"Vestibular: {escola}\nDisciplina: {disciplina}\n\n{pergunta or 'Resolva esta questão.'}"}
        ]
        try:
            claude = get_claude()
            with claude.messages.stream(
                model=CLAUDE_MODEL, max_tokens=4000, system=system,
                messages=[{"role": "user", "content": content}]
            ) as stream:
                for text in stream.text_stream:
                    for char in text:
                        yield "data: \n\n" if char == "\n" else f"data: {char}\n\n"
        except Exception as e:
            print(f"[AGENTE] Erro Claude Vision: {e}")
            yield "data: Erro ao processar imagem.\n\n"
    else:
        system = (
            prompt_base(escola, disciplina) +
            prompt_disciplina(disciplina) +
            prompt_modo(modo, escola, disciplina, nivel, quantidade, fase) +
            instrucao_gabarito
        )
        try:
            contexto = buscar_similares(pergunta, top_k=3, escola=escola, disciplina=disciplina.lower())
            if contexto:
                bloco = "\n\n---\n\n".join([r["texto"] for r in contexto])
                system += f"\n\nQuestões reais do banco:\n{bloco}"
        except Exception as e:
            print(f"[RAG] Erro: {e}")

        messages = [{"role": "system", "content": system}]
        if historico:
            for msg in historico[-10:]:
                if msg.get("role") in ("user", "assistant") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})
        else:
            messages.append({"role": "user", "content": pergunta})

        stream = stream_groq(messages)
        if stream is None:
            stream = stream_together(messages)

        if stream:
            try:
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        for char in delta:
                            yield "data: \n\n" if char == "\n" else f"data: {char}\n\n"
            except Exception as e:
                print(f"[AGENTE] Erro stream: {e}")
                yield "data: Erro ao gerar resposta.\n\n"
        else:
            yield "data: Serviço temporariamente indisponível. Tente novamente em alguns minutos.\n\n"

    yield "data: [DONE]\n\n"
