from flask_bcrypt import Bcrypt
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

load_dotenv()
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['CORS_HEADERS'] = 'application/json'
CORS(app)



try:
    mongo = pymongo.MongoClient("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false")
    db = mongo.hasoc
    print('\n\n' + '#'*10 + '\n\nSUCCESS\n\n' + '#'*10)
    mongo.server_info()
except Exception as ex:
    print('\n\n\n*********************************\n\n\n')
    print(ex)
    print('\n\n\n*********************************\n\n\n')


from app import admin,dashboard,leaderboard,user

