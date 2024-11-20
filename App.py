from flask import Flask
from flask import render_template, request,redirect, url_for, flash
from config import config
from flask_mysqldb import MySQL

#Models
from models.ModelUser import ModelUser

#Entities
from models.entities.User import User

app = Flask(__name__)
db=MySQL(app)


@app.route('/')
def index():
  return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    user = User(0, 0,0, request.form['correo'],0, request.form["password"])
    logged_user = ModelUser.login(db, user)
    if logged_user != None:
      if logged_user.contraseña:
        return redirect(url_for("home"))
      else:
        flash("Contraseña incorrecta")
        return render_template("login.html")
    else:
      flash("Usuario no encontrado")
      return render_template("login.html")
  else:
    return render_template('login.html')

@app.route("/home")
def home():
  return render_template("salarios.html")


if __name__=='__main__':
  app.config.from_object(config["development"])
  app.run()