import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

'''
!! NOTE use this link to get new token
https://fsnd-stefan.auth0.com/authorize?audience=coffee-shop&response_type=token&client_id=5R2mLKQg5UOGxb2onAdlgSBy3WLDNcvO&redirect_uri=http://localhost:8080/login-results
barista token (stefanbfritz): eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkhiZXQ0WlRvaTE2bzUyRXd4ZENoRSJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtc3RlZmFuLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZThmYzVlY2E1NTRkZjBjMDQ5N2IxZTUiLCJhdWQiOiJjb2ZmZWUtc2hvcCIsImlhdCI6MTU4NzEzMjE2NiwiZXhwIjoxNTg3MTM5MzY2LCJhenAiOiI1UjJtTEtRZzVVT0d4YjJvbkFkbGdTQnkzV0xETmN2TyIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmRyaW5rcyIsImdldDpkcmlua3MtZGV0YWlsIiwicGF0Y2g6ZHJpbmtzIiwicG9zdDpkcmlua3MiXX0.NgBwhnfbv73wC1vtZvfH-QMsRctxi3jZW7EBe0v4ChlUyHmMTHreHIjVmklo3GSE-9o6q0Tc271R_wGO7VvqSpW7pWLo61uT7feolwTjwxHvLFOnqGdYfhYUONZdMurKIrXgzbdQZXTpwkBL-WuReR6N7PBoXWge9jc7y7THw2Q1B7ZuCJOcGdS4-2d6g0Zbi89m6lRdgH5svy9UQ-V2GlDfAsXNQfvkWuie8k48AsAXxoUt97fh8zMpBo8jOnCBr8a7v6PwW5YUZl1VF9vzwSA_QpRXBiXv6JN0jdftg9YTk1usMKhsRaot4In2DCBcXTxH5m-zpVGo4B6blgTI7w

'''

def get_title_and_recipe(request):
    body = request.get_json()
    title = body['title'] if 'title' in body else None
    recipe = json.dumps(body['recipe']) if 'recipe' in body else None

    if recipe and recipe[0] != '[': # only one ingredient in the recipe, json.dumps does not put in list form
        recipe = '[' + recipe + ']'
    
    return title, recipe


## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.order_by(Drink.title).all()

    if len(drinks) == 0:
        abort(404)

    formatted_drinks = [d.short() for d in drinks]

    return jsonify({
        'success': True,
        'drinks' : formatted_drinks,
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks = Drink.query.order_by(Drink.title).all()

    if len(drinks) == 0:
        abort(404)

    formatted_drinks = [d.long() for d in drinks]

    return jsonify({
        'success': True,
        'drinks' : formatted_drinks,
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink():
    try:
        title, recipe = get_title_and_recipe(request)
        
        new_drink = Drink(
            title=title,
            recipe=recipe
        )
        new_drink.insert()

    except:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [new_drink.long()],
    })



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id):
    try:
        title, recipe = get_title_and_recipe(request)
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        
        if drink is None:
            abort(404)
        if title:
            drink.title = title
        if recipe:
            drink.recipe = recipe
        
        drink.update()

    except:
        abort(422)
        
    return jsonify({
        'success': True,
        "drinks" : [drink.long()]
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'not found'
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def not_found(error):
    return jsonify({
        "success": False,
        'error': error.status_code,
        'message' : error.error
    }), error.status_code