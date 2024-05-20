from flask import render_template, request, redirect, session
from app import app
from post import obter_posts, criar_post
from werkzeug.utils import secure_filename
from utils import allowed_file
import os

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
        usuario = session.get("username")
        posts = obter_posts()
        return render_template("index.html", username=usuario, posts=posts)
