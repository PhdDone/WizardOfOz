import os
from flask import Flask,render_template, request,json
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from pymongo import MongoClient

import logging

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'

mongo = PyMongo(app)


sents = ["Sys: Hello, welcom", "User: I want a gastropub food", "Sys: There're 4 restaurants serving Sichuan food, what price range do you want?"]

sents2 = ["Sys: Hello, welcom", "User: I want a gastropub food", "Sys: There're 4 restaurants serving Sichuan food, what price range do you want?", "User: don't care"]
@app.route('/')
def hello():
    return 'Welcome to Python Flask!'

@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/signUpUser', methods=['POST'])
def signUpUser():
    user =  request.form['username'];
    password = request.form['password'];
    return json.dumps({'status':'OK','user':user,'pass':password});

@app.route('/newUserTask')
def newUserTask():
    #get one task
    task = mongo.db.tasks.find_one({"status": "userTask"})
    print task
    if task is None:
        return render_template('checkWizard.html')
    taskId = task["taskId"]

    #updateStatus
    result = mongo.db.tasks.update({"taskId": taskId}, {"$set": {
        "status": "waitForUserHit"
    }})

    foodType = "*"
    address = "*"
    priceRange = "*"
    venueName = "*"

    content = task["content"]
    sents = []

    for k in range(0, len(content)):
        sents.append(content[k])

    if "venueName" in task.keys():
        venueName = task["venueName"]
    if "foodType" in task.keys():
        foodType = task["foodType"]
    if "address" in task.keys():
        address = task["address"]
    if "priceRange" in task.keys():
        priceRange = task["priceRange"]

    lookingFor = task["lookingFor"]

    return render_template('user.html', taskId=taskId, venueName=venueName, foodType=foodType, priceRange=priceRange, address=address, lookingFor=lookingFor, sents=sents)

@app.route('/userUpdateTask', methods=['POST'])
def userUpdateTask():
    if request.method == "POST":
        print request
        content = request.get_json()
        print content
        taskId = content['taskId']
        userResponse = content['userResponse']
        print userResponse
        task = mongo.db.tasks.find_one({"taskId": taskId})
        index = len(task["content"])
        task["content"].append("User: " + userResponse)
        task["status"] = "wizardTask"
        mongo.db.tasks.remove({"taskId": taskId})
        mongo.db.tasks.insert(task)
        #print taskId
        return json.dumps({'status':'OK','taskId': taskId, 'userResponse': userResponse})

#Wizard
@app.route('/newWizardTask')
def newWizardTask():
    task = mongo.db.tasks.find_one({"status": "wizardTask"})
    if task is None:
        return render_template('checkUser.html')

    taskId = task["taskId"]
    content = task["content"]

    #updateStatus
    result = mongo.db.tasks.update({"taskId": taskId}, {"$set": {
    "status": "waitForWizardHit"
    }})
    sents = []
    for k in range(0, len(content)):
        sents.append(content[k])

    return render_template('wizard.html', taskId=taskId, sents = sents)

@app.route('/searchDB',methods=['POST'])
def searchDB():
    print request
    key = request.get_json()
    print key

    results = list(mongo.db.restaurant.find({'venueName': 'LaoSichuan', 'foodType': 'Sichuan'}))
    print results
    for r in results:
        del r['_id']
    return json.dumps(results)

@app.route('/wizardUpdateTask', methods=['POST'])
def wizardUpdateTask():
    if request.method == "POST":
        print request
        content = request.get_json()
        print content
        taskId = content['taskId']
        wizardResponse = content['wizardResponse']
        print wizardResponse
        task = mongo.db.tasks.find_one({"taskId": taskId})
        
        task["content"].append("Sys: " + wizardResponse)
        task["status"] = "userTask"
        mongo.db.tasks.remove({"taskId": taskId})
        mongo.db.tasks.insert(task)
        #print taskId
        return json.dumps({'status':'OK','taskId': taskId, 'wizardResponse': wizardResponse})

def initDb():
    #task schema:
    #status: userTask, wizardTask, finished
    #priceRange:
    #address
    #phoneNumber
    #foodType
    #venueName

    #venue schema:
    #name
    #address
    #phone
    #foodType

    client = MongoClient('mongodb://localhost:27017/')
    restdb = client['restdb']
    restdb.tasks.drop()
    restdb.restaurant.drop()

    with app.app_context():
        #Task1 example: find a address of a sichuan resturant.
        task1 = {'taskId':'123', 'status': 'userTask', 'content':['Sys: Welcome!'], 'foodType': 'Sichuan', 'lookingFor': 'address'}
        #Task2 example: find a  resturant near beiyou.
        task2 = {'taskId':'124', 'status': 'userTask', 'content':['Sys: Welcome!'], 'venueName': 'Shaxianxiaochi', 'lookingFor': 'address'}
        mongo.db.tasks.insert(task1)
        mongo.db.tasks.insert(task2)
        print mongo.db.tasks.find_one({'taskId': '123'})
        res1 = {'venueName': 'LaoSichuan', 'foodType': 'Sichuan', 'address': "zhongguancun", 'phone': "110"}
        res2 = {'venueName': 'Shaxianxiaochi', 'foodType': 'shaxian', 'address': "Xi tu cheng no. 10", 'phone': "911"}
        res3 = {'venueName': 'LaoSichuan', 'foodType': 'Sichuan', 'address': "xiyatu", 'phone': "001"}
        mongo.db.restaurant.insert(res1)
        mongo.db.restaurant.insert(res2)
        mongo.db.restaurant.insert(res3)


if __name__=="__main__":
    #logging.basicConfig(filename='app.log',level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    initDb()
    app.run(host='0.0.0.0', port=9005, debug=True)
