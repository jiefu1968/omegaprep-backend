import os
from dotenv import load_dotenv
load_dotenv()

print("Testando Groq...")
from groq import Groq
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
r = groq.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role":"user","content":"Diga apenas: Groq funcionando!"}],
    max_tokens=20
)
print("✅", r.choices[0].message.content)

print("\nTestando Claude...")
import anthropic
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
r = claude.messages.create(
    model="claude-opus-4-5",
    max_tokens=20,
    messages=[{"role":"user","content":"Diga apenas: Claude funcionando!"}]
)
print("✅", r.content[0].text)
