from werkzeug.security import check_password_hash

class User():
  def __init__(self, id, nombre, apellido, email, edad, contraseña ) -> None:
    self.id = id
    self.nombre = nombre
    self.apellido = apellido
    self.email = email
    self.edad = edad
    self.contraseña = contraseña
  
  @classmethod
  def check_password(self, hashed_password, password):
    return check_password_hash(hashed_password, password)
  