from .entities.User import User

class ModelUser():
  
  @classmethod
  def login(self, db, user):
    try:
      cursor= db.connection.cursor()
      sql = """SELECT id_Usuario, nombre, apellido, email, edad, contraseña from Usuarios
                  WHERE email = '{}'""".format(user.email)
      cursor.execute(sql)
      row = cursor.fetchone()
      if row != None:
        user = User(row[0], row[1], row[2], row[3], row[4], User.check_password(row[5], user.contraseña))
        return user
      else: 
        return None
    except Exception as ex:
      raise(Exception(ex))
    
  @classmethod
  def get_by_id(self, db, id):
    try:
      cursor= db.connection.cursor()
      sql = """SELECT id_Usuario, nombre, apellido, email, edad from Usuarios
                  WHERE id_Usuario = '{}'""".format(id)
      cursor.execute(sql)
      row = cursor.fetchone()
      if row != None:
        return User(row[0], row[1], row[2], row[3], row[4], None)
      else: 
        return None
    except Exception as ex:
      raise(Exception(ex))