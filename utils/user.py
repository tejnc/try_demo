import os
import jwt
def get_user_by_id(headers):
    token = headers['Authorization'][7:]
    decoded_token = jwt.decode(token, os.environ['SECRET_KEY'],algorithms=["HS256"])   
    return decoded_token