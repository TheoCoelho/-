import sqlite3

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
