from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import init_db
import os
from app.llm import gerar_resposta_matematica
app = FastAPI(
    title="OmegaPrep API",
    description="Motor de IA para preparação de vestibulares",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve arquivos estáticos (imagens de questões)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
def startup():
    init_db()
    print("✅ OmegaPrep API iniciada!")

@app.get("/")
def root():
    return {"status": "ok", "app": "OmegaPrep API", "versao": "1.0.0"}

from app.routes.questoes import router as questoes_router
app.include_router(questoes_router)
