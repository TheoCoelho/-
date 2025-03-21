import json
import uuid
from PIL import Image
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, g, send_from_directory
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

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Certifique-se de que a pasta de upload existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    """Rota para upload de imagens."""
    if 'username' not in session:
        return jsonify({"success": False, "error": "Usuário não autenticado"}), 401

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    os.makedirs(user_folder, exist_ok=True)  # Cria a pasta do usuário, se não existir

    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(user_folder, filename)
        file.save(filepath)
        return jsonify({"success": True, "filename": filename}), 200

    return jsonify({"success": False, "error": "Arquivo inválido"}), 400

@app.route('/upload/design', methods=['POST'])
def upload_design_file():
    if 'username' not in session:
        return jsonify({"success": False, "error": "Usuário não autenticado"}), 401

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'design', username)
    os.makedirs(user_folder, exist_ok=True)

    file = request.files.get('file')
    custom_name = request.form.get('image_name', '').strip()

    if not file or not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Arquivo inválido"}), 400

    extension = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{secure_filename(custom_name)}.{extension}" if custom_name else secure_filename(file.filename)
    filepath = os.path.join(user_folder, filename)
    file.save(filepath)

    image_url = url_for('static', filename=f'uploads/design/{username}/{filename}', _external=False)
    return jsonify({"success": True, "image_url": image_url, "image_name": custom_name or filename}), 200

@app.route('/upload-img-data/design')
def upload_img_data_design():
    if 'username' not in session:
        return jsonify({"success": False, "error": "Usuário não autenticado"}), 401

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'design', username)

    # Cria a pasta do usuário caso não exista
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        return jsonify({"images": []})

    # Lista os arquivos do diretório com timestamps de criação
    images = [
        {
            "path": os.path.join(user_folder, img),
            "filename": img,
            "created_time": os.path.getctime(os.path.join(user_folder, img))
        }
        for img in os.listdir(user_folder)
    ]

    # Ordena por data de criação (mais recente primeiro)
    images.sort(key=lambda x: x["created_time"], reverse=True)

    # Retorna os dados ordenados
    image_data = [
        {
            "url": url_for('static', filename=f'uploads/design/{username}/{img["filename"]}', _external=False),
            "name": "_".join(os.path.splitext(img["filename"])[0].split("_")[1:]),
        }
        for img in images
    ]
    return jsonify({"images": image_data})



@app.route('/save-edited-image', methods=['POST'])
def save_edited_image():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'}), 401

    file = request.files.get('image')
    if file:
        username = session['username']
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'design', username)
        os.makedirs(user_folder, exist_ok=True)

        unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(user_folder, unique_filename)
        file.save(filepath)

        # Retorna a URL da nova imagem
        image_url = url_for('static', filename=f'uploads/design/{username}/{unique_filename}')
        return jsonify({'success': True, 'filepath': image_url})
    return jsonify({'success': False, 'error': 'Nenhuma imagem enviada'}), 400



def save_image(image_path):
    img = Image.open(image_path)
    img.save(image_path, format="PNG", quality=100)  # Mantém a máxima qualidade

@app.route('/upload-img-data')
def upload_img_data():
    """Retorna as imagens do usuário no formato JSON."""
    if 'username' not in session:
        return jsonify({"success": False, "error": "Usuário não autenticado"}), 401

    username = session['username']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)

    if not os.path.exists(user_folder):
        return jsonify({"images": []})  # Nenhuma imagem para o usuário

    images = os.listdir(user_folder)
    # Resolve o caminho completo da imagem
    images = [url_for('static', filename=f'uploads/{username}/{img}') for img in images]
    return jsonify({"images": images})

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

import json

@app.route('/design')
def design_route():
    # Pega os parâmetros da URL ou da sessão
    modelo = request.args.get('modelo', session.get('design_atual', {}).get('modelo', 'default')).lower()

    print(f"Modelo recebido: {modelo}")

    # Ler os dados do JSON
    with open('static/carrossel_opcoes.json') as f:
        data = json.load(f)

    # Verifica se o modelo existe no JSON
    if modelo in data['pecas']:
        imagem = data['pecas'][modelo].get('imagem', 'default.png')
        silhueta = data['pecas'][modelo].get('silhueta', 'default_silhueta.svg')
    else:
        print(f"Modelo {modelo} não encontrado no JSON. Usando padrão.")
        imagem = 'default.png'
        silhueta = 'default_silhueta.svg'

    caminho_silhueta = os.path.join('static/models', silhueta)

    # Verifica se a silhueta existe
    if os.path.exists(caminho_silhueta):
        silhueta = url_for('static', filename=f'models/{silhueta}')
    else:
        print(f"Silhueta {silhueta} não encontrada, usando padrão.")
        silhueta = url_for('static', filename='models/default_silhueta.svg')

    print(f"Silhueta final enviada para o template: {silhueta}")

    return render_template('design.html', selecao={'modelo': modelo}, imagem=imagem, silhueta=silhueta)

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

@app.route('/gallery-data')
def gallery_data():
    """Retorna a lista de imagens no formato JSON."""
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    images = [f'/{UPLOAD_FOLDER}/{img}' for img in images]
    return {"images": images}
@app.route('/image-editor/<path:filename>')
def serve_image_editor(filename):
    return send_from_directory('image-editor', filename)

import os

@app.route('/list-models')
def list_models():
    files = os.listdir('static/models')
    return jsonify(files)


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
