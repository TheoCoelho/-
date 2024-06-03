from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import sqlite3
import os
from PIL import Image
from werkzeug.utils import secure_filename

from db import conectar_bd
from user import verificar_usuario, cadastrar_usuario

def criar_post(username, content, image_url=None):
    """Cria um novo post no banco de dados."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO posts (username, content, image_url) VALUES (?, ?, ?)", (username, content, image_url))
        conn.commit()

    if image_url:
        # Verifica se a imagem precisa ser redimensionada
        img = Image.open(image_url[1:])
        if img.size != (500, 500):
            img = img.resize((500, 500))
            img.save(image_url[1:])

def obter_posts():
    """Obtém todos os posts do banco de dados, incluindo informações de foto de perfil do usuário e contagens de curtidas, comentários e compartilhamentos."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                posts.id, posts.username, posts.content, posts.timestamp, posts.image_url, usuarios.profile_pic,
                (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS num_likes,
                (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS num_comentarios,
                (SELECT COUNT(*) FROM compartilhamentos WHERE compartilhamentos.post_id = posts.id) AS num_compartilhamentos
            FROM posts
            INNER JOIN usuarios ON posts.username = usuarios.username
            ORDER BY posts.timestamp DESC
        """)
        posts = cursor.fetchall()
        posts_with_comments = []
        for post in posts:
            cursor.execute("""
                SELECT comentarios.username, comentarios.comentario, comentarios.timestamp 
                FROM comentarios 
                WHERE comentarios.post_id = ? 
                ORDER BY comentarios.timestamp ASC
            """, (post[0],))
            post_comentarios = cursor.fetchall()
            post_with_comments = list(post)
            post_with_comments.append(post_comentarios)
            posts_with_comments.append(post_with_comments)
        return posts_with_comments

def curtir_post(post_id, username):
    """Adiciona uma curtida ao post. Se já houver uma curtida do usuário, remove-a."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM likes WHERE post_id = ? AND username = ?", (post_id, username))
        existing_like = cursor.fetchone()

        if existing_like:
            cursor.execute("DELETE FROM likes WHERE post_id = ? AND username = ?", (post_id, username))
            liked = False
        else:
            cursor.execute("INSERT INTO likes (post_id, username) VALUES (?, ?)", (post_id, username))
            liked = True

        conn.commit()
    return liked

def descurtir_post(post_id, username):
    """Remove uma curtida de um post, se o usuário tiver curtido."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM likes WHERE post_id = ? AND username = ?", (post_id, username))
        conn.commit()

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    


def comentar_post(post_id, username, comentario):
    """Adiciona um comentário a um post e registra a interação."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comentarios (post_id, username, comentario) VALUES (?, ?, ?)", (post_id, username, comentario))
        conn.commit()
        
        cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
        usuario_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO interacoes (usuario_id, post_id, tipo, comentario) VALUES (?, ?, 'comentario', ?)", (usuario_id, post_id, comentario))
        conn.commit()

def compartilhar_post(post_id, username):
    """Adiciona um compartilhamento a um post."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO compartilhamentos (post_id, username) VALUES (?, ?)", (post_id, username))
        conn.commit()


def obter_usuarios_que_curtiram(post_id):
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM likes WHERE post_id = ?", (post_id,))
        return [row[0] for row in cursor.fetchall()]


def get_likes_from_db(post_id):
    """Obtém o número de curtidas de um post a partir do banco de dados."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM likes WHERE post_id = ?", (post_id,))
        likes = cursor.fetchone()[0]
    return likes