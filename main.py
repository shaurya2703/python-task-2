from flask import Flask, request, jsonify
from models import db,User, Organisation, OrganisationUser, serialize_organisation, serialize_user
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
app.config['SECRET_KEY'] = "random string"
db.init_app(app)
mongo = PyMongo(app)



@app.route("/hello")
def hello():
    return "Hello"

@app.route('/users', methods=['POST'])
def add_user():
    name = request.json['name']
    email = request.json['email']
    new_user = User(name=name,email=email)
    if 'id' in request.json:
        id = request.json['id']
        new_user.id = id

    db.session.add(new_user)
    db.session.commit()

    return jsonify(serialize_user(user=new_user))

@app.route("/list_users",methods=['GET'])
def list_users():
    name_filter = request.args.get('name')
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)

    query = User.query
    if name_filter:
        query = query.filter(User.name.like(f'%{name_filter}%'))

    users = query.offset(offset).limit(limit).all()
    total_count = query.count()

    response = {
        'users': [ serialize_user(user) for user in users],
        'total_count': total_count
    }

    return jsonify(response)

@app.route('/users/<string:name>')
def get_user(name):
    print(name)
    user = User.query.filter_by(name=name).first()
    if user is None:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    })

@app.route("/organisations",methods=['POST'])
def add_organisation():
    name = request.json['name']

    new_org = Organisation(name)

    db.session.add(new_org)
    db.session.commit()

    return jsonify(serialize_organisation(new_org))

@app.route("/list_organisations",methods=['GET'])
def list_organisations():
    name_filter = request.args.get('name')
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)

    query = Organisation.query
    if name_filter:
        query = query.filter(Organisation.name.like(f'%{name_filter}%'))

    organisations = query.offset(offset).limit(limit).all()
    total_count = query.count()

    response = {
        'users': [ serialize_organisation(organisation) for organisation in organisations],
        'total_count': total_count
    }

    return jsonify(response)

@app.route('/organisations/<string:name>')
def get_organisation(name):
    print(name)
    org = Organisation.query.filter_by(name=name).first()
    if org is None:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(serialize_organisation(org))


@app.route('/organisations/<int:org_id>/permissions', methods=['POST'])
def update_org_permissions(org_id):
    data = request.json
    users = data.get('users', [])
    access_level = data.get('access_level')

    org = Organisation.query.get_or_404(org_id)

    for user_id in users:
        user_org = OrganisationUser.query.filter_by(user_id=user_id, org_id=org.id).first()
        if user_org:
            user_org.access_level = access_level
        else:
            user_org = OrganisationUser(user_id=user_id, org_id=org.id, access_level=access_level)
            db.session.add(user_org)

    db.session.commit()

    return jsonify({'message': 'Permissions updated successfully'}), 200

@app.route('/organisations/<int:org_id>/users/<int:user_id>', methods=['DELETE'])
def remove_user_permission(org_id, user_id):
    organisation = Organisation.query.get(org_id)
    user = User.query.get(user_id)
    if organisation and user:
        user_org = OrganisationUser.query.filter_by(user_id=user_id, org_id=org_id).first()
        if user_org:
            db.session.delete(user_org)
            db.session.commit()
            return jsonify({'message': f'User {user.name} has been removed from organization {organisation.name}.'}), 200
        else:
            return jsonify({'error': 'User does not have access to this organization.'}), 404
    else:
        return jsonify({'error': 'Organization or user not found.'}), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True,port=8000)