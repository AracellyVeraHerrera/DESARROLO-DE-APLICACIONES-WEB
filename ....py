from flask_login import UserMixin
import conexion.conexion as db

class User(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password

def get_user_by_id(user_id):
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=%s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return User(row["id_usuario"], row["nombre"], row["email"], row["password"])
    return None

def get_user_by_email(email):
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return User(row["id_usuario"], row["nombre"], row["email"], row["password"])
    return None

def insert_user(nombre, email, password):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", (nombre, email, password))
    conn.commit()
    cursor.close()
    conn.close()
