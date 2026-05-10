from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY      = os.getenv("GROQ_API_KEY")

GROQ_MODEL        = "llama-3.3-70b-versatile"
CLAUDE_MODEL      = "claude-opus-4-5"
EMBED_MODEL       = "/Users/jefersonchagas/MeusProjetos/omegaprep-backend/modelo_local"
# Pega a pasta onde o config.py está
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Monta o caminho para o arquivo 'questoes.db' que está na mesma pasta
DB_PATH = os.path.join(BASE_DIR, "questoes.db")
EMBEDDINGS_PATH   = "app/rag/embeddings.pkl"
CONHECIMENTO_PATH = "conhecimento"
STATIC_PATH       = "static"
