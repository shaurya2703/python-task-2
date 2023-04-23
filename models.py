from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

def serialize_user(user):
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email
        }              


class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

def serialize_organisation(organisation):
    return {
        'id':organisation.id,
        'name':organisation.name
    }

class OrganisationUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    org_id = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    access_level = db.Column(db.Enum('READ', 'WRITE', 'ADMIN'), nullable=False)

    user = db.relationship(User, backref=db.backref('user_organisations', cascade='all, delete-orphan'))
    organisation = db.relationship(Organisation, backref=db.backref('user_organisations', cascade='all, delete-orphan'))

    def __init__(self, user_id, org_id, access_level):
        self.user_id = user_id
        self.org_id = org_id
        self.access_level = access_level