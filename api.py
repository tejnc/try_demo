import os
import jwt
import time
import datetime
from dotenv import load_dotenv
from logging import currentframe
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from pymongo import mongo_client
from pymongo.message import query
from utils.user import get_user_by_id
from flask import Flask, json, jsonify, request
from mongonator import MongoClientWithPagination, ASCENDING
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
#TODO: properly write the docstrings for every functions.
#TODO: create registration checking system for email address
#TODO: create login system for logging in with tokens 
#TODO: properly manage the token response for protected api

load_dotenv()


app.config['SECRET_KEY']= os.environ['SECRET_KEY']
app.config['MONGO_URI'] = os.environ['URI']
mongo = PyMongo(app)
db_operations = mongo.db.demo

mongo_client = MongoClientWithPagination(os.environ['URI'])
db =mongo_client['demo_db']
col = db['demo']

@app.route('/register',methods=['POST'])
def register_user():
    """
       Users information are added.
    """
    address = dict()
    _json = request.json
    _name = _json['name']
    address['province'] = _json['province']
    address['district'] = _json['district']
    address['town'] = _json['town']
    _gender = _json['gender']
    _email = _json['email']
    _password = _json['password']

    if _name and _email and _password and address and _gender and request.method=='POST':
        _hashed_password = generate_password_hash(_password)
        id = db_operations.insert({'name':_name,'address': address,'email':_email,'password':_hashed_password})
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
    current_time = time.time()
    exp_time = get_user_by_id(request.headers)['exp']
    query_filter = {'name':{'$ne':None}}

    if exp_time > current_time:
        # users = db_operations.find()
        # resp = dumps(users)
        # return resp
        for d in col.paginate(query=query_filter, limit=5, projection={'name':1,'email':1,'address':1,'gender':1},ordering_field='name', ordering=ASCENDING):
            users = dumps(d.response)
            return users

    else:
        return jsonify("token expired")


@app.route('/user',methods=["GET"])
def user():
    """ It helps to find the user."""
    # _name = str(name).capitalize()
    # user = db_operations.find_one({'name':_name})
    # resp = dumps(user)
    # return resp

    get_user_by_id(request.headers)
    


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
    _password = _json['password']

    if _id and _name and _email and _password and request.method=="PUT":
        _hashed_password = generate_password_hash(_password)       
        db_operations.update_one({'_id':ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)},{'$set': {'name':_name,'email':_email,'pwd':_hashed_password}})
        resp = jsonify('User updated successfully.')
        resp.status_code = 200
        return resp


@app.route('/login', methods=['POST'])
def login():
    """
        User login
    """
    _json = request.json
    _email = _json['email']
    _password = _json['password']

    login_user = db_operations.find_one({'email':_email})
    print(login_user['_id'],type(login_user['_id']))

    if login_user:
        if check_password_hash(login_user['password'],_password):
            """checking password and implementing jwt tokens """

            token = jwt.encode({'id':str(login_user['_id']), 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)} , app.config['SECRET_KEY'])
            resp = jsonify(
                {
                    'message':"User logged in successfully.",
                    'token': token
                }
                        )
            resp.status_code = 200
            return resp
        
        else:
            resp = jsonify("Password incorrect!")
            return resp

    else:
        resp = jsonify("User not found!")
        return resp


@app.route('/logout')
def logout():
    pass


if __name__ == "__main__":
    app.run(debug=True)

