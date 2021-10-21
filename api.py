from flask import Flask, json, jsonify, request

from flask_pymongo import PyMongo

from bson.json_util import dumps

from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb+srv://test:test@cluster0.x25kn.mongodb.net/demo_db?retryWrites=true&w=majority'
mongo = PyMongo(app)
db_operations = mongo.db.demo

@app.route('/add',methods=['POST'])
def add_user():
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

if __name__ == "__main__":
    app.run(debug=True)