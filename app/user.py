from app import app,db,bcrypt
from flask import Flask, request, Response, redirect, url_for, json, make_response, jsonify
import pymongo
import jwt
import hashlib
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime, timedelta
from flask_cors import cross_origin, CORS
import urllib
from dotenv import load_dotenv
import os

@app.route('/user/add_team', methods=['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def add_team():
    try:
        if request.method == 'POST':
            data = request.json
            team_name = data['team_name']
            email = data['email']
            password = data['password']
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            data = db.submissions.insert_one(
                {'_id': team_name, 'team_name': team_name, 'email': email, 'password_hash': password_hash,"submissions":[]})
            return Response(
                response=json.dumps({'message': 'User created successfully'}), status=200, mimetype="application/json")
        else:
            return Response(status=400, response=json.dumps({'message': 'Bad request'}), mimetype='application/json')

    except pymongo.errors.DuplicateKeyError:
        return Response(
            response=json.dumps({'message': 'duplicate entry'}), status=403, mimetype='application/json')
    except Exception as Ex:
        print('\n\n\n*********************************')
        print(Ex)
        print('*********************************\n\n\n')
        return Response(
            response=json.dumps({'message': Ex}), status=500, mimetype="application/json")


@ app.route('/user/login', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def login():
    try:
        if request.method == 'POST':
            form_data = request.get_json()
            team_name = form_data['team_name']
            password = form_data['password']
            if(team_name != '' and password != ''):
                data = list(db.submissions.find({'_id': team_name}))
                if(len(data) == 0):
                    return Response(status=404, response=json.dumps({'message': 'Team does not exist'}), mimetype='application/json')
                else:
                    data = data[0]
                    db_password_hash = data['password_hash']
                    if(bcrypt.check_password_hash(db_password_hash, password)):
                        token = jwt.encode({'team_name': team_name}, app.config['SECRET_KEY'])
                        return make_response(jsonify({'token': token.decode('UTF-8')}), 201)
                    else:
                        return Response(status=402, response=json.dumps({'message': 'Invalid password'}), mimetype='application/json')
            else:
                return Response(status=400, response=json.dumps({'message': 'Bad request'}), mimetype='application/json')
        else:
            return Response(status=401, response=json.dumps({'message': 'invalid request type'}), mimetype='application/json')
    except Exception as Ex:
        print('\n\n\n*********************************')
        print(Ex)
        print('*********************************\n\n\n')
        return Response(
            response=json.dumps({'message': Ex}), status=500, mimetype="application/json")


@ app.route('/user/change_password', methods=['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def change_password():
    try:
        if request.method == 'POST':
            data = request.get_json()
            team_name = data['team_name']
            password = data['password']
            new_password = data['new_password']
            data = list(db.submissions.find({'_id': team_name}))
            if(len(data) > 0):
                data = data[0]
                db_password_hash = data['password_hash']
                if(bcrypt.check_password_hash(db_password_hash, password)):
                    password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
                    db.submissions.update_one({'_id': team_name}, {'$set': {'password_hash': password_hash}})
                    return Response(status=200, response=json.dumps({'message': 'password updated successfully'}), mimetype='application/json')
                else:
                    return Response(status=402, response=json.dumps({'message': 'invalid password'}), mimetype='application/json')
            else:
                return Response(status=404, response=json.dumps({'message': 'invalid team name'}), mimetype='application/json')
    except Exception as Ex:
        print('\n\n\n*********************************')
        print(Ex)
        print('*********************************\n\n\n')
        return Response(
            response=json.dumps({'message': Ex}), status=500, mimetype="application/json")