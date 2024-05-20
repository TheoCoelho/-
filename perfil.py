import os
from flask import render_template, redirect, request, session
from PIL import Image
from werkzeug.utils import secure_filename
from db import conectar_bd
from post import allowed_file

def exibir_perfil(app):
    if "username" in session:
        username = session["username"]
        with conectar_bd() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT profile_pic FROM usuarios WHERE username = ?", (username,))
            profile_pic = cursor.fetchone()[0]
        return render_template("perfil.html", profile_pic=profile_pic, username=username)
    return redirect("/")

def atualizar_perfil(app):
    if "username" in session:
        username = session["username"]
        profile_pic = request.files.get("profile_pic")
        if profile_pic and allowed_file(profile_pic.filename):
            filename = secure_filename(profile_pic.filename)
            profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_pic.save(profile_pic_path)
            profile_pic_url = f"/{app.config['UPLOAD_FOLDER']}/{filename}"

            # Redimensionar e cortar a imagem
            img = Image.open(profile_pic_path)
            img.thumbnail((150, 150))
            width, height = img.size
            left = (width - 150) / 2
            top = (height - 150) / 2
            right = (width + 150) / 2
            bottom = (height + 150) / 2
            img = img.crop((left, top, right, bottom))
            img.save(profile_pic_path)

            with conectar_bd() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE usuarios SET profile_pic = ? WHERE username = ?", (profile_pic_url, username))
                conn.commit()
        return redirect("/perfil")
    return redirect("/login")

def design_page():
    return render_template("design.html")

def favoritos_page():
    return render_template("favoritos.html")

def interacoes_page():
    return render_template("interacoes.html")
