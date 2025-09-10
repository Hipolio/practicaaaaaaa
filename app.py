# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade
# pip install -r requirements.txt

from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify, make_response

import mysql.connector
import datetime
import pytz

from flask_cors import CORS, cross_origin

con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_23005116_bd",
    user="u760464709_23005116_usr",
    password="z8[T&05u"
)

app = Flask(__name__)
CORS(app)

# ========================
# FUNCIONES PUSHER
# ========================
def pusherPadrinos():
    import pusher
    pusher_client = pusher.Pusher(
        app_id="2046006",
        key="fd4071018e972df38f9a",
        secret="f54509be4e62f829f280",
        cluster="us2",
        ssl=True
    )
    pusher_client.trigger("hardy-drylands-461", "eventoPadrinos", {"message": "Hola Mundo!"})
    return make_response(jsonify({}))

def pusherCargos():
    import pusher
    pusher_client = pusher.Pusher(
        app_id="2046006",
        key="e57a8ad0a9dc2e83d9a2",
        secret="f54509be4e62f829f280",
        cluster="us2",
        ssl=True
    )
    pusher_client.trigger("canalCargos", "eventoCargos", {"message": "Nuevo cargo"})
    return make_response(jsonify({}))

# ========================
# RUTAS GENERALES
# ========================
@app.route("/")
def index():
    if not con.is_connected():
        con.reconnect()
    con.close()
    return render_template("index.html")

@app.route("/app")
def app2():
    if not con.is_connected():
        con.reconnect()
    con.close()
    return render_template("login.html")

@app.route("/iniciarSesion", methods=["POST"])
def iniciarSesion():
    if not con.is_connected():
        con.reconnect()

    usuario    = request.form["txtUsuario"]
    contrasena = request.form["txtContrasena"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Usuario
    FROM usuarios
    WHERE Nombre_Usuario = %s
    AND Contrasena = %s
    """
    val    = (usuario, contrasena)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

# ========================
# RUTAS PADRINOS
# ========================
@app.route("/padrinos")
def padrinos():
    return render_template("padrinos.html")

@app.route("/tbodyPadrinos")
def tbodyPadrinos():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idPadrino, nombrePadrino, sexo, telefono, correoElectronico
    FROM padrinos
    ORDER BY idPadrino DESC
    LIMIT 10 OFFSET 0
    """
    cursor.execute(sql)
    registros = cursor.fetchall()
    return render_template("tbodyPadrinos.html", padrinos=registros)

@app.route("/padrino", methods=["POST"])
def guardarPadrinos():
    if not con.is_connected():
        con.reconnect()

    idPadrino          = request.form["idPadrino"]
    nombrePadrino      = request.form["nombrePadrino"]
    sexo               = request.form["sexo"]
    telefono           = request.form["telefono"]
    correoElectronico  = request.form["correoElectronico"]
    
    cursor = con.cursor()
    if idPadrino:
        sql = """
        UPDATE padrinos
        SET nombrePadrino = %s, sexo = %s, telefono = %s, correoElectronico = %s
        WHERE idPadrino = %s
        """
        val = (nombrePadrino, sexo, telefono, correoElectronico, idPadrino)
    else:
        sql = """
        INSERT INTO padrinos (nombrePadrino, sexo, telefono, correoElectronico)
        VALUES (%s, %s, %s, %s)
        """
        val = (nombrePadrino, sexo, telefono, correoElectronico)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()
    pusherPadrinos()
    return make_response(jsonify({}))

@app.route("/padrino/eliminar", methods=["POST"])
def eliminarPadrino():
    if not con.is_connected():
        con.reconnect()
    idPadrino = request.form["idPadrino"]
    cursor = con.cursor()
    sql    = "DELETE FROM padrinos WHERE idPadrino = %s"
    cursor.execute(sql, (idPadrino,))
    con.commit()
    con.close()
    return make_response(jsonify({}))

# ========================
# RUTAS CARGOS
# ========================
@app.route("/cargos")
def cargos():
    return render_template("cargos.html")

@app.route("/tbodyCargos")
def tbodyCargos():
    if not con.is_connected():
        con.reconnect()
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idCargos, descripcion, monto, fecha, idMascotas
    FROM cargos
    ORDER BY idCargos DESC
    LIMIT 10 OFFSET 0
    """
    cursor.execute(sql)
    registros = cursor.fetchall()
    return render_template("tbodyCargos.html", cargos=registros)

@app.route("/cargos", methods=["POST"])
def guardarCargo():
    if not con.is_connected():
        con.reconnect()

    idCargos    = request.form["idCargos"]
    descripcion = request.form["descripcion"]
    monto       = request.form["monto"]
    fecha       = request.form["fecha"]
    idMascotas  = request.form["idMascotas"]

    cursor = con.cursor()
    if idCargos:
        sql = """
        UPDATE cargos
        SET descripcion = %s, monto = %s, fecha = %s, idMascotas = %s
        WHERE idCargos = %s
        """
        val = (descripcion, monto, fecha, idMascotas, idCargos)
    else:
        sql = """
        INSERT INTO cargos (descripcion, monto, fecha, idMascotas)
        VALUES (%s, %s, %s, %s)
        """
        val = (descripcion, monto, fecha, idMascotas)

    cursor.execute(sql, val)
    con.commit()
    con.close()
    pusherCargos()
    return make_response(jsonify({}))

@app.route("/cargos/eliminar", methods=["POST"])
def eliminarCargo():
    if not con.is_connected():
        con.reconnect()
    idCargo = request.form["idCargos"]
    cursor = con.cursor()
    sql    = "DELETE FROM cargos WHERE idCargos = %s"
    cursor.execute(sql, (idCargo,))
    con.commit()
    con.close()
    return make_response(jsonify({}))


