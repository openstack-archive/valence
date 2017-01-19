import uuid

from functools import wraps

from flask import request
from flask import Response
from flask_restful import Resource


def generate_members(element_name, url, total_num):
    members = []
    i = 0
    while i < total_num:
        dic = dict()
        dic["@odata.id"] = url + element_name + str(i + 1)
        members.append(dic)
        i += 1
    return members


def generate_uuid_by_element_id(element_id):
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, element_id))


def check_auth(username, password):
    """check if a username password combination is valid"""
    return username == 'admin' and password == 'Passw0rd'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials',
        401,
        {
            'WWW-Authenticate': 'Basic realm="Login Required"'
        }
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


class AuthResource(Resource):
    method_decorators = [requires_auth]
