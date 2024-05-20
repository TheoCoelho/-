from flask import request, redirect, render_template
from db import conectar_bd
from werkzeug.utils import secure_filename
import os
from PIL import Image

from utils import allowed_file

def settings_page(session, redirect, request, conectar_bd, app):
    if "username" in session:
        if request.method == "POST":
            username = session["username"]
            
            # Verifica se há uma solicitação para atualizar a foto de perfil
            profile_pic = request.files.get("profile_pic")
            if profile_pic and allowed_file(profile_pic.filename):
                filename = secure_filename(profile_pic.filename)
                profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_pic.save(profile_pic_path)
                profile_pic_url = f"/{app.config['UPLOAD_FOLDER']}/{filename}"
                
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
            
            return redirect("/settings")
        else:
            username = session["username"]
            return render_template("settings.html", username=username)
    else:
        return redirect("/login")
