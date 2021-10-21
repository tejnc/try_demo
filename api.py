from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import Flask, json, jsonify, request
from werkzeug.security import generate_password_hash

app = Flask(__name__)
#TODO: properly write the docstrings for every functions.


app.config['MONGO_URI'] = 'mongodb+srv://test:test@cluster0.x25kn.mongodb.net/demo_db?retryWrites=true&w=majority'
mongo = PyMongo(app)
db_operations = mongo.db.demo

@app.route('/add',methods=['POST'])
def add_user():
    """
       Users information are added.
    """
    _json = request.json
    _name = _json['name']
    _email = _json['email']
    _password = _json['pwd']

    if _name and _email and _password and request.method=='POST':

        _hashed_password = generate_password_hash(_password)

        id = db_operations.insert({'name':_name,'email':_email,'pwd':_hashed_password})

        resp = jsonify('User added successfully.')

        resp.status_code = 200

        return resp
    
    else:
        return not_found()

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status':404,
        'message': 'Not found' + request.url
    }

    resp = jsonify(message)

    resp.status_code = 404

    return resp

@app.route('/users')
def users():
    """ Show the list of users. """
    users = db_operations.find()
    resp = dumps(users)
    return resp

@app.route('/user/<id>')
def user(id):
    """ It helps to find the user."""

    user = db_operations.find_one({'_id':ObjectId(id)})
    resp = dumps(user)
    return resp

@app.route('/delete/<id>',methods=['DELETE'])
def delete_user(id):
    """ Deleting the user with id(passed)."""
    db_operations.delete_one({'_id':ObjectId(id)})
    resp = jsonify("Users deleted successfully.")

    resp.status_code = 200

    return resp

@app.route('/update/<id>',methods=['PUT'])
def update_user(id):
    """Updating the user with the passed id."""

    _id = id
    _json = request.json
    _name = _json['name']
    _email = _json['email']
    _password = _json['pwd']

    if _id and _name and _email and _password and request.method=="PUT":
        _hashed_password = generate_password_hash(_password)
        
        db_operations.update_one({'_id':ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},{'$set': {'name':_name,'email':_email,'pwd':_hashed_password}})

        resp = jsonify('User updated successfully.')

        resp.status_code = 200

        return resp

if __name__ == "__main__":
    app.run(debug=True)