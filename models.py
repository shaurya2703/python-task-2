from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User:
    
    def __init__(self,id,name, email):
        self.id = id
        self.name = name
        self.email = email

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
        }  


class Organisation():
    
    def __init__(self, id,name):
        self.id = id
        self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }      
