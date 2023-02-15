from flask_login import UserMixin

class User (UserMixin):
  def __init__(self, id, email, firstName, LastName, password, role):
    self.id = id
    self.email = email
    self.firstName = firstName
    self.lastName = LastName
    self.password = password
    self.role = role