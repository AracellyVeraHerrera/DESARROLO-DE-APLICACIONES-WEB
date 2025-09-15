from flask import Flask
from Conexion.conexion import obtener_conexion

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask funcionando 🚀"

@app.route('/test_db')
def test_db():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT DATABASE();")
        resultado = cursor.fetchone()
        return f"Conectado a la base de datos: {resultado[0]}"
    except Exception as e:
        return f"Error en la conexión: {e}"

@app.route('/insertar_usuario')
def insertar_usuario():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO usuarios(nombre, mail) VALUES (%s, %s)",
        ("Juan Pérez", "juan@example.com")
    )
    conexion.commit()
    return "Usuario insertado correctamente ✅"

@app.route('/usuarios')
def listar_usuarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    return str(usuarios)

if __name__ == '__main__':
    app.run(debug=True)
