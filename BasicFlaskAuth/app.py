from flask import Flask, request, abort, jsonify, redirect
import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen

import pprint

pp = pprint.PrettyPrinter(indent=4)

app = Flask(__name__)

AUTH0_DOMAIN = 'fsnd-stefan.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'image'
CLIENT_ID = 'QEpJRy31MOBtlbbsqsEUOV5GWnFjk9y9'
CALLBACK_URL = 'http://localhost:8080/login-results'

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not incluced in JWT'
        }, 400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found'
        }, 403)
    return True

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                raise AuthError({
                'code': 'unauthorized',
                'description': 'Could not process token'
            }, 401)
                # abort(401)
            
            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator

# url to login to auth0
# https://fsnd-stefan.auth0.com/authorize?audience=image&response_type=token&client_id=QEpJRy31MOBtlbbsqsEUOV5GWnFjk9y9&redirect_uri=http://localhost:8080/login-results
# token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkhiZXQ0WlRvaTE2bzUyRXd4ZENoRSJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtc3RlZmFuLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZThmYzVlY2E1NTRkZjBjMDQ5N2IxZTUiLCJhdWQiOiJpbWFnZSIsImlhdCI6MTU4Njc5OTU4NSwiZXhwIjoxNTg2ODA2Nzg1LCJhenAiOiJRRXBKUnkzMU1PQnRsYmJzcXNFVU9WNUdXbkZqazl5OSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmltYWdlcyIsInBvc3Q6aW1hZ2VzIl19.NaplzXhrqapsucwsWTpXVub_D4Nf41NUXOwavq5sVuvd86IW2iELNL3zLfrmA3YfhgzkMY1lJn7SffoQMMSL5NI9lzk5lkbY4_o4NTzsOFySm2WgaEUBd8i8ywhi2qrBjo8OLuEiNqHX1SGCaB5JT9yG1BWG8hvw1ZPirKHQJMz4TEGb4E-sC0zpcVPkk2v6R2QI-oLXyqre1mN4lKNEL5C-jkvfvdNSOGuiQMhneTlzDejhnhguMqONS6Y34WJH5L_WAJuZhN8ZE0235GuLjgK8wzGyXBUJ0bDl6wBYYhV1XzkJiKEGFcFLri_Gj-rxVuPhyA_Jzs3p2mrjnTk95A

@app.route('/')
def index():
    # login page, see button

    # redirect to Auth0

    # use the callback function as "access granted" screen
    
    # get jwt token from header

    # redirect to headers() and set headers
    html = '''
            <form action="/login">
                <input type="submit" value="Login"/>
            </form>
            '''
    # return html
    authorize_url = f'https://{AUTH0_DOMAIN}/authorize?'
    authorize_url += f'audience={API_AUDIENCE}&'
    authorize_url += 'response_type=token&'
    authorize_url += f'client_id={CLIENT_ID}&'
    authorize_url += f'redirect_uri={CALLBACK_URL}'

    return redirect(authorize_url)

@app.route('/login')
def login():
    return redirect("https://fsnd-stefan.auth0.com/authorize?audience=image&response_type=token&client_id=QEpJRy31MOBtlbbsqsEUOV5GWnFjk9y9&redirect_uri=http://localhost:5000/headers")

@app.route('/login-results')
def logged_in():
    access_token = request.args.get('access_token', None)
    print(f"Access token is: {access_token}")
    return f"access token is {access_token}"

@app.route('/images')
@requires_auth('get:images')
def images(payload):
    pp.pprint(payload)
    return 'not implemented'

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success' : False,
        'error' : error.error,
        'status_code' : error.status_code
        
    }), error.status_code