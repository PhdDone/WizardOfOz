#-*-coding:utf-8-*-
import os
from flask import Flask,render_template, request,json
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from pymongo import MongoClient
import dbutil
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'

mongo = PyMongo(app)


@app.route('/')
def hello():
    return 'Welcome to KENG!'

def buildSents(sysUtc, userUtc):
    sents = []
    idx = 0
    while idx < len(sysUtc) and idx < len(userUtc):
        sents.append(sysUtc[idx])
        sents.append(userUtc[idx])
        idx += 1
    while idx < len(sysUtc):
        sents.append(sysUtc[idx])
        idx += 1
    return sents

@app.route('/task/<taskID>')
def getTaskById(taskID):
    task = mongo.db.tasks.find_one({dbutil.TASK_ID: taskID}, {'_id': False})
    if task != None:
        return json.dumps(task)
    return json.dumps({"status": "Not found"})

@app.route('/showAll')
def show_all():
    return json.dumps(list(mongo.db.tasks.find({},{'_id': False})))

@app.route('/newUserTask')
def newUserTask():
    #get one task
    task = mongo.db.tasks.find_and_modify(
        { dbutil.STATUS : dbutil.UT },
        {"$set": { dbutil.STATUS: dbutil.WU}},
    )
    #print task
    #task = mongo.db.tasks.find_one({dbutil.STATUS: dbutil.UT})
    #print task
    if task is None:
        return render_template('checkWizard.html')
    taskId = task[dbutil.TASK_ID]

    #updateStatus
    #result = mongo.db.tasks.update({dbutil.TASK_ID: taskId}, {"$set": {
    #    dbutil.STATUS: dbutil.WU
    #}})

    foodType = "*"
    address = "*"
    priceRange = "*"
    venueName = "*"
    area = "*"

    sysUtc = task[dbutil.SYS_UTC]
    userUtc = task[dbutil.USER_UTC]

    sents = buildSents(sysUtc, userUtc)
    userGoal = task[dbutil.USER_GOAL]


    if dbutil.NAME in task.keys():
        venueName = task[dbutil.NAME]
    if dbutil.FOOD_TYPE in task.keys():
        foodType = task[dbutil.FOOD_TYPE]
    if dbutil.ADDRESS in task.keys():
        address = task[dbutil.ADDRESS]
    if dbutil.PRICE_RANGE in task.keys():
        priceRange = task[dbutil.PRICE_RANGE]
    if dbutil.AREA_NAME in task.keys():
        area = task[dbutil.AREA_NAME]

    #lookingFor = task[dbutil.LOOKING_FOR]

    #return render_template('user.html', taskId=taskId, venueName=venueName, foodType=foodType, area=area, priceRange=priceRange, address=address, lookingFor=lookingFor, sents=sents)
    return render_template('user.html', taskId=taskId, userGoal = userGoal, sents=sents)

@app.route('/userUpdateTask', methods=['POST'])
def userUpdateTask():
    if request.method == "POST":
        #print request
        content = request.get_json()
        print content
        taskId = content[dbutil.TASK_ID]
        userResponse = content['user_response']
        #print userResponse
        task = mongo.db.tasks.find_one({dbutil.TASK_ID: taskId})
        task[dbutil.USER_UTC].append("User: " + userResponse)
        task[dbutil.STATUS] = dbutil.WT
        #end = content["end"]
        #if end:
            #task[dbutil.STATUS] = dbutil.FT
        mongo.db.tasks.remove({dbutil.TASK_ID: taskId})
        mongo.db.tasks.insert(task)
        #print taskId
        return json.dumps({'status':'OK','task_id': taskId, 'user_response': userResponse})

#Wizard
@app.route('/newWizardTask')
def newWizardTask():
    task = mongo.db.tasks.find_and_modify(
        { dbutil.STATUS : dbutil.WT },
        {"$set": { dbutil.STATUS: dbutil.WW}}
    )

    #task = mongo.db.tasks.find_one({dbutil.STATUS: dbutil.WT})
    if task is None:
        return render_template('checkUser.html')

    taskId = task[dbutil.TASK_ID]
    sysUtc = task[dbutil.SYS_UTC]
    userUtc = task[dbutil.USER_UTC]

    sents = buildSents(sysUtc, userUtc)

    prevFoodType = ""
    prevUpperBound = -1
    prevLowerBound = -1
    prevAreaName = ""

    if len(userUtc) >= 2 and len(task[dbutil.DIA_STATE]) - 1 >= len(userUtc) - 2 and dbutil.DS_GOAL_LABELS in task[dbutil.DIA_STATE][len(userUtc) - 2].keys():
        prevDialogueStateGoalLabels = task[dbutil.DIA_STATE][len(userUtc) - 2][dbutil.DS_GOAL_LABELS]
        prevAreaName = prevDialogueStateGoalLabels[dbutil.AREA_NAME]
        prevFoodType = prevDialogueStateGoalLabels[dbutil.FOOD_TYPE]
        prevUpperBound = prevDialogueStateGoalLabels[dbutil.DS_PRICE_UPPER_BOUND]
        prevLowerBound = prevDialogueStateGoalLabels[dbutil.DS_PRICE_LOWER_BOUND]

    #goal-labels: {
    #                 area_name: "",
    #                 ds_prece_upper_bound: -1,
    #                 ds_price_lower_bound: -1,
    #                 food_type: ""
    #            },
    #updateStatus
    #result = mongo.db.tasks.update({"taskId": taskId}, {"$set": {
    #dbutil.STATUS: dbutil.WW
    #}})
    print prevAreaName
    return render_template('wizard.html', taskId=taskId, sents = sents, prevFoodType = prevFoodType, prevAreaName = prevAreaName, prevUpperBound = prevUpperBound, prevLowerBound = prevLowerBound)

def createDefaultDS():
    foodType = ""
    area = ""
    askFoodType = False
    askArea = False
    #return foodType + "," + area + "," + str(askFoodType) + "," + str(askArea)
    return "No dialogue state"

@app.route('/searchDB',methods=['POST'])
def searchDB():
    #print request
    content = request.get_json()
    area = content[dbutil.AREA]
    name = content[dbutil.NAME]
    foodType = content[dbutil.FOOD_TYPE]
    print content

    priceLowerBound = -1
    priceUpperBound = -1

    if len(content["lower_bound"]) > 0:
        priceLowerBound = int(content["lower_bound"])
    if len(content["upper_bound"]) > 0:
        priceUpperBound = int(content["upper_bound"])

    if priceLowerBound != -1 and priceUpperBound <=0:
        priceUpperBound = 999999

    if priceUpperBound != -1 and priceLowerBound <=0:
        priceLowerBound = 0

    #askFoodType = content[dbutil.DS_ASKING_FOOD_TYPE]
    askArea = content[dbutil.DS_ASKING_AREA]
    askPrice = content[dbutil.DS_ASKING_PRICE]
    askScore = content[dbutil.DS_ASKING_SCORE]

    taskId = content[dbutil.TASK_ID]
    task = mongo.db.tasks.find_one({dbutil.TASK_ID: taskId})
    curDS = task[dbutil.DIA_STATE]
    userUtc = task[dbutil.USER_UTC]
    idx = len(userUtc) - 1

    #TODO: update DS
    newDS = { dbutil.DS_GOAL_LABELS : { dbutil.FOOD_TYPE : foodType,
                                dbutil.AREA_NAME: area,
                                dbutil.DS_PRICE_LOWER_BOUND: priceLowerBound,
                                dbutil.DS_PRICE_UPPER_BOUND: priceUpperBound
                                },
              dbutil.DS_REQUEST_SLOTS : { dbutil.DS_ASKING_AREA: askArea,
                                   #dbutil.DS_ASKING_FOOD_TYPE: askFoodType,
                                   dbutil.DS_ASKING_PRICE: askPrice,
                                   dbutil.DS_ASKING_SCORE: askScore}
    }

    #newDS = foodType + "," + area + "," + str(priceLowerBound) + "," + str(priceUpperBound) + "," + str(askFoodType) + "," + str(askArea) + "," + str(askPrice)
    while len(curDS) < len(userUtc):
        print "DS len: {}, userUtc len: {}".format(str(len(curDS)), str(len(userUtc)))
        curDS.append({"error": createDefaultDS()})
    if idx >= 0:
        newDS[dbutil.USER_UTC] = userUtc[idx]
    curDS[idx] = newDS
    task[dbutil.DIA_STATE] = curDS
    print task[dbutil.DIA_STATE]
    mongo.db.tasks.remove({dbutil.TASK_ID: taskId})
    mongo.db.tasks.insert(task)

    #res = list(restaurantdb.find({AREA_NAME : {'$regex' : '.*' + '三元桥' + '.*'}}))
    #build search key
    key = {}
    if len(area) != 0:
        key[dbutil.AREA_NAME] = {'$regex': '.*' + area + '.*'}
    if len(foodType) != 0:
        key[dbutil.FOOD_TYPE] = foodType
    if priceLowerBound != -1:
        key[dbutil.PRICE] = {'$gt':  priceLowerBound, '$lt': priceUpperBound}
    if len(name) != 0:
        key[dbutil.NAME] = {'$regex': '.*' + name + '.*'}
    app.logger.info("search key: %s", key)

    results = list(mongo.db.restaurant.find(key))
    #print results
    for r in results:
        del r['_id']
    return json.dumps(results)

@app.route('/wizardUpdateTask', methods=['POST'])
def wizardUpdateTask():
    if request.method == "POST":
        #print request
        content = request.get_json()
        #print content
        taskId = content[dbutil.TASK_ID]
        wizardResponse = content['wizard_response']
        #print wizardResponse
        task = mongo.db.tasks.find_one({dbutil.TASK_ID: taskId})

        #if len(task[dbutil.DIA_STATE]) < len(task[dbutil.USER_UTC]):
        #    return json.dumps({'status':'error','message': "请先填写对话状态信息"})
        task[dbutil.SYS_UTC].append("Sys: " + wizardResponse)
        task[dbutil.STATUS] = dbutil.UT
        end = content["end"]
        if end:
            task[dbutil.STATUS] = dbutil.FT

        mongo.db.tasks.remove({dbutil.TASK_ID: taskId})
        mongo.db.tasks.insert(task)
        #print taskId
        return json.dumps({'status':'OK','task_id': taskId, 'wizard_response': wizardResponse})

def initDb_v0():
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
    logging.basicConfig(filename='app.log',level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    dbutil.loadTask()
    app.run(host='0.0.0.0', port=9005, debug=True)
