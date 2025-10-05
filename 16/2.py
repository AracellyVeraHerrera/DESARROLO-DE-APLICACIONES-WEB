from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import get_db_connection

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Ruta principal
@app.route("/")
def index():
    if "user_id" in session:
        return render_template("index.html")
    return redirect(url_for("login"))

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            flash("Credenciales incorrectas")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- CRUD USUARIOS ----------------
@app.route("/users")
def users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("users.html", users=users)

@app.route("/users/add", methods=["POST"])
def add_user():
    username = request.form["username"]
    password = request.form["password"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    conn.close()
    return redirect(url_for("users"))

@app.route("/users/delete/<int:id>")
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("users"))

# ---------------- CRUD POSTS ----------------
@app.route("/posts")
def posts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT posts.id, posts.title, posts.content, users.username FROM posts JOIN users ON posts.user_id = users.id")
    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("posts.html", posts=posts)

@app.route("/posts/add", methods=["POST"])
def add_post():
    title = request.form["title"]
    content = request.form["content"]
    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)", (title, content, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for("posts"))

@app.route("/posts/delete/<int:id>")
def delete_post(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("posts"))

if __name__ == "__main__":
    app.run(debug=True)
