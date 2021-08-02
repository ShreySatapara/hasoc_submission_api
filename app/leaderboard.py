from app import app,db,bcrypt,token_required
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
import pandas as pd
from io import StringIO


@app.route('/leaderboard', methods=['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
@token_required
def leaderboard():
    try:
        if(request.method=='POST'):
            req_data = request.json
            task_name = req_data['task_name']
            if(task_name not in ["1A_English","1A_Hindi","1A_Marathi","1B_English","1B_Hindi","2_ICHCL"]):
                return Response(status=405, response=json.dumps({'message':'invalid taskname'}),mimetype='application/json')
            data = list(db.submissions.find({"task_name":task_name},{'_id':0,"submission_labels":0}))
            if(len(data)==0):
                return Response(status=404, response=json.dumps({'message':'no submissions found yet'}),mimetype="application/json")
            #print(data)
            data.sort(key = lambda x:x['f1_score'],reverse=True)
            return Response(status=200, response=json.dumps(data),mimetype='application/json')

        else:
            return Response(status=400, response=json.dumps())
    except Exception as Ex:
        print('***********************')
        print(str(Ex))
        print('***********************')