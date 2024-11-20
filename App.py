from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from config import config
from flask_mysqldb import MySQL, MySQLdb
from flask_login import LoginManager, login_user, logout_user, login_required

#Models
from models.ModelUser import ModelUser

#Entities
from models.entities.User import User

app = Flask(__name__)
db=MySQL(app)
login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
  return ModelUser.get_by_id(db, id)


@app.route('/')
def index():
  return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    user = User(0, 0,0, request.form['correo'],0, request.form["password"])
    logged_user = ModelUser.login(db, user)
    if logged_user != None:
      if logged_user.contraseña:
        login_user(logged_user)
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
  return render_template("index.html")

@app.route('/departamentos', methods=['GET'])
def departamentos():
    cursor = db.connection.cursor()  # Usa un cursor estándar
    cursor.execute("SELECT * FROM Departamentos")
    resultados = cursor.fetchall()  # Devuelve los resultados como una lista de tuplas
    cursor.close()

    departamentos = []
    for row in resultados:
        departamentos.append({
            'id_departamento': row[0], 
            'nombre_departamento': row[1]
        })
    
    return render_template('departamentos.html', departamentos=departamentos)


@app.route('/add_departamento', methods=['POST'])
def add_departamento():
    nombre_departamento = request.form['nombre_departamento']
    cursor = db.connection.cursor()  # Usamos db.connection para crear el cursor
    try:
        cursor.execute("INSERT INTO Departamentos (nombre_departamento) VALUES (%s)", (nombre_departamento,))
        db.connection.commit()  # Usamos db.connection.commit() en lugar de db.commit()
        flash("Departamento agregado exitosamente", "success")
    except Exception as e:
        db.connection.rollback()  # Usamos db.connection.rollback() en lugar de db.rollback()
        flash(f"Error al agregar el departamento: {e}", "danger")
    finally:
        cursor.close()
    return redirect('/departamentos')
  
@app.route('/edit_departamento/<int:id>', methods=['GET', 'POST'])
def edit_departamento(id):
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Departamentos WHERE id_departamento = %s", (id,))
    departamento = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre_departamento']
        cursor = db.connection.cursor()
        try:
            cursor.execute("UPDATE Departamentos SET nombre_departamento = %s WHERE id_departamento = %s", (nuevo_nombre, id))
            db.connection.commit()
            flash("Departamento actualizado exitosamente", "success")
            return redirect('/departamentos')
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al actualizar el departamento: {e}", "danger")
        finally:
            cursor.close()
    
    return render_template('edit_departamento.html', departamento=departamento)
  
@app.route('/delete_departamento/<int:id>', methods=['GET'])
def delete_departamento(id):
    cursor = db.connection.cursor()
    try:
        cursor.execute("DELETE FROM Departamentos WHERE id_departamento = %s", (id,))
        db.connection.commit()
        flash("Departamento eliminado exitosamente", "success")
    except Exception as e:
        db.connection.rollback()
        flash(f"Error al eliminar el departamento: {e}", "danger")
    finally:
        cursor.close()

    return redirect('/departamentos')


if __name__=='__main__':
  app.config.from_object(config["development"])
  app.run()