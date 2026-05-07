import sqlite3
from app.config import DB_PATH

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS questoes (
            id TEXT PRIMARY KEY,
            escola TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            ano INTEGER,
            numero INTEGER,
            fase INTEGER DEFAULT 1,
            enunciado TEXT NOT NULL,
            alternativas TEXT DEFAULT '[]',
            gabarito TEXT,
            nivel TEXT DEFAULT 'medio',
            tags TEXT DEFAULT '[]',
            tem_imagem INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS resolucoes (
            id TEXT PRIMARY KEY,
            questao_id TEXT NOT NULL,
            passos TEXT NOT NULL,
            conceito_chave TEXT,
            dicas TEXT,
            erros_comuns TEXT,
            metodo_alternativo TEXT,
            FOREIGN KEY (questao_id) REFERENCES questoes(id)
        );

        CREATE TABLE IF NOT EXISTS sessoes (
            id TEXT PRIMARY KEY,
            aluno_id TEXT NOT NULL,
            escola TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            modo TEXT NOT NULL,
            criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS mensagens (
            id TEXT PRIMARY KEY,
            sessao_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sessao_id) REFERENCES sessoes(id)
        );
    """)
    conn.commit()
    conn.close()
    print("Banco de dados criado!")
