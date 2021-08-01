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
import pandas as pd
from io import StringIO

@app.route('/')
def test3():
    return '<h1>server is running</h1>'

def confusion_matrix(y_labels,submission_json):
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    if(len(y_labels)==len(list(submission_json))):
        for tweet_id in y_labels:
            try:
                if(y_labels[tweet_id]=='HOF'):
                    if(submission_json[tweet_id][0]=='HOF'):
                        TP+=1
                    elif(submission_json[tweet_id][0]=='NONE'):
                        FN+=1
                    else:
                        return Response(status=405, response=json.dumps({'message':'unknown or empty labels found'}),mimetype='application/json')
                elif(y_labels[tweet_id]=='NONE'):
                    if(submission_json[tweet_id][0]=='HOF'):
                        FP+=1
                    elif(submission_json[tweet_id][0]=='NONE'):
                        TN+=1
                    else:
                        return Response(status=405, response=json.dumps({'message':'unknown or empty labels found'}),mimetype='application/json')
            except KeyError:
                return Response(status=406, response=json.dumps({'message':'missinng tweet id or unknown id found'}),mimetype='application/json')
            except Exception as Ex:
                return str(Ex)
        return {'TP':TP,'FP':FP,'TN':TN,'FN':FN}
    else:
        return Response(status=406, response=json.dumps({'message':'missinng tweet id or unknown id found'}),mimetype='application/json')

@app.route('/dashboard/submission', methods=['POST'])
def submit_run():
    try:
        if(request.method=='POST'):
            req = request.form
            team_name = request.form.get('team_name')
            task_name = request.form.get('task_name')
            submission_name = request.form.get('submission_name')
            description = request.form.get('description')
            submission_file = request.files['file']
            submission_df = pd.read_csv(submission_file)
            if(list(submission_df.columns)!=['tweet_id','label']):
                return Response(status=403, response=json.dumps({"message":'wrong columns'}), mimetype='application/json')
            count = list(db.submissions.aggregate([
                {'$match': {"_id":team_name,'submissions': {'$elemMatch': {'task_name': task_name}}}}, {
                '$project': {'submissions': {'$filter': {'input': '$submissions', 'as': 'submissions', 'cond': {'$eq': ['$$submissions.task_name', task_name]}}},}}]))
            if(len(count)==0 or len(count[0]['submissions'])<5):
                if(len(count)!=0 and len(count[0]['submissions'])>0):
                    if(len(list(db.submissions.find({'_id':team_name,'submissions.task_name':task_name,'submissions.submission_name':submission_name})))>0):
                        return Response(status=409,response=json.dumps({'message':"can't use same submission name for multiple submissions"}),mimetype='application/json')
                submission_df = submission_df.astype({'tweet_id':str})
                submission_json = submission_df.set_index('tweet_id').T.to_dict('list')
                actual_labels = list(db.test_labels.find({'_id':'2_ICHCL'},{'labels':1}))
                actual_labels = actual_labels[0]['labels']
                confusion_mat = confusion_matrix(actual_labels,submission_json)
                if(isinstance(confusion_mat,dict)):
                    precision = confusion_mat['TP'] / (confusion_mat['TP'] + confusion_mat['FP'])
                    recall = confusion_mat['TP'] / (confusion_mat['TP'] + confusion_mat['FN'])
                    f1_score = 2*((precision*recall)/(precision + recall))
                    accuracy = (confusion_mat['TP'] + confusion_mat['TN']) / sum(list(confusion_mat.values()))
                    db.submissions.update_one({'_id':team_name},{'$push':{'submissions':{'task_name':task_name,'submission_name':submission_name,'description':description,'timestamp':datetime.utcnow(),'accuracy':accuracy,'f1_score':f1_score,'confusion':confusion_mat,'submission_labels':submission_json}}})
                    return Response(status=200, response=json.dumps({'message':'submitted successfully'}),mimetype='application/json')
                else:
                    return confusion_mat
            else:
                return Response(status=408, response=json.dumps({"message":'maximum submission exceeded'}), mimetype='application/json')
        else:
            return Response(status=400, message=json.dumps({'message':'bad request'},mimetype='application/json'))
    except Exception as Ex:
        print("*******************************")
        print(Ex)
        print('*******************************')
        return str(Ex)

@app.route('/dashboard/team_data', methods=['POST'])
def team_data():
    try:
        if(request.method=='POST'):
            data = request.json
            team_name = data['team_name']
            team_submissions = list(db.submissions.find({'_id':team_name},{"team_name":0,"password_hash":0,"email":0,"submissions.submission_labels":0,"_id":0}))
            if(len(team_submissions)==0):
                return Response(status=401, response=json.dumps({'message':'invalid team-name'}),mimetype='application/json')
            elif(len(team_submissions[0]['submissions'])==0):
                return Response(status=404, response=json.dumps({'message':'No submissions found'}),mimetype='application/json')
            else:
                return Response(status=200, response=json.dumps(team_submissions[0]),mimetype='application/json')
        else:
            return Response(status=400, response=json.dumps({'message':'bad request'}),mimetype='application/json')
    except Exception as Ex:
        print("*******************************")
        print(Ex)
        print('*******************************')
        return str(Ex)
