from flask import Flask, render_template, send_from_directory
import os

# Instanciar la aplicacion
app = Flask(__name__)


# Ruta de la pagina de inicio
@app.route('/', methods = ["GET"])
def inicio():
    # Retornar el html de la pagina de incio
    return render_template('index.html')

# Ruta de la pagina del juego
@app.route('/game', methods = ["GET"])
def game():
    # Retornar html con la pagina del juego
    return render_template('game.html')

# Direccion de archivos estaticos
@app.route('/static/<archivo>', methods = ["Get"])
def css_link(archivo):
    # Se retorna la direccion a la carpeta de archivos estaticos
    return send_from_directory(os.path.join('templates/static'), archivo)


# Iniciar la app
"""
if __name__ == "__main__":
    app.run(debug=True)
"""