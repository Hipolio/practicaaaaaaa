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
    # return "<h5>Hola, soy la view app</h5>"

@app.route("/iniciarSesion", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
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

@app.route("/padrinos")
def padrinos():
    return render_template("padrinos.html")

@app.route("/tbodyPadrinos")
def tbodyPadrinos():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idPadrino,
           nombrePadrino,
           sexo,
           telefono,
           correoElectronico

    FROM padrinos

    ORDER BY idPadrino DESC

    LIMIT 10 OFFSET 0
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    # Si manejas fechas y horas
    """
    for registro in registros:
        fecha_hora = registro["Fecha_Hora"]

        registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
        registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
    """

    return render_template("tbodyPadrinos.html", padrinos=registros)

@app.route("/productos/ingredientes/<int:idPadrino>")
def productosIngredientes(idPadrino):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT productos.Nombre_Producto, ingredientes.*, productos_ingredientes.Cantidad FROM productos_ingredientes
    INNER JOIN productos ON productos.Id_Producto = productos_ingredientes.Id_Producto
    INNER JOIN ingredientes ON ingredientes.Id_Ingrediente = productos_ingredientes.Id_Ingrediente
    WHERE productos_ingredientes.Id_Producto = %s
    ORDER BY productos.Nombre_Producto
    """

    cursor.execute(sql, (idPadrino, ))
    registros = cursor.fetchall()

    return render_template("modal.html", productosIngredientes=registros)

@app.route("/padrinos/buscar", methods=["GET"])
def buscarPadrinos():
    if not con.is_connected():
        con.reconnect()

    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"
    
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idPadrino,
           nombrePadrino,
           sexo,
           telefono,
           correoElectronico

    FROM padrinos

    WHERE nombrePadrino LIKE %s
    OR    telefono          LIKE %s
    OR    correoElectronico     LIKE %s

    ORDER BY idPadrino DESC
    
    LIMIT 10 OFFSET 0
    """
    val    = (busqueda, busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()

        # Si manejas fechas y horas
        """
        for registro in registros:
            fecha_hora = registro["Fecha_Hora"]

            registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
            registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
            registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
        """

    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        registros = []

    finally:
        con.close()

    return make_response(jsonify(registros))

@app.route("/padrino", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def guardarPadrinos():
    if not con.is_connected():
        con.reconnect()

    idPadrino          = request.form["idPadrino"]
    nombrePadrino      = request.form["nombrePadrino"]
    sexo               = request.form["sexo"]
    telefono           = request.form["telefono"]
    correoElectronico  = request.form["correoElectronico"]
    # fechahora   = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    
    cursor = con.cursor()

    if idPadrino:
        sql = """
        UPDATE padrinos

        SET nombrePadrino     = %s,
            sexo              = %s,
            telefono          = %s,
            correoElectronico = %s

        WHERE idPadrino = %s
        """
        val = (nombrePadrino, sexo, telefono, correoElectronico, idPadrino)
    else:
        sql = """
        INSERT INTO padrinos (nombrePadrino, sexo, telefono, correoElectronico)
                    VALUES    (%s,          %s,      %s,    %s)
        """
        val =                 (nombrePadrino, sexo, telefono, correoElectronico)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    pusherPadrinos()
    
    return make_response(jsonify({}))

@app.route("/padrino/<int:idPadrino>")
def editarPadrino(idPadrino):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idPadrino, nombrePadrino, sexo, telefono, correoElectronico

    FROM padrinos

    WHERE idPadrino = %s
    """
    val    = (idPadrino,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/padrino/eliminar", methods=["POST"])
def eliminarPadrino():
    if not con.is_connected():
        con.reconnect()

    idPadrino = request.form["idPadrino"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    DELETE FROM padrinos
    WHERE idPadrino = %s
    """
    val    = (idPadrino,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))
