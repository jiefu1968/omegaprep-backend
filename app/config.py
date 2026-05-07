from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY      = os.getenv("GROQ_API_KEY")

GROQ_MODEL        = "llama-3.3-70b-versatile"
CLAUDE_MODEL      = "claude-opus-4-5"
EMBED_MODEL       = "/Users/jefersonchagas/MeusProjetos/omegaprep-backend/modelo_local"
DB_PATH           = "omegaprep.db"
EMBEDDINGS_PATH   = "app/rag/embeddings.pkl"
CONHECIMENTO_PATH = "conhecimento"
STATIC_PATH       = "static"
