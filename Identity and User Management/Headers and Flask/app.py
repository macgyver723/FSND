from flask import Flask, request, jsonify, abort
from functools import wraps

app = Flask(__name__)

def get_token_auth_header():
    if 'Authorization' not in request.headers:
        abort(401)
    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')

    if len(header_parts) != 2:
        abort(401)
    elif header_parts[0].lower() != 'bearer':
        abort(401)
    
    auth_token = header_parts[1]
    # print(f'auth_header: {auth_header}')
    # print(f'auth_token: {auth_token}')

    return header_parts[1]

def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        jwt = get_token_auth_header()
        return f(jwt, *args, **kwargs)
    return wrapper

@app.route('/headers')
@requires_auth
def headers(jwt):
    print(jwt)
    return "not implemented (yet)"

@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        'success' : False,
        'error' : 401,
        'message' : "not authorized"
    }), 401