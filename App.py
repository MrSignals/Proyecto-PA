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
  return render_template("login.html")

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

@app.route('/empleados', methods=['GET'])
def empleados():
    cursor = db.connection.cursor()  # Usa un cursor estándar
    cursor.execute("""
        SELECT e.id_empleado, e.nombre, e.apellido, e.correo, e.telefono, d.nombre_departamento 
        FROM Empleados e 
        INNER JOIN Departamentos d ON e.id_departamento = d.id_departamento
    """)
    resultados = cursor.fetchall()  # Devuelve los resultados como una lista de tuplas
    cursor.close()

    empleados = []
    for row in resultados:
        empleados.append({
            'id_empleado': row[0],
            'nombre': row[1],
            'apellido': row[2],
            'correo': row[3],
            'telefono': row[4],
            'departamento': row[5],
        })

    return render_template('empleados.html', empleados=empleados)

@app.route('/add_empleado', methods=['GET', 'POST'])
def add_empleado():
    cursor = db.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        telefono = request.form['telefono']
        id_departamento = request.form['id_departamento']

        try:
            cursor.execute("""
                INSERT INTO Empleados (nombre, apellido, correo, telefono, id_departamento)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, apellido, correo, telefono, id_departamento))
            db.connection.commit()
            flash("Empleado agregado exitosamente", "success")
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al agregar el empleado: {e}", "danger")
        finally:
            cursor.close()
        return redirect(url_for('empleados'))
    
    # Si el método es GET, obtenemos los departamentos para el formulario
    cursor.execute("SELECT id_departamento, nombre_departamento FROM Departamentos")
    departamentos = cursor.fetchall()
    cursor.close()
    return render_template('add_empleado.html', departamentos=departamentos)

@app.route('/edit_empleado/<int:id>', methods=['GET', 'POST'])
def edit_empleado(id):
    cursor = db.connection.cursor()

    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        telefono = request.form['telefono']
        id_departamento = request.form['id_departamento']

        try:
            cursor.execute("""
                UPDATE Empleados 
                SET nombre=%s, apellido=%s, correo=%s, telefono=%s, id_departamento=%s 
                WHERE id_empleado=%s
            """, (nombre, apellido, correo, telefono, id_departamento, id))
            db.connection.commit()
            flash("Empleado actualizado exitosamente", "success")
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al actualizar el empleado: {e}", "danger")
        finally:
            cursor.close()
        return redirect(url_for('empleados'))

    # Si es una solicitud GET, obtenemos los datos actuales del empleado
    cursor.execute("SELECT * FROM Empleados WHERE id_empleado = %s", (id,))
    empleado = cursor.fetchone()

    # Obtener los departamentos para la selección
    cursor.execute("SELECT id_departamento, nombre_departamento FROM Departamentos")
    departamentos = cursor.fetchall()
    cursor.close()

    if not empleado:
        flash("Empleado no encontrado", "warning")
        return redirect(url_for('empleados'))

    return render_template('edit_empleado.html', empleado=empleado, departamentos=departamentos)

@app.route('/delete_empleado/<int:id>', methods=['GET','POST'])
def delete_empleado(id):
    cursor = db.connection.cursor()
    try:
        # Eliminar empleado por su ID
        cursor.execute("DELETE FROM Empleados WHERE id_empleado = %s", (id,))
        db.connection.commit()
        flash("Empleado eliminado exitosamente", "success")
    except Exception as e:
        db.connection.rollback()
        flash(f"Error al eliminar el empleado: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('empleados'))
 
 
@app.route('/proyectos', methods=['GET'])
def proyectos():
    cursor = db.connection.cursor()  # Usa un cursor estándar
    cursor.execute("SELECT * FROM proyectos")
    resultados = cursor.fetchall()  # Devuelve los resultados como una lista de tuplas
    cursor.close()

    proyectos = []
    for row in resultados:
        proyectos.append({
            'id_proyecto': row[0], 
            'nombre_proyecto': row[1],
            'fecha_inicio' : row[2]
        })
    
    return render_template('proyectos.html', proyectos=proyectos)


@app.route('/add_proyectos', methods=['POST'])
def add_proyecto():
    nombre_proyecto = request.form['nombre_proyecto']
    fecha_inicio = request.form['fecha_inicio']

    cursor = db.connection.cursor()  # Usamos db.connection para crear el cursor
    try:
        cursor.execute("INSERT INTO proyectos (nombre_proyecto, fecha_inicio) VALUES (%s, %s)", (nombre_proyecto, fecha_inicio))

        db.connection.commit()  # Usamos db.connection.commit() en lugar de db.commit()
        flash("Proyecto agregado exitosamente", "success")
    except Exception as e:
        db.connection.rollback()  # Usamos db.connection.rollback() en lugar de db.rollback()
        flash(f"Error al agregar el proyecto: {e}", "danger")
    finally:
        cursor.close()
    return redirect('/proyectos')
  
@app.route('/edit_proyectos/<int:id>', methods=['GET', 'POST'])
def edit_proyectos(id):
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM proyectos WHERE id_proyecto = %s", (id,))
    proyectos = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre_proyecto']
        nueva_fecha = request.form['fecha_inicio']
        cursor = db.connection.cursor()
        try:
            cursor.execute("UPDATE proyectos SET nombre_proyecto = %s, fecha_inicio = %s WHERE id_proyecto = %s", (nuevo_nombre, nueva_fecha, id, ))
            db.connection.commit()
            flash("Proyecto actualizado exitosamente", "success")
            return redirect('/proyectos')
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al actualizar el proyecto: {e}", "danger")
        finally:
            cursor.close()
    
    return render_template('edit_proyectos.html', proyectos=proyectos)
  
@app.route('/delete_proyecto/<int:id>', methods=['GET'])
def delete_proyecto(id):
    cursor = db.connection.cursor()
    try:
        cursor.execute("DELETE FROM proyectos WHERE id_proyecto = %s", (id,))
        db.connection.commit()
        flash("Proyecto eliminado exitosamente", "success")
    except Exception as e:
        db.connection.rollback()
        flash(f"Error al eliminar el proyecto: {e}", "danger")
    finally:
        cursor.close()

    return redirect('/proyectos')

if __name__=='__main__':
  app.config.from_object(config["development"])
  app.run()