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

@app.route('/home', methods=['GET'])
def home():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)

    # Consulta base con WHERE 1=1 para facilitar los filtros
    query = """
        SELECT 
            e.nombre AS nombre_empleado,
            d.nombre_departamento AS nombre_departamento,
            p.nombre_proyecto AS nombre_proyecto,
            s.salario AS salario,
            t.fecha_asignacion AS fecha_asignacion,
            t.descripcion AS descripcion
        FROM 
            Empleados e
        LEFT JOIN 
            Departamentos d ON e.id_departamento = d.id_departamento
        LEFT JOIN 
            Salarios s ON e.id_empleado = s.id_empleado
        LEFT JOIN 
            Tareas t ON e.id_empleado = t.id_empleado
        LEFT JOIN 
            Proyectos p ON t.id_proyecto = p.id_proyecto
        WHERE 1=1
    """
    filters = []
    args = []

    # Filtros dinámicos
    departamento_id = request.args.get('departamento')
    if departamento_id:
        query += " AND d.id_departamento = %s"
        args.append(departamento_id)

    proyecto_id = request.args.get('proyecto')
    if proyecto_id:
        query += " AND p.id_proyecto = %s"
        args.append(proyecto_id)

    salario_min = request.args.get('salario')
    if salario_min:
        query += " AND s.salario >= %s"
        args.append(salario_min)

    # Ejecutar consulta con filtros
    cursor.execute(query, args)
    resultados = cursor.fetchall()

    # Consultas para los filtros
    cursor.execute("SELECT id_departamento, nombre_departamento FROM Departamentos")
    departamentos = cursor.fetchall()

    cursor.execute("SELECT id_proyecto, nombre_proyecto FROM Proyectos")
    proyectos = cursor.fetchall()

    cursor.close()

    # Renderizar la plantilla con datos
    return render_template(
        'index.html',
        resultados=resultados,
        departamentos=departamentos,
        proyectos=proyectos
    )


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

@app.route('/salarios', methods=['GET', 'POST'])
def salario():
    cursor = db.connection.cursor()

    if request.method == 'POST':
        # Procesar el formulario para agregar un salario
        id_empleado = request.form['id_empleado']
        salario = request.form['salario']
        fecha_pago = request.form['fecha_pago']

        try:
            cursor.execute("""
                INSERT INTO Salarios (id_empleado, salario, fecha_pago)
                VALUES (%s, %s, %s)
            """, (id_empleado, salario, fecha_pago))
            db.connection.commit()
            flash("Salario agregado exitosamente", "success")
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al agregar el salario: {e}", "danger")
        finally:
            cursor.close()

    # Recuperar los empleados para mostrarlos en el combo box
    try:
        cursor.execute("SELECT id_empleado, nombre FROM Empleados")
        empleados = cursor.fetchall()  # Devuelve una lista de tuplas con (id_empleado, nombre)
    except Exception as e:
        flash(f"Error al obtener empleados: {e}", "danger")
        empleados = []  # Si ocurre un error, aseguramos que empleados sea una lista vacía

    # Obtener los salarios con los nombres de los empleados
    try:
        cursor.execute("""
            SELECT Salarios.id_salario, Empleados.nombre, Salarios.salario, Salarios.fecha_pago
            FROM Salarios
            JOIN Empleados ON Salarios.id_empleado = Empleados.id_empleado
        """)
        resultados = cursor.fetchall()  # Devuelve los resultados de los salarios con los nombres de empleados
    except Exception as e:
        flash(f"Error al obtener salarios: {e}", "danger")
        resultados = []  # Si ocurre un error, aseguramos que resultados sea una lista vacía

    salarios = []
    for row in resultados:
        salarios.append({
            'id_salario': row[0],
            'nombre_empleado': row[1],  # El nombre del empleado
            'salario': row[2],
            'fecha_pago': row[3]
        })

    cursor.close()

    return render_template('salarios.html', salarios=salarios, empleados=empleados)


@app.route('/add_salarios', methods=['GET', 'POST'])
def add_salario():
    cursor = db.connection.cursor()

    if request.method == 'POST':
        # Procesar el formulario para agregar un salario
        id_empleado = request.form['id_empleado']
        salario = request.form['salario']
        fecha_pago = request.form['fecha_pago']

        try:
            cursor.execute("""
                INSERT INTO Salarios (id_empleado, salario, fecha_pago)
                VALUES (%s, %s, %s)
            """, (id_empleado, salario, fecha_pago))
            db.connection.commit()
            flash("Salario agregado exitosamente", "success")
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al agregar el salario: {e}", "danger")
        finally:
            cursor.close()
        
        return redirect(url_for('salario'))  # Redirige a la misma página para mostrar los salarios

    else:
        # Si el método es GET, obtenemos los empleados para el formulario
        try:
            cursor.execute("SELECT id_empleado, nombre FROM Empleados")
            empleados = cursor.fetchall()  # Devuelve una lista de tuplas con (id_empleado, nombre)
        except Exception as e:
            flash(f"Error al obtener empleados: {e}", "danger")
            empleados = []  # Si ocurre un error, aseguramos que empleados sea una lista vacía

        # Obtener los salarios para la tabla
        cursor.execute("SELECT * FROM Salarios")
        resultados = cursor.fetchall()  # Devuelve los resultados de los salarios
        salarios = []
        for row in resultados:
            salarios.append({
                'id_salario': row[0], 
                'id_empleado': row[1],
                'salario': row[2],
                'fecha_pago': row[3]
            })
        
        cursor.close()

        return render_template('add_salario.html', empleados=empleados, salarios=salarios)

  
@app.route('/edit_salarios/<int:id>', methods=['GET', 'POST'])
def edit_salarios(id):
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Obtener los datos del salario a editar
    cursor.execute("SELECT * FROM Salarios WHERE id_salario = %s", (id,))
    salarios = cursor.fetchone()
    cursor.close()

    # Si es un POST (cuando el formulario es enviado)
    if request.method == 'POST':
        # Obtener los nuevos valores del formulario
        nuevo_salario = request.form['salario']
        nueva_fecha_pago = request.form['fecha_pago']

        # Actualizar el salario en la base de datos
        cursor = db.connection.cursor()
        try:
            cursor.execute("""
                UPDATE Salarios 
                SET salario = %s, fecha_pago = %s 
                WHERE id_salario = %s
            """, (nuevo_salario, nueva_fecha_pago, id))
            db.connection.commit()
            flash("Salario actualizado exitosamente", "success")
            return redirect('/salarios')  # Redirige a la página de salarios
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al actualizar el salario: {e}", "danger")
        finally:
            cursor.close()

    # Si es un GET, mostramos el formulario de edición con los datos actuales
    return render_template('edit_salarios.html', salarios=salarios)
  
@app.route('/delete_salarios/<int:id>', methods=['GET'])
def delete_salario(id):
    cursor = db.connection.cursor()
    try:
        cursor.execute("DELETE FROM salarios WHERE id_salario = %s", (id,))
        db.connection.commit()
        flash("Salario eliminado exitosamente", "success")
    except Exception as e:
        db.connection.rollback()
        flash(f"Error al eliminar el salario: {e}", "danger")
    finally:
        cursor.close()

    return redirect('/salarios') 

@app.route('/tareas', methods=['GET', 'POST'])
def tareas():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':
        # Capturar los datos del formulario
        descripcion = request.form['descripcion']
        id_empleado = request.form['id_empleado']
        id_proyecto = request.form['id_proyecto']
        fecha_asignacion = request.form['fecha_asignacion']

        try:
            cursor.execute("""
                INSERT INTO Tareas (descripcion, id_empleado, id_proyecto, fecha_asignacion)
                VALUES (%s, %s, %s, %s)
            """, (descripcion, id_empleado, id_proyecto, fecha_asignacion))
            db.connection.commit()
            flash("Tarea agregada exitosamente", "success")
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al agregar tarea: {e}", "danger")
        finally:
            cursor.close()
            return redirect('/tareas')
    
    # Obtener la lista de tareas
    cursor.execute("""
        SELECT 
            t.id_tarea, t.descripcion, t.fecha_asignacion,
            e.nombre AS empleado_nombre, 
            p.nombre_proyecto AS proyecto_nombre
        FROM Tareas t
        JOIN Empleados e ON t.id_empleado = e.id_empleado
        JOIN Proyectos p ON t.id_proyecto = p.id_proyecto
    """)
    tareas = cursor.fetchall()
    
    # Obtener empleados y proyectos para el formulario
    cursor.execute("SELECT id_empleado, nombre FROM Empleados")
    empleados = cursor.fetchall()
    cursor.execute("SELECT id_proyecto, nombre_proyecto FROM Proyectos")
    proyectos = cursor.fetchall()
    
    cursor.close()
    return render_template('tareas.html', tareas=tareas, empleados=empleados, proyectos=proyectos)

@app.route('/edit_tarea/<int:id>', methods=['GET', 'POST'])
def edit_tarea(id):
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Obtener la tarea actual
    cursor.execute("SELECT * FROM Tareas WHERE id_tarea = %s", (id,))
    tarea = cursor.fetchone()
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        nueva_descripcion = request.form['descripcion']
        nuevo_empleado = request.form['id_empleado']
        nuevo_proyecto = request.form['id_proyecto']
        nueva_fecha = request.form['fecha_asignacion']

        try:
            cursor.execute("""
                UPDATE Tareas
                SET descripcion = %s, id_empleado = %s, id_proyecto = %s, fecha_asignacion = %s
                WHERE id_tarea = %s
            """, (nueva_descripcion, nuevo_empleado, nuevo_proyecto, nueva_fecha, id))
            db.connection.commit()
            flash("Tarea actualizada exitosamente", "success")
            return redirect('/tareas')
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al actualizar la tarea: {e}", "danger")
        finally:
            cursor.close()
    
    # Obtener empleados y proyectos para el formulario
    cursor.execute("SELECT id_empleado, nombre FROM Empleados")
    empleados = cursor.fetchall()
    cursor.execute("SELECT id_proyecto, nombre_proyecto FROM Proyectos")
    proyectos = cursor.fetchall()
    
    cursor.close()
    return render_template('edit_tarea.html', tarea=tarea, empleados=empleados, proyectos=proyectos)

@app.route('/delete_tarea/<int:id>', methods=['GET'])
def delete_tarea(id):
    cursor = db.connection.cursor()
    try:
        cursor.execute("DELETE FROM Tareas WHERE id_tarea = %s", (id,))
        db.connection.commit()
        flash("Tarea eliminada exitosamente", "success")
    except Exception as e:
        db.connection.rollback()
        flash(f"Error al eliminar la tarea: {e}", "danger")
    finally:
        cursor.close()
    return redirect('/tareas')



if __name__=='__main__':
  app.config.from_object(config["development"])
  app.run()