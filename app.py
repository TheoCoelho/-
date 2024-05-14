from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from datetime import datetime
import os
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
app.secret_key = "sua_chave_secreta"

app.config['UPLOAD_FOLDER'] = 'static/uploads'

UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def conectar_bd():
    """Conecta ao banco de dados e retorna a conexão."""
    return sqlite3.connect("usuarios.db")

def criar_tabela_usuarios():
    """Cria a tabela de usuários se ela não existir e insere um usuário administrador padrão."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
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

        



def cadastrar_usuario(username, password):
    """Insere um novo usuário no banco de dados."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

def verificar_usuario(username, password):
    """Verifica se um usuário existe no banco de dados com o nome de usuário e senha fornecidos."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()

def obter_posts():
    """Obtém todos os posts do banco de dados."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts ORDER BY timestamp DESC")
        return cursor.fetchall()

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

@app.route("/")
def index():
    """Página inicial. Se o usuário estiver logado, redireciona para a página principal; caso contrário, exibe o formulário de login."""
    if "username" in session:
        return redirect("/home")
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Rota para processar o formulário de login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = verificar_usuario(username, password)
        if user:
            session["username"] = username
            return redirect("/home")
        else:
            return render_template("login.html", error="Usuário ou senha incorretos.")
    else:
        return render_template("login.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    """Página principal. Se o usuário estiver logado, exibe a página principal; caso contrário, redireciona para a página inicial."""
    if "username" in session:
        if request.method == "POST":
            content = request.form["content"]
            image = request.files["image"] if "image" in request.files else None
            image_url = None
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_url = f"/{app.config['UPLOAD_FOLDER']}/{filename}"  # Atualiza a URL da imagem
            criar_post(session["username"], content, image_url)
            return redirect("/home")
        else:
            usuario = session["username"]
            posts = obter_posts()
            return render_template("home.html", username=usuario, posts=posts)
    else:
        return redirect("/")



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

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    """Rota para a página de perfil."""
<<<<<<< HEAD
    return render_template("perfil.html") 
=======
    return render_template("perfil.html")

>>>>>>> 68f237b86c18a439c219d8276026ad7ddf25d94d
@app.route("/design", methods=["GET", "POST"])
def design():
    content = render_template("design.html")
    return render_template("perfil.html", content=content)

@app.route("/favoritos", methods=["GET", "POST"])
def favoritos():
    content = render_template("favoritos.html")
    return render_template("perfil.html", content=content)

@app.route("/interacoes", methods=["GET", "POST"])
def interacoes():
    content = render_template("interacoes.html")
    return render_template("perfil.html", content=content)

"""

@app.route("/get_design_content", methods=["GET"])
def get_design_content():
    with open("templates/design.html", "r") as design_file:
        design_content = design_file.read()
    return jsonify({"content": design_content})

<<<<<<< HEAD




@app.route("/get_favorites_content", methods=["GET"])
def get_favorites_content():
    with open("templates/favoritos.html", "r") as favorites_file:
        favorites_content = favorites_file.read()
    return jsonify({"content": favorites_content})




@app.route("/get_interactions_content", methods=["GET"])
def get_interactions_content():
    with open("templates/interaçoes.html", "r") as interactions_file:
        interactions_content = interactions_file.read()
    return jsonify({"content": interactions_content})
"""
=======
>>>>>>> 68f237b86c18a439c219d8276026ad7ddf25d94d
if __name__ == "__main__":
    criar_tabela_usuarios()
    criar_tabela_posts()
    app.run(debug=True)
