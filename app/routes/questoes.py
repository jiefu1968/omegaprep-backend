import json
import base64
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_conn
from app.rag.agente import orquestrador_stream
from app.utils import formatar_texto_ia
router = APIRouter(prefix="/questoes", tags=["questoes"])

class AgenteRequest(BaseModel):
    modo: str
    pergunta: str
    escola: str
    disciplina: str
    nivel: str = "medio"
    quantidade: int = 5
    fase: int = 1
    historico: Optional[list] = None
    gabarito: Optional[str] = None

@router.get("/")
def listar(escola: str = None, disciplina: str = None, ano: int = None):
    conn = get_conn()
    query = "SELECT * FROM questoes WHERE 1=1"
    params = []
    if escola:
        query += " AND escola=?"; params.append(escola)
    if disciplina:
        query += " AND disciplina=?"; params.append(disciplina)
    if ano:
        query += " AND ano=?"; params.append(ano)
    query += " ORDER BY numero ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    # Criamos uma lista formatada
    questoes_formatadas = []
    for r in rows:
        q_dict = dict(r)
        q_dict["enunciado"] = formatar_texto_ia(q_dict.get("enunciado", ""))
        questoes_formatadas.append(q_dict)
        
    return questoes_formatadas

@router.get("/{questao_id}")
def buscar(questao_id: str):
    conn = get_conn()
    q = conn.execute("SELECT * FROM questoes WHERE id=?", (questao_id,)).fetchone()
    r = conn.execute("SELECT * FROM resolucoes WHERE questao_id=?", (questao_id,)).fetchone()
    conn.close()

    if not q:
        return {"erro": "Questão não encontrada"}

    # 1. Transformamos em dicionário e aplicamos a limpeza
    questao_dict = dict(q)
    questao_dict["enunciado"] = formatar_texto_ia(questao_dict.get("enunciado", ""))

    # 2. Tratamos a resolução se ela existir
    resolucao_dict = dict(r) if r else None
    if resolucao_dict:
        campo = "explicação" if "explicação" in resolucao_dict else "texto"
        resolucao_dict[campo] = formatar_texto_ia(resolucao_dict.get(campo, ""))

    return {"questao": questao_dict, "resolucao": resolucao_dict}
@router.post("/agente/stream")
async def agente_stream(req: AgenteRequest):
    return StreamingResponse(
        orquestrador_stream(
            modo=req.modo,
            pergunta=req.pergunta,
            escola=req.escola,
            disciplina=req.disciplina,
            nivel=req.nivel,
            quantidade=req.quantidade,
            fase=req.fase,
            historico=req.historico,
            gabarito=req.gabarito,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

@router.post("/resolver")
async def resolver_com_imagem(
    escola: str = Form(...),
    disciplina: str = Form(...),
    enunciado: str = Form(""),
    gabarito: str = Form(""),
    imagem: UploadFile = File(None)
):
    imagem_b64 = None
    imagem_tipo = "image/jpeg"

    if imagem:
        conteudo = await imagem.read()
        imagem_b64 = base64.standard_b64encode(conteudo).decode()
        ext = imagem.filename.split('.')[-1].lower()
        imagem_tipo = f"image/{'jpeg' if ext in ['jpg','jpeg'] else 'png'}"

    return StreamingResponse(
        orquestrador_stream(
            modo="gpt",
            pergunta=enunciado or "Resolva esta questão didaticamente.",
            escola=escola,
            disciplina=disciplina,
            imagem_b64=imagem_b64,
            imagem_tipo=imagem_tipo,
            gabarito=gabarito,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
