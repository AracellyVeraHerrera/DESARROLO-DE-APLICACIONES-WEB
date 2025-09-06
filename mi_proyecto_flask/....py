from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, json, csv

app = Flask(__name__)

# --- Rutas a carpetas (asegura que existan) ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATOS_DIR = os.path.join(BASE_DIR, "datos")
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DATOS_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

# --- Configuración SQLite ---
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(DB_DIR, "usuarios.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- Modelo de base de datos ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# -------------------------
# Rutas de la aplicación
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")

# ---------- TXT ----------
@app.route("/guardar_txt", methods=["POST"])
def guardar_txt():
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        return render_template("resultado.html", mensaje="Nombre vacío.")
    path = os.path.join(DATOS_DIR, "datos.txt")
    with open(path, "a", encoding="utf-8") as f:
        f.write(nombre + "\n")
    return render_template("resultado.html", mensaje=f'Nombre "{nombre}" guardado en TXT.')

@app.route("/leer_txt")
def leer_txt():
    path = os.path.join(DATOS_DIR, "datos.txt")
    if not os.path.exists(path):
        return jsonify([])
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()]
    return jsonify(lines)

# ---------- JSON ----------
@app.route("/guardar_json", methods=["POST"])
def guardar_json():
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        return render_template("resultado.html", mensaje="Nombre vacío.")
    path = os.path.join(DATOS_DIR, "datos.json")
    data = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    data.append({"nombre": nombre})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return render_template("resultado.html", mensaje=f'Nombre "{nombre}" guardado en JSON.')

@app.route("/leer_json")
def leer_json():
    path = os.path.join(DATOS_DIR, "datos.json")
    if not os.path.exists(path):
        return jsonify([])
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

# ---------- CSV ----------
@app.route("/guardar_csv", methods=["POST"])
def guardar_csv():
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        return render_template("resultado.html", mensaje="Nombre vacío.")
    path = os.path.join(DATOS_DIR, "datos.csv")
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nombre])
    return render_template("resultado.html", mensaje=f'Nombre "{nombre}" guardado en CSV.')

@app.route("/leer_csv")
def leer_csv():
    path = os.path.join(DATOS_DIR, "datos.csv")
    if not os.path.exists(path):
        return jsonify([])
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return jsonify(rows)

# ---------- SQLite ----------
@app.route("/guardar_db", methods=["POST"])
def guardar_db():
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        return render_template("resultado.html", mensaje="Nombre vacío.")
    usuario = Usuario(nombre=nombre)
    db.session.add(usuario)
    db.session.commit()
    return render_template("resultado.html", mensaje=f'Usuario "{nombre}" guardado en SQLite.')

@app.route("/leer_db")
def leer_db():
    usuarios = Usuario.query.all()
    return jsonify([{"id": u.id, "nombre": u.nombre} for u in usuarios])

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)