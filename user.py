from db import conectar_bd, buscar_url_imagem_perfil

def cadastrar_usuario(username, password, email, nome, sobrenome, data_nascimento):
    """Insere um novo usuário no banco de dados."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password, email, nome, sobrenome, data_nascimento) VALUES (?, ?, ?, ?, ?, ?)", (username, password, email, nome, sobrenome, data_nascimento))
        conn.commit()


def verificar_usuario(username, password):
    """Verifica se um usuário existe no banco de dados com o nome de usuário e senha fornecidos."""
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()

def login(request, session, redirect, render_template):
    """Rota para processar o formulário de login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = verificar_usuario(username, password)
        if user:
            session["username"] = username
            session["profile_pic"] = buscar_url_imagem_perfil(username)  # Adicione esta linha
            return redirect("/index")
        else:
            return render_template("login.html", error="Usuário ou senha incorretos.")
    else:
        return render_template("login.html")

def logout(session, redirect):
    """Rota para fazer logout. Remove o usuário da sessão e redireciona para a página inicial."""
    session.pop("username", None)
    session.pop("profile_pic", None)
    return redirect("/")

def registro(request, verificar_usuario, cadastrar_usuario, redirect, render_template):
    """Rota para o formulário de registro."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        data_nascimento = request.form["dob"]
        if verificar_usuario(username, password):
            return render_template("registro.html", error="Usuário já existe. Tente outro.")
        else:
            cadastrar_usuario(username, password, email, firstname, lastname, data_nascimento)
            return redirect("/")
    return render_template("registro.html")


