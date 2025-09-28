from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


# Conexión con MySQL
def conexionBD():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # cambia por tu usuario
        password="",  # cambia por tu password
        database="desarrollo_web"
    )


# Página principal
@app.route('/')
def index():
    return render_template('index.html')


# ------ CRUD ------
# READ
@app.route('/productos')
def productos():
    con = conexionBD()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    datos = cursor.fetchall()
    con.close()
    return render_template('productos.html', productos=datos)


# CREATE
@app.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']

        con = conexionBD()
        cursor = con.cursor()
        cursor.execute("INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)",
                       (nombre, precio, stock))
        con.commit()
        con.close()
        return redirect(url_for('productos'))
    return render_template('formulario.html')


# UPDATE
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    con = conexionBD()
    cursor = con.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']
        cursor.execute("UPDATE productos SET nombre=%s, precio=%s, stock=%s WHERE id_producto=%s",
                       (nombre, precio, stock, id))
        con.commit()
        con.close()
        return redirect(url_for('productos'))

    cursor.execute("SELECT * FROM productos WHERE id_producto=%s", (id,))
    producto = cursor.fetchone()
    con.close()
    return render_template('formulario.html', producto=producto)


# DELETE
@app.route('/eliminar/<int:id>')
def eliminar(id):
    con = conexionBD()
    cursor = con.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto=%s", (id,))
    con.commit()
    con.close()
    return redirect(url_for('productos'))


if __name__ == '__main__':
    app.run(debug=True)
