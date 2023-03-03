from flask_login import UserMixin

class User (UserMixin):
  def __init__(self, id, email, firstName, LastName, password, role, DateBirth, PlaceBirth, CountryCodeP, PhoneNumber, PostalAddress):
    self.id = email
    self.email = email
    self.firstName = firstName
    self.lastName = LastName
    self.password = password
    self.role = role
    self.tid = id
    self.DateBirth = DateBirth
    self.PlaceBirth = PlaceBirth
    self.CountryCodeP = CountryCodeP
    self.PhoneNumber = PhoneNumber
    self.PostalAddress = PostalAddress
