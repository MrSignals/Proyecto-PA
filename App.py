import os
from flask import Flask, jsonify
from flask import render_template, request,redirect, url_for
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config['ENV'] = 'development'  # Establecer el entorno de desarrollo
app.config['DEBUG'] = True  # Activar el modo de depuración

def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return connection

@app.route('/')
def index():
  return redirect(url_for('login'))

@app.route('/login')
def login():
  if request.method == ['GET', 'POST']:
    print(request.form['correo'])
    print(request.form['password'])
  else:
    return render_template('login.html')

@app.route('/users', methods=['GET'])
def get_users():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # dictionary=True para obtener un dict en lugar de una tupla
    cursor.execute("SELECT * FROM categoria")  # Cambia 'usuarios' por el nombre de tu tabla
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(result)

if __name__=='__main__':
  app.run(debug=True)