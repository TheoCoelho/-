from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import sqlite3
from datetime import datetime
import os
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
app.secret_key = "sua_chave_secreta"

app.config['UPLOAD_FOLDER'] = 'static/uploads'

UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def conectar_bd():
    """Conecta ao banco de dados e retorna a conexão."""
    return sqlite3.connect("usuarios.db")

def adicionar_coluna_profile_pic():
    """Adiciona a coluna profile_pic à tabela de usuários, se ainda não existir."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        if 'profile_pic' not in column_names:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN profile_pic TEXT")
            conn.commit()

def criar_tabela_usuarios():
    """Cria a tabela de usuários se ela não existir e insere um usuário administrador padrão."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                profile_pic TEXT
            )
        """)
        cursor.execute("SELECT * FROM usuarios WHERE username = 'lc'")
        admin = cursor.fetchone()
        if not admin:
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", ('lc', '1908'))
            conn.commit()

def criar_tabela_posts():
    """Cria a tabela de posts se ela não existir."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                image_url TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def criar_tabela_likes():
    """Cria a tabela de curtidas se ela não existir."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY,
                post_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)
        conn.commit()

def criar_tabela_comentarios():
    """Cria a tabela de comentários se ela não existir."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comentarios (
                id INTEGER PRIMARY KEY,
                post_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                comentario TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)
        conn.commit()


def criar_tabela_compartilhamentos():
    """Cria a tabela de compartilhamentos se ela não existir."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compartilhamentos (
                id INTEGER PRIMARY KEY,
                post_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        """)
        conn.commit()

def cadastrar_usuario(username, password):
    """Insere um novo usuário no banco de dados."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?, ?)", (username, password))
        conn.commit()

def verificar_usuario(username, password):
    """Verifica se um usuário existe no banco de dados com o nome de usuário e senha fornecidos."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()

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
        # Obtém os comentários de cada post
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

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def curtir_post(post_id, username):
    """Adiciona uma curtida a um post, se o usuário ainda não tiver curtido."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM likes WHERE post_id = ? AND username = ?", (post_id, username))
        like = cursor.fetchone()
        if not like:
            cursor.execute("INSERT INTO likes (post_id, username) VALUES (?, ?)", (post_id, username))
            conn.commit()

def obter_usuarios_que_curtiram(post_id):
    """Obtém a lista de usuários que curtiram um post."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM likes WHERE post_id = ?", (post_id,))
        return [row[0] for row in cursor.fetchall()]

@app.route("/usuarios_que_curtiram/<int:post_id>")
def usuarios_que_curtiram(post_id):
    """Rota para obter os usuários que curtiram um post."""
    usuarios = obter_usuarios_que_curtiram(post_id)
    return jsonify(usuarios=usuarios)




def comentar_post(post_id, username, comentario):
    """Adiciona um comentário a um post."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comentarios (post_id, username, comentario) VALUES (?, ?, ?)", (post_id, username, comentario))
        conn.commit()


def compartilhar_post(post_id, username):
    """Adiciona um compartilhamento a um post."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO compartilhamentos (post_id, username) VALUES (?, ?)", (post_id, username))
        conn.commit()

@app.route("/")
def home():
    """Redireciona todos os visitantes para a página principal."""
    return redirect("/index")

@app.route('/redesocial', methods=["GET", "POST"])
def redesocial():
    """Página da rede social. Se o usuário estiver logado, exibe a página com os posts; caso contrário, redireciona para a página de login."""
    if request.method == "POST":
        content = request.form["content"]
        image = request.files["image"] if "image" in request.files else None
        image_url = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_url = f"/{app.config['UPLOAD_FOLDER']}/{filename}"
        criar_post(session["username"], content, image_url)
        return redirect("/redesocial")
    else:
        usuario = session["username"] if "username" in session else None
        posts = obter_posts()
        return render_template("redesocial.html", username=usuario, posts=posts)

@app.route("/like", methods=["POST"])
def like_post():
    """Endpoint para curtir ou descurtir um post."""
    if "username" in session:
        post_id = request.form["post_id"]
        username = session["username"]
        liked = curtir_post(post_id, username)
        return jsonify(success=True, liked=liked)
    return jsonify(success=False)

def curtir_post(post_id, username):
    """Curtir ou descurtir um post."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM likes WHERE post_id = ? AND username = ?", (post_id, username))
        existing_like = cursor.fetchone()

        if existing_like:
            # Se o usuário já curtiu o post, descurtir
            cursor.execute("DELETE FROM likes WHERE post_id = ? AND username = ?", (post_id, username))
            liked = False
        else:
            # Se o usuário ainda não curtiu o post, curtir
            cursor.execute("INSERT INTO likes (post_id, username) VALUES (?, ?)", (post_id, username))
            liked = True
        
        conn.commit()
        
        return liked


@app.route("/unlike", methods=["POST"])
def unlike_post():
    """Rota para descurtir um post."""
    if "username" in session:
        post_id = request.form["post_id"]
        username = session["username"]
        descurtir_post(post_id, username)
        return jsonify(success=True)
    return jsonify(success=False)

def descurtir_post(post_id, username):
    """Remove uma curtida de um post, se o usuário tiver curtido."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM likes WHERE post_id = ? AND username = ?", (post_id, username))
        conn.commit()


@app.route("/comentario", methods=["POST"])
def comentar():
    """Rota para comentar em um post."""
    if "username" in session:
        post_id = request.form["post_id"]
        comentario = request.form["comentario"]
        username = session["username"]
        comentar_post(post_id, username, comentario)
        return jsonify(success=True)
    return jsonify(success=False)

@app.route("/comment", methods=["POST"])
def comment():
    """Rota para adicionar um comentário em um post."""
    if "username" in session:
        post_id = request.form["post_id"]
        comentario = request.form["comentario"]
        username = session["username"]
        comentar_post(post_id, username, comentario)
        return jsonify(success=True)
    return jsonify(success=False)

@app.route("/comments/<int:post_id>")
def get_comments(post_id):
    """Rota para obter os comentários de um post."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, comentario FROM comentarios WHERE post_id = ?", (post_id,))
        comments = [{"username": row[0], "comentario": row[1]} for row in cursor.fetchall()]
    return jsonify(comments=comments)





@app.route("/share", methods=["POST"])
def share():
    """Rota para compartilhar um post."""
    if "username" in session:
        post_id = request.form["post_id"]
        username = session["username"]
        compartilhar_post(post_id, username)
        post_url = url_for('redesocial', _external=True) + f"#post-{post_id}"
        return jsonify(success=True, url=post_url)
    return jsonify(success=False)


def obter_usuarios_que_curtiram(post_id):
    """Obtém a lista de usuários que curtiram um post."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM likes WHERE post_id = ?", (post_id,))
        return [row[0] for row in cursor.fetchall()]



@app.route("/login", methods=["GET", "POST"])
def login():
    """Rota para processar o formulário de login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = verificar_usuario(username, password)
        if user:
            session["username"] = username
            return redirect("/index")
        else:
            return render_template("login.html", error="Usuário ou senha incorretos.")
    else:
        return render_template("login.html")

@app.route("/index", methods=["GET", "POST"])
def main_page():
    """Página principal. Se o usuário estiver logado, exibe a página principal; caso contrário, redireciona para a página inicial."""
    if request.method == "POST":
        content = request.form["content"]
        image = request.files["image"] if "image" in request.files else None
        image_url = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_url = f"/{app.config['UPLOAD_FOLDER']}/{filename}"
        criar_post(session["username"], content, image_url)
        return redirect("/index")
    else:
        usuario = session["username"] if "username" in session else None
        posts = obter_posts()
        return render_template("index.html", username=usuario, posts=posts)

@app.route("/logout")
def logout():
    """Rota para fazer logout. Remove o usuário da sessão e redireciona para a página inicial."""
    session.pop("username", None)
    return redirect("/")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    """Rota para o formulário de registro."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with conectar_bd() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                return render_template("registro.html", error="Usuário já existe. Tente outro.")
            else:
                cadastrar_usuario(username, password)
                return redirect("/")
    return render_template("registro.html")

from PIL import Image

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    """Rota para a página de perfil."""
    if request.method == "POST":
        if "username" in session:
            username = session["username"]
            profile_pic = request.files["profile_pic"] if "profile_pic" in request.files else None
            if profile_pic and allowed_file(profile_pic.filename):
                filename = secure_filename(profile_pic.filename)
                profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_pic.save(profile_pic_path)
                profile_pic_url = f"/{app.config['UPLOAD_FOLDER']}/{filename}"
                
                # Redimensiona a imagem para que o lado maior tenha 150 pixels
                img = Image.open(profile_pic_path)
                img.thumbnail((150, 150))
                
                # Calcula as coordenadas de recorte para fazer um recorte de 150x150 pixels centrado na imagem
                width, height = img.size
                left = (width - 150) / 2
                top = (height - 150) / 2
                right = (width + 150) / 2
                bottom = (height + 150) / 2
                
                # Recorta a imagem
                img = img.crop((left, top, right, bottom))
                
                # Salva a imagem recortada
                img.save(profile_pic_path)
                
                with conectar_bd() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE usuarios SET profile_pic = ? WHERE username = ?", (profile_pic_url, username))
                    conn.commit()
            return redirect("/perfil")
        else:
            return redirect("/login")
    else:
        if "username" in session:
            username = session["username"]
            with conectar_bd() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT profile_pic FROM usuarios WHERE username = ?", (username,))
                profile_pic = cursor.fetchone()[0]
            return render_template("perfil.html", profile_pic=profile_pic, username=username)

@app.route("/design", methods=["GET", "POST"])
def design():
    return render_template("design.html")

@app.route("/favoritos", methods=["GET", "POST"])
def favoritos():
    return render_template("favoritos.html")

@app.route("/interacoes", methods=["GET", "POST"])
def interacoes():
    return render_template("interacoes.html")



@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        if "username" in session:
            username = session["username"]
            
            # Editar foto de perfil
            profile_pic = request.files.get("profile_pic")  # Usar request.files.get para evitar KeyError
            if profile_pic and allowed_file(profile_pic.filename):
                # Processar a foto do perfil
                filename = secure_filename(profile_pic.filename)
                profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_pic.save(profile_pic_path)
                profile_pic_url = f"/{app.config['UPLOAD_FOLDER']}/{filename}"
                
                # Redimensiona a imagem para que o lado maior tenha 150 pixels
                img = Image.open(profile_pic_path)
                img.thumbnail((150, 150))
                
                # Calcula as coordenadas de recorte para fazer um recorte de 150x150 pixels centrado na imagem
                width, height = img.size
                left = (width - 150) / 2
                top = (height - 150) / 2
                right = (width + 150) / 2
                bottom = (height + 150) / 2
                
                # Recorta a imagem
                img = img.crop((left, top, right, bottom))
                
                # Salva a imagem recortada
                img.save(profile_pic_path)
                
                with conectar_bd() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE usuarios SET profile_pic = ? WHERE username = ?", (profile_pic_url, username))
                    conn.commit()
                    
                    # Redireciona de volta para a página de configurações após o envio bem-sucedido
                    return redirect("/settings")
            else:
                # Se não houver envio de foto de perfil, continue renderizando a página de configurações
                return render_template("settings.html", username=username)
        else:
            return redirect("/login")
    else:
        if "username" in session:
            username = session["username"]
            with conectar_bd() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT profile_pic FROM usuarios WHERE username = ?", (username,))
                profile_pic = cursor.fetchone()[0]
            return render_template("settings.html", profile_pic=profile_pic, username=username)
        else:
            return redirect("/login")


if __name__ == "__main__":
    with app.app_context():
        criar_tabela_usuarios()
        adicionar_coluna_profile_pic()
        criar_tabela_posts()
        criar_tabela_likes()
        criar_tabela_comentarios()
        criar_tabela_compartilhamentos()
    app.run(debug=True)
