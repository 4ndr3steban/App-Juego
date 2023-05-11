from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)


@app.route('/', methods = ["GET"])
def inicio():
    return render_template('index.html')


@app.route('/game', methods = ["GET"])
def game():
    return render_template('game.html')


@app.route('/static/<archivo>', methods = ["Get"])
def css_link(archivo):
    # Se retorna la direccion a la carpeta de archivos estaticos
    return send_from_directory(os.path.join('templates/static'), archivo)


if __name__ == "__main__":
    app.run(debug=True)