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
import random

from logging.handlers import RotatingFileHandler

from flask import render_template, request, redirect, url_for


app = Flask(__name__)

#app.config['MONGO_DBNAME'] = 'restdb'
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'

#mongo = PyMongo(app)


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/setcookie', methods = ['POST', 'GET'])
def setcookie():
    if request.method == 'POST':
        user = request.form['username']
        resp = redirect(url_for("newTask"))
        resp.set_cookie('UserName', user)
        return resp

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # You should really validate that these fields
        # are provided, rather than displaying an ugly
        # error message, but for the sake of a simple
        # example we'll just assume they are provided

        user_name = request.form["name"]
        #password = request.form["password"]
        #user = db.find_by_name_and_password(user_name, password)

        #if not user:
            # Again, throwing an error is not a user-friendly
            # way of handling this, but this is just an example
        #    raise ValueError("Invalid username or password supplied")

        # Note we don't *return* the response immediately
        response = redirect(url_for("newTask"))
        response.set_cookie('UserName', user_name)
        return response
    else:
        return render_template("index.html")

@app.route("/do-that")
def do_that():
    user_id = request.cookies.get('UserName')
    if user_id:
        user = database.get(user_id)
        if user:
            # Success!
            return render_template('do_that.html', user=user)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/newTask')
def newTask():
    user_name = request.cookies.get('UserName')

    if not user_name:
        return redirect(url_for('login'))
    app.logger.info("User %s is assigned with new random task", user_name)

    if dbutil.haveWizardTask() and random.uniform(0, 1) > 0.4:
        return newWizardTask()
    else:
        if dbutil.haveUserTask():
            return newUserTask()
    if dbutil.haveWizardTask():
        return newUserTask()
    return render_template("noTask.html")

@app.route('/')
def hello():
    return render_template('home.html')

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

@app.route('/resetTask/<taskID>')
def resetTaskById(taskID):
    task = dbutil.taskdb.find_one({dbutil.TASK_ID: taskID}, {'_id': False})
    if task != None:
        return json.dumps(task)
    return json.dumps({"status": "Not found"})

@app.route('/task/<taskID>')
def getTaskById(taskID):
    task = dbutil.taskdb.find_one({dbutil.TASK_ID: taskID}, {'_id': False})
    if task != None:
        return json.dumps(task)
    return json.dumps({"status": "Not found"})

@app.route('/showAll')
def show_all():
    return json.dumps(list(dbutil.taskdb.find({},{'_id': False})))

@app.route('/newUserTask')
def newUserTask():
    user_name = request.cookies.get('UserName')

    if not user_name:
        return redirect(url_for('login'))
    app.logger.info("User %s is assigned with a new user HIT", user_name)
    #get one task
    task = dbutil.taskdb.find_and_modify(
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
    user_name = request.cookies.get('UserName')
    if not user_name:
        return redirect(url_for('login'))

    app.logger.info("User %s finish a user HIT", user_name)
    if request.method == "POST":
        #print request
        content = request.get_json()
        taskId = content[dbutil.TASK_ID]
        userResponse = content['user_response']
        #print userResponse
        task = dbutil.taskdb.find_one({dbutil.TASK_ID: taskId})
        task[dbutil.USER_UTC].append("User: " + userResponse)
        task[dbutil.USER_UTC_ANNOTATOR].append(user_name)
        task[dbutil.STATUS] = dbutil.WT
        #end = content["end"]
        #if end:
            #task[dbutil.STATUS] = dbutil.FT
        dbutil.taskdb.remove({dbutil.TASK_ID: taskId})
        dbutil.taskdb.insert(task)
        #print taskId
        return json.dumps({'status':'OK','task_id': taskId, 'user_response': userResponse})

#Wizard
@app.route('/newWizardTask')
def newWizardTask():
    user_name = request.cookies.get('UserName')

    if not user_name:
        return redirect(url_for('login'))
    app.logger.info("User %s is assigned with new wizard HIT", user_name)

    task = dbutil.taskdb.find_and_modify(
        { dbutil.STATUS : dbutil.WT },
        {"$set": { dbutil.STATUS: dbutil.WW}}
    )

    #task = dbutil.taskdb.find_one({dbutil.STATUS: dbutil.WT})
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
    #result = dbutil.taskdb.update({"taskId": taskId}, {"$set": {
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
    user_name = request.cookies.get('UserName')
    if not user_name:
        return redirect(url_for('login'))

    app.logger.info("User %s is searching DB", user_name)
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
    task = dbutil.taskdb.find_one({dbutil.TASK_ID: taskId})
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
                                   dbutil.DS_ASKING_SCORE: askScore},
              dbutil.SYS_DIA_ANNOTATOR: user_name
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
    dbutil.taskdb.remove({dbutil.TASK_ID: taskId})
    dbutil.taskdb.insert(task)

    #res = list(restaurantdb.find({AREA_NAME : {'$regex' : '.*' + '三元桥' + '.*'}}))
    #build search key
    key = {}
    if len(area) != 0:
        key[dbutil.AREA_NAME] = {'$regex': '.*' + area + '.*'}
    if len(foodType) != 0:
        key[dbutil.FOOD_TYPE] = {'$regex': '.*' + foodType + '.*'}
    if priceLowerBound != -1:
        key[dbutil.PRICE] = {'$gt':  priceLowerBound, '$lt': priceUpperBound}
    if len(name) != 0:
        name2 = name.split("(")
        print name2[0]
        key[dbutil.NAME] = {'$regex': '.*' + name2[0] + '.*'}
    app.logger.info("User %s search key: %s", user_name, key)

    results = list(dbutil.restaurantdb.find(key))

    #print results
    for r in results:
        del r['_id']

    sortedlist = sorted(results, key=lambda k: float(k[dbutil.SCORE]), reverse=True)
    return json.dumps(sortedlist)

@app.route('/wizardUpdateTask', methods=['POST'])
def wizardUpdateTask():
    user_name = request.cookies.get('UserName')
    if not user_name:
        return redirect(url_for('login'))

    app.logger.info("User %s finish a wizard HIT ", user_name)
    if request.method == "POST":
        #print request
        content = request.get_json()
        #print content
        taskId = content[dbutil.TASK_ID]
        wizardResponse = content['wizard_response']
        sysDiaAct = content[dbutil.SYS_DIA_ACT]
        sysSlotInfo = content[dbutil.SYS_SLOT_INFO]
        print sysSlotInfo
        #print wizardResponse
        task = dbutil.taskdb.find_one({dbutil.TASK_ID: taskId})

        #if len(task[dbutil.DIA_STATE]) < len(task[dbutil.USER_UTC]):
        #    return json.dumps({'status':'error','message': "请先填写对话状态信息"})
        task[dbutil.SYS_UTC].append("Sys: " + wizardResponse)
        task[dbutil.STATUS] = dbutil.UT
        #print task
        task[dbutil.DIA_ACT].append({dbutil.SYS_DIA_ACT : sysDiaAct, dbutil.SYS_UTC : wizardResponse, dbutil.SYS_SLOT_INFO: sysSlotInfo, dbutil.SYS_DIA_ANNOTATOR: user_name})
        end = content["end"]
        if end:
            task[dbutil.STATUS] = dbutil.FT

        dbutil.taskdb.remove({dbutil.TASK_ID: taskId})
        dbutil.taskdb.insert(task)
        print "returning"
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
        dbutil.taskdb.insert(task1)
        dbutil.taskdb.insert(task2)
        print dbutil.taskdb.find_one({'taskId': '123'})
        res1 = {'venueName': 'LaoSichuan', 'foodType': 'Sichuan', 'address': "zhongguancun", 'phone': "110"}
        res2 = {'venueName': 'Shaxianxiaochi', 'foodType': 'shaxian', 'address': "Xi tu cheng no. 10", 'phone': "911"}
        res3 = {'venueName': 'LaoSichuan', 'foodType': 'Sichuan', 'address': "xiyatu", 'phone': "001"}
        dbutil.restaurantdb.insert(res1)
        dbutil.restaurantdb.insert(res2)
        dbutil.restaurantdb.insert(res3)


if __name__=="__main__":
    logging.basicConfig(filename='app.log',level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    handler = RotatingFileHandler('foo.log', maxBytes=1000000000, backupCount=10)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    dbutil.loadTask()
    dbutil.loadRestaurantData()
    app.run(host='0.0.0.0', port=9005, debug=True)
