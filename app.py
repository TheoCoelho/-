from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__, template_folder='templates')
app.secret_key = "sua_chave_secreta"

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

# Rotas do Flask

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
        # Se a requisição for GET, apenas renderiza a página de login
        return render_template("login.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    """Página principal. Se o usuário estiver logado, exibe a página principal; caso contrário, redireciona para a página inicial."""
    if "username" in session:
        if request.method == "POST":
            # Processar os dados do formulário de entrada como visitante
            return "Você entrou como visitante."
        else:
            # Renderizar a página principal normalmente
            usuario = session["username"]
            return render_template("home.html", username=usuario)
    else:
        return redirect("/")

@app.route("/visitante", methods=["POST"])
def entrar_como_visitante():
    """Rota para entrar como visitante."""
    session["username"] = "visitante"
    return redirect("/home")

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
        # Verifica se o usuário já existe no banco de dados
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
    return render_template("perfil.html") 

@app.route("/design", methods=["GET", "POST"])
def design():
    """Rota para a página de design."""
    return render_template("design.html")



if __name__ == "__main__":
    criar_tabela_usuarios()
    app.run(debug=True)

