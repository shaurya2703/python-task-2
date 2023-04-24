from flask import Flask, request, jsonify
from models import db,User, Organisation, OrganisationUser
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
app.config['SECRET_KEY'] = "random string"

client = MongoClient('localhost',27017)
db = client['user_management_app']
users = db['users']
organisations = db['organisations']
users_organisations = db['users_organisations']



@app.route("/hello")
def hello():
    return "Hello"

@app.route('/users', methods=['POST'])
def add_user():
    name = request.json['name']
    email = request.json['email']
    user_id = request.json['id'] if 'id' in request.json else ObjectId()
    new_user = User(id=user_id,name=name,email=email)

    result = users.insert_one(new_user.to_dict())

    return f"Added user with ID: {result.inserted_id}"

@app.route("/list_users",methods=['GET'])
def list_users():
    name_filter = request.args.get('name')
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)

    query = {}
    if name_filter:
        query['name'] = {'$regex': f'{name_filter}.*', '$options': 'i'}

    # Get total count of records
    total_count = users.count_documents(query)

    # Perform pagination
    cursor = users.find(query).skip(offset).limit(limit)

    # Build response
    user_list = [user for user in cursor]
    for user in user_list:
        user['_id'] = str(user['_id']) # Convert ObjectId to string
        user['id'] = str(user['id'])
    response = {'users': user_list, 'total_count': total_count}
    return jsonify(response)

@app.route('/users/<string:name>')
def get_user(name):
    print(name)
    # Find user by name
    user = users.find_one({'name': name})

    # If user not found, return 404
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    # Convert ObjectId to string
    user['_id'] = str(user['_id'])
    user['id'] = str(user['id'])

    # Return user as JSON response
    return jsonify(user)

@app.route("/organisations",methods=['POST'])
def add_organisation():
    name = request.json['name']

    org_id = request.json['id'] if 'id' in request.json else ObjectId()
    new_org = Organisation(id=org_id,name=name)

    result = organisations.insert_one(new_org.to_dict())

    return f"Added organisation with ID: {result.inserted_id}"

    

@app.route("/list_organisations",methods=['GET'])
def list_organisations():
    name_filter = request.args.get('name')
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)

    query = {}
    if name_filter:
        query['name'] = {'$regex': f'{name_filter}.*', '$options': 'i'}

    # Get total count of records
    total_count = organisations.count_documents(query)

    # Perform pagination
    cursor = organisations.find(query).skip(offset).limit(limit)

    # Build response
    org_list = [org for org in cursor]
    for org in org_list:
        org['_id'] = str(org['_id']) # Convert ObjectId to string
        org['id'] = str(org['id'])
    response = {'organisations': org_list, 'total_count': total_count}
    return jsonify(response)

@app.route('/organisations/<string:name>')
def get_organisation(name):
    print(name)
    org = organisations.find_one({'name':name})
    if org is None:
        return jsonify({'message': 'Organisation not found'}), 404

    org['_id'] = str(org['_id'])
    org['id'] = str(org['id'])

    return jsonify(org)


@app.route('/permissions', methods=['POST'])
def update_org_permissions():
    user_id = request.json['user_id']
    org_permissions = request.json['org_permissions']

    # Update permissions for each organization
    for org_permission in org_permissions:
        # Get organization ID and access level from organization permission object
        org_id = org_permission.get('org_id')
        access_level = org_permission.get('access_level')

        # Check if organization exists in database
        organisation = organisations.find_one({'_id': ObjectId(org_id)})
        if organisation is None:
            return jsonify({'error': 'Organization not found'}), 404

        # Check if user exists in database
        user = users.find_one({'_id': ObjectId(user_id)})
        if user is None:
            return jsonify({'error': 'User not found'}), 404

        # Update user's permissions for organization in users_organisations collection
        users_organisations.update_one(
            {'user_id': ObjectId(user_id), 'org_id': ObjectId(org_id)},
            {'$set': {'access_level': access_level}},
            upsert=True)

    return jsonify({'success': 'Permissions updated successfully'}), 200

@app.route('/organisations/<int:org_id>/users/<int:user_id>', methods=['DELETE'])
def remove_user_permission(org_id, user_id):
    organisation = organisations.find_one({'id':org_id})
    org_json = jsonify(organisation)
    user = users.find_one({'id':user_id})
    user_json = jsonify(user)
    if organisation and user:
        user_org = users_organisations.find_one({'user_id':user_id, 'org_id':org_id})
        if user_org:
            users_organisations.delete_one({'_id':user_org['_id']})
            return jsonify({'message': f'User {user_json} has been removed from organization {org_json}.'}), 200
        else:
            return jsonify({'error': 'User does not have access to this organization.'}), 404
    else:
        return jsonify({'error': 'Organization or user not found.'}), 404


if __name__ == "__main__":
    with app.app_context():
        # db.create_all()
        app.run(debug=True,port=8000)