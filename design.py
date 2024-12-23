# design.py

from flask import session, jsonify
from db import conectar_bd

# Função para armazenar seleções na sessão
def salvar_selecao(parte, modelo, opcoes=None):
    session['design_atual'] = {  # Sobrescreve as seleções anteriores
        'parte': parte,
        'modelo': modelo,
        'opcoes': opcoes
    }
    session.modified = True  # Garante a atualização da sessão

# Função para recuperar seleções
def obter_selecao():
    return session.get('design_atual', {})

# Função para salvar design no banco
def salvar_design_no_bd(username, parte, modelo, opcoes):
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO designs (username, parte, modelo, opcoes)
            VALUES (?, ?, ?, ?)
        """, (username, parte, modelo, ",".join(opcoes) if opcoes else None))
        conn.commit()