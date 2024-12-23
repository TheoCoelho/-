import json
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, g
import os
from werkzeug.utils import secure_filename
from db import conectar_bd, criar_tabela_usuarios, adicionar_coluna_profile_pic, criar_tabela_posts, criar_tabela_likes, criar_tabela_comentarios, criar_tabela_compartilhamentos, criar_tabela_interacoes, buscar_url_imagem_perfil,criar_tabela_designs
from post import obter_posts, criar_post, curtir_post, descurtir_post, obter_usuarios_que_curtiram, comentar_post, compartilhar_post, get_likes_from_db
from perfil import exibir_perfil, atualizar_perfil, design_page, favoritos_page, interacoes_page
from user import cadastrar_usuario, verificar_usuario, login, logout, registro
from settings import settings_page
from utils import allowed_file
from design import salvar_selecao, obter_selecao,salvar_design_no_bd;
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "sua_chave_secreta"
app.config['UPLOAD_FOLDER'] = 'static/uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

@app.route('/')
def home():
    username = session.get('username')
    profile_pic = session.get('profile_pic', '/static/uploads/default/profile_pic.jpg')
    return render_template('index.html', username=username, profile_pic=profile_pic)

@app.route('/criar')
def criar():
    return render_template('criar.html')

@app.route("/index", methods=["GET", "POST"])
def main_page():
    usuario = session["username"] if "username" in session else None
    profile_pic = None
    if usuario:
        profile_pic = buscar_url_imagem_perfil(usuario)
    return render_template("index.html", username=usuario, profile_pic=profile_pic)

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
    if request.method == "POST":
        return atualizar_perfil(app)
    else:
        return exibir_perfil(app)

@app.route("/curtir/<int:post_id>", methods=["POST"])
def curtir(post_id):
    if "username" in session:
        curtir_post(post_id, session["username"])
    return jsonify(success=True)

@app.route("/descurtir/<int:post_id>", methods=["POST"])
def descurtir(post_id):
    if "username" in session:
        descurtir_post(post_id, session["username"])
    return jsonify(success=True)

@app.route("/meusdesign")
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
    usuarios = obter_usuarios_que_curtiram(post_id)
    return jsonify(usuarios=usuarios)

@app.route('/redesocial', methods=["GET", "POST"])
def redesocial():
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
        profile_pic = None
        if usuario:
            profile_pic = buscar_url_imagem_perfil(usuario)
        return render_template("redesocial.html", username=usuario, posts=posts, profile_pic=profile_pic)

@app.route("/like", methods=["POST"])
def like_post():
    if "username" in session:
        post_id = request.form["post_id"]
        username = session["username"]
        liked = curtir_post(post_id, username)
        likes = get_likes_from_db(post_id)
        return jsonify(success=True, liked=liked, likes=likes)
    return jsonify(success=False)

@app.route("/unlike", methods=["POST"])
def unlike_post():
    if "username" in session:
        post_id = request.form["post_id"]
        username = session["username"]
        descurtir_post(post_id, username)
        likes = get_likes_from_db(post_id)
        return jsonify(success=True, likes=likes)
    return jsonify(success=False)

@app.route("/comentario", methods=["POST"])
def comentar():
    if "username" in session:
        post_id = request.form["post_id"]
        comentario = request.form["comentario"]
        username = session["username"]
        comentar_post(post_id, username, comentario)
        return jsonify(success=True)
    return jsonify(success=False)

@app.route("/comments/<int:post_id>")
def get_comments(post_id):
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, comentario FROM comentarios WHERE post_id = ?", (post_id,))
        comments = [{"username": row[0], "comentario": row[1]} for row in cursor.fetchall()]
    return jsonify(comments=comments)

@app.route("/share", methods=["POST"])
def share():
    if "username" in session:
        post_id = request.form["post_id"]
        username = session["username"]
        compartilhar_post(post_id, username)
        post_url = url_for('redesocial', _external=True) + f"#post-{post_id}"
        return jsonify(success=True, url=post_url)
    return jsonify(success=False)

@app.route('/get_likes')
def get_likes():
    post_id = request.args.get('post_id')
    likes = get_likes_from_db(post_id)
    return jsonify({'likes': likes})

@app.before_request
def load_profile_pic():
    if 'username' in session:
        g.username = session['username']
        g.profile_pic = session.get('profile_pic')
        if not g.profile_pic:
            g.profile_pic = buscar_url_imagem_perfil(session['username'])
            session['profile_pic'] = g.profile_pic
    else:
        g.username = None
        g.profile_pic = '/static/uploads/default/profile_pic.jpg'

@app.context_processor
def inject_user():
    return {'username': g.username, 'profile_pic': g.profile_pic}

@app.route('/get_carrossel_options/<part>')
def get_carrossel_options(part):
    with open('carrossel_opcoes.json') as f:
        data = json.load(f)
    if part in data:
        return jsonify(data[part])
    else:
        return jsonify({"error": "Part not found"}), 404
    


@app.route('/get_modelos/<opcao>')
def get_modelos(opcao):
    with open('static/carrossel_opcoes.json') as f:
        data = json.load(f)
    modelos = data['tronco']['modelos'].get(opcao, [])
    return jsonify(modelos=modelos)


@app.route('/design')
def design_route():
    selecao = session.get('design_atual')
    if not selecao:
        selecao = {'parte': 'Nenhuma', 'modelo': 'Seleção'}
    return render_template('design.html', selecao=selecao)


@app.route('/confirmar-selecao', methods=['POST'])
def confirmar_selecao():
    parte = request.form.get('parte')
    modelo = request.form.get('modelo')

    if not parte or not modelo:
        return jsonify({'error': 'Seleção inválida'}), 400

    # Atualiza a sessão
    session['design_atual'] = {'parte': parte, 'modelo': modelo}
    session.modified = True

    # Confirma o sucesso para redirecionamento via JavaScript
    return jsonify(success=True)


@app.route('/editar-design', methods=['POST'])
def editar_design():
    novo_nome = request.form.get('novo_nome')
    
    if not novo_nome:
        return jsonify(success=False, message="Nome inválido.")

    # Atualiza a sessão com o novo nome
    if 'design_atual' in session:
        session['design_atual']['modelo'] = novo_nome
        session.modified = True
        return jsonify(success=True)
    
    return jsonify(success=False, message="Nenhum design selecionado.")

if __name__ == "__main__":
    with app.app_context():
        criar_tabela_usuarios()
        adicionar_coluna_profile_pic()
        criar_tabela_posts()
        criar_tabela_likes()
        criar_tabela_comentarios()
        criar_tabela_compartilhamentos()
        criar_tabela_interacoes() 
        criar_tabela_designs()

    app.run(debug=True)
