from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import os
from werkzeug.utils import secure_filename
from db import conectar_bd, criar_tabela_usuarios, adicionar_coluna_profile_pic, criar_tabela_posts, criar_tabela_likes, criar_tabela_comentarios, criar_tabela_compartilhamentos, criar_tabela_interacoes
from post import obter_posts, criar_post, curtir_post, descurtir_post, obter_usuarios_que_curtiram, comentar_post, compartilhar_post, get_likes_from_db
from perfil import exibir_perfil, atualizar_perfil, design_page, favoritos_page, interacoes_page
from user import cadastrar_usuario, verificar_usuario, login, logout, registro
from settings import settings_page
from utils import allowed_file

app = Flask(__name__, template_folder='templates')
app.secret_key = "sua_chave_secreta"
app.config['UPLOAD_FOLDER'] = 'static/uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

@app.route("/")
def home():
    return redirect("/index")

@app.route("/index", methods=["GET", "POST"])
def main_page():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login_route():
    return login(request, session, redirect, render_template)

@app.route("/logout")
def logout_route():
    return logout(session, redirect)

@app.route("/registro", methods=["GET", "POST"])
def registro_route():
    return registro(request, verificar_usuario, cadastrar_usuario, redirect, render_template)

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    """Rota para a página de perfil."""
    if request.method == "POST":
        return atualizar_perfil(app)
    else:
        return exibir_perfil(app)

@app.route("/curtir/<int:post_id>", methods=["POST"])
def curtir(post_id):
    """Rota para curtir um post."""
    if "username" in session:
        curtir_post(post_id, session["username"])
    return redirect("/")

@app.route("/descurtir/<int:post_id>", methods=["POST"])
def descurtir(post_id):
    """Rota para descurtir um post."""
    if "username" in session:
        descurtir_post(post_id, session["username"])
    return redirect("/")

@app.route("/design")
def design():
    return design_page()

@app.route("/favoritos")
def favoritos():
    return favoritos_page()

@app.route("/interacoes")
def interacoes():
    return interacoes_page()

@app.route("/settings", methods=["GET", "POST"])
def settings():
    return settings_page(session, redirect, request, conectar_bd, app)

@app.route("/usuarios_que_curtiram/<int:post_id>")
def usuarios_que_curtiram(post_id):
    """Rota para obter os usuários que curtiram um post."""
    usuarios = obter_usuarios_que_curtiram(post_id)
    return jsonify(usuarios=usuarios)

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

@app.route("/unlike", methods=["POST"])
def unlike_post():
    """Rota para descurtir um post."""
    if "username" in session:
        post_id = request.form["post_id"]
        username = session["username"]
        descurtir_post(post_id, username)
        return jsonify(success=True)
    return jsonify(success=False)

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

@app.route('/get_likes')
def get_likes():
    likes = get_likes_from_db()
    return jsonify({'likes': likes})

if __name__ == "__main__":
    with app.app_context():
        criar_tabela_usuarios()
        adicionar_coluna_profile_pic()
        criar_tabela_posts()
        criar_tabela_likes()
        criar_tabela_comentarios()
        criar_tabela_compartilhamentos()
        criar_tabela_interacoes()  # Adicione esta linha
    app.run(debug=True)