import pickle
import json
import numpy as np
from pathlib import Path
from app.config import EMBEDDINGS_PATH, CONHECIMENTO_PATH, EMBED_MODEL

_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBED_MODEL)
    return _model

def build_texto_questao(q: dict) -> str:
    alts = json.loads(q["alternativas"]) if isinstance(q["alternativas"], str) else []
    tags = json.loads(q["tags"]) if isinstance(q["tags"], str) else []
    return f"""Escola: {q['escola']}
Disciplina: {q['disciplina']}
Ano: {q['ano']} | Fase: {q['fase']} | Nível: {q['nivel']}
Tags: {', '.join(tags)}
Enunciado: {q['enunciado']}
Alternativas: {' | '.join(alts)}""".strip()

def dividir_chunks(texto: str, tamanho: int = 400) -> list:
    paragrafos = texto.split('\n\n')
    chunks, atual = [], ""
    for p in paragrafos:
        if len(atual.split()) + len(p.split()) < tamanho:
            atual += "\n\n" + p
        else:
            if atual:
                chunks.append(atual.strip())
            atual = p
    if atual:
        chunks.append(atual.strip())
    return chunks or [texto]

def indexar_tudo():
    from app.db.database import get_conn
    conn = get_conn()
    rows = conn.execute("SELECT * FROM questoes").fetchall()
    conn.close()

    questao_docs = []
    for q in [dict(r) for r in rows]:
        questao_docs.append({
            "id": q["id"],
            "tipo": "questao",
            "texto": build_texto_questao(q),
            "metadata": {
                "escola": q["escola"],
                "disciplina": q["disciplina"],
                "ano": q["ano"],
                "nivel": q["nivel"],
                "fase": q["fase"],
            }
        })

    conhecimento_docs = []
    path = Path(CONHECIMENTO_PATH)
    if path.exists():
        for md in path.rglob("*.md"):
            disciplina = md.parent.name
            topico = md.stem
            texto = md.read_text(encoding="utf-8")
            for i, chunk in enumerate(dividir_chunks(texto)):
                conhecimento_docs.append({
                    "id": f"conhecimento_{disciplina}_{topico}_{i}",
                    "tipo": "conhecimento",
                    "texto": chunk,
                    "metadata": {"disciplina": disciplina, "topico": topico, "escola": ""}
                })

    todos = questao_docs + conhecimento_docs
    if not todos:
        print("Nenhum documento para indexar.")
        return

    textos = [d["texto"] for d in todos]
    print(f"Indexando {len(todos)} documentos...")

    model = get_model()
    embeddings = model.encode(textos, show_progress_bar=True)

    dados = {
        "ids":        [d["id"] for d in todos],
        "textos":     textos,
        "embeddings": embeddings,
        "metadata":   [d["metadata"] for d in todos],
        "tipos":      [d["tipo"] for d in todos],
    }

    Path(EMBEDDINGS_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(dados, f)

    print(f"✅ {len(questao_docs)} questões indexadas")
    print(f"✅ {len(conhecimento_docs)} chunks de teoria indexados")

def buscar_similares(pergunta: str, top_k=5,
                     escola=None, disciplina=None, tipos=None) -> list:
    if not Path(EMBEDDINGS_PATH).exists():
        return []

    with open(EMBEDDINGS_PATH, "rb") as f:
        dados = pickle.load(f)

    model = get_model()
    q_emb = model.encode([pergunta])
    matrix = np.array(dados["embeddings"])
    scores = np.dot(matrix, q_emb.T).flatten()
    norma = np.linalg.norm(matrix, axis=1) * np.linalg.norm(q_emb) + 1e-9
    scores = scores / norma

    indices = []
    for i, meta in enumerate(dados["metadata"]):
        if tipos and dados["tipos"][i] not in tipos:
            continue
        if escola and meta.get("escola","") not in (escola, ""):
            continue
        if disciplina and meta.get("disciplina","") != disciplina:
            continue
        indices.append(i)

    top = sorted(indices, key=lambda i: scores[i], reverse=True)[:top_k]

    return [{
        "id":       dados["ids"][i],
        "tipo":     dados["tipos"][i],
        "score":    float(scores[i]),
        "texto":    dados["textos"][i],
        "metadata": dados["metadata"][i],
    } for i in top]

if __name__ == "__main__":
    indexar_tudo()
