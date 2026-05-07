import anthropic
from groq import Groq
from app.config import ANTHROPIC_API_KEY, GROQ_API_KEY
from app.utils import formatar_texto_ia
groq_client = Groq(api_key=GROQ_API_KEY)

def get_claude():
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def tem_imagem(conteudo: list) -> bool:
    return any(item.get("type") == "image" for item in conteudo)
def gerar_resposta_matematica(prompt: str) -> str:
    # 1. Chama a IA (Groq no exemplo)
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 2. Captura o texto bruto
    texto_bruto = completion.choices[0].message.content
    
    # 3. APLICA A LIMPEZA (Aqui é onde a mágica acontece!)
    return formatar_texto_ia(texto_bruto)