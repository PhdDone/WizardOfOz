#-*-coding:utf-8-*-
from pymongo import MongoClient
import datetime
import glob
import os.path
import pymongo
import json
import sys
import itertools
import codecs
from pprint import pprint
import re
import os

client = MongoClient('mongodb://localhost:27017/')

print os.environ.keys()
#client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
#if 'DB_PORT_27017_TCP_ADDR' in os.environ.keys():


restdb = client['restdb']

taskdb = restdb.tasks
restaurantdb = restdb.restaurant

#Task related
TASK_ID = "task_id"
STATUS = "status"
NAME = "name" #venueName
PRICE_RANGE = "price_range"
ADDRESS = "address"
PHONE_NUMBER = "phone_number"
FOOD_TYPE = "food_type"
AREA_NAME = "area_name"
USER_UTC = "user_utc" #string array
SYS_UTC = "sys_utc" #string array
DIA_STATE = "dia_state"  #string array
LOOKING_FOR = "looking_for"
USER_GOAL = "user_goal"

#dialogue_stated related
DS_FOOD_TYPE = "ds_food_type"
DS_AREA = "ds_area"
DS_PRICE_LOWER_BOUND = "ds_price_lower_bound"
DS_PRICE_UPPER_BOUND = "ds_prece_upper_bound"


DS_ASKING_FOOD_TYPE = "ds_asking_food_type"
DS_ASKING_AREA = "ds_asking_area"
DS_ASKING_PRICE = "ds_asking_price"
DS_ASKING_SCORE = "ds_asking_score"

DS_GOAL_LABELS = "goal_lables"
DS_REQUEST_SLOTS = "request_slots"

DIA_ACT = "dia_act"
SYS_DIA_ACT = "sys_dia_act"
SYS_DIA_ACT_HELLO = "hello"
SYS_DIA_ACT_BYE = "bye"
SYS_DIA_ACT_REQUEST = "request"
SYS_DIA_ACT_CONFIRM = "confirm"
SYS_DIA_ACT_INFORM = "inform"
SYS_DIA_ACT_RECOMMEND = "recommend"
SYS_DIA_ACT_REPEAT = "repeat"

#TASK_SCHEMA = [STATUS, TASK_ID, NAME, PRICE_RANGE, ADDRESS, PHONE_NUMBER, FOOD_TYPE, AREA_NAME, USER_UTC, SYS_UTC, DIA_STATE]
TASK_SCHEMA = [STATUS, TASK_ID, USER_UTC, SYS_UTC, DIA_STATE, DIA_ACT, USER_GOAL]

#Task status
UT = "userTask"
WU = "waitForUserHit"
WT = "wizardTask"
WW = "waitForWizardHit"
FT = "finish"

#Restaurant related
CITY = "city"
#NAME = "name" #same from task
AREA = "area"
RATING_NUM = "rating_num"
PRICE = "price"
URL = "url"
SCORE = "score"
LNG = "lng"
LAT = "lat"
COOK = "cook" #["g114", "韩国料理"]
ID = "id"
ADDRESS = "address"
RATING_NUM = "rating_num"
AREA_NAME = "area_name"

RESTAURANT_SCHEMA = [CITY, NAME, RATING_NUM, PRICE, URL, SCORE, LNG, LAT, COOK, ID, ADDRESS, AREA, AREA_NAME, FOOD_TYPE]

DIA_ACT = "dia_act"
#{"dia_act" : [{"sys_dia_act": "hello": "sys_utc": "hello world"}]}
SYS_DIA_ACT = "sys_dia_act"
SYS_DIA_ACT_HELLO = "hello"
SYS_DIA_ACT_BYE = "bye"
SYS_DIA_ACT_REQUEST = "request"
SYS_DIA_ACT_CONFIRM = "confirm"
SYS_DIA_ACT_INFORM = "inform"
SYS_DIA_ACT_RECOMMEND = "recommend"
SYS_DIA_ACT_REPEAT = "repeat"


def checkTask(task):
    for key in TASK_SCHEMA:
        if key not in task.keys():
            #TODO: check task_id
            print "{} not in task: {}".format(key, task[TASK_ID])
            if key == USER_UTC or key == SYS_UTC or key == DIA_STATE or key == AREA or key == DIA_ACT:
                task[key] = []
                continue
            task[key] = "*"
    return task

def checkRestaurant(restaurant):
    for key in RESTAURANT_SCHEMA:
        if key not in restaurant.keys():
            print "{} not in task: {}".format(key, restaurant[ID])
            if key == COOK or key == AREA:
                restaurant[key] = []
                continue
            restaurant[key] = "*"
    if len(restaurant[COOK]) >= 2:
        restaurant[FOOD_TYPE] = restaurant[COOK][1]
    if len(restaurant[AREA]) >= 2:
        restaurant[AREA_NAME] = restaurant[AREA][1]
    return restaurant

def insertTask(task):
    task = checkTask(task)
    _id = taskdb.insert(task)
    return _id

def dropTaskDB():
    taskdb.drop()

def dropRestaurantDB():
    restaurantdb.drop()

def resetWUtoUT():
    WU_tasks = list(taskdb.find({STATUS : WU}))
    taskdb.remove({"status": WU})
    for t in WU_tasks:
        t[STATUS] = UT
        insertTask(t)

def resetWWtoWT():
    WW_tasks = list(taskdb.find({STATUS : WW}))
    res = taskdb.remove({STATUS: WW})
    for t in WW_tasks:
        t[STATUS] = WT
        insertTask(t)

def init():
    dropTaskDB()

    task1 = {TASK_ID:'123', STATUS: 'userTask', SYS_UTC:["Sys: 欢迎! 您可以根据菜系，价格和区域查找餐厅"], FOOD_TYPE: "川菜", AREA_NAME: "中关村", LOOKING_FOR: ADDRESS}
#Task2 example: find a  resturant near beiyou.
    task2 = {TASK_ID:'124', STATUS: 'userTask', SYS_UTC:["Sys: 欢迎! 您可以根据菜系，价格和区域查找餐厅"], PRICE_RANGE: "50以上", LOOKING_FOR: SCORE}

    insertTask(task1)
    insertTask(task2)
    print taskdb.find_one({'taskId': '123'})
    res1 = {'venueName': 'LaoSichuan', 'foodType': 'Sichuan', 'address': "zhongguancun", 'phone': "110"}
    res2 = {'venueName': 'Shaxianxiaochi', 'foodType': 'shaxian', 'address': "Xi tu cheng no. 10", 'phone': "911"}
    res3 = {'venueName': 'LaoSichuan', 'foodType': 'Sichuan', 'address': "xiyatu", 'phone': "001"}
    #restaurantdb.insert(res1)
    #restaurantdb.insert(res2)
    #restaurantdb.insert(res3)

def loadRestaurantData():
    dropRestaurantDB()
    FILE = "./data/beijing_rest.json"
    data = []
    with codecs.open(FILE,'rU','utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    for restaurant in data:
        res = checkRestaurant(restaurant)
        restaurantdb.insert(res)

def getAllFoodType():
    from sets import Set

    foodTypesAll = list(restaurantdb.find({},{FOOD_TYPE:1, "_id":0}))
    foodTypes = Set()

    for x in foodTypesAll:
        foodTypes.add(x[FOOD_TYPE])

    for x in foodTypes:
        print "<option>" + x + "</option>"

def getAllAreaName():
    from sets import Set

    foodTypesAll = list(restaurantdb.find({},{AREA_NAME:1, "_id":0}))
    foodTypes = Set()

    for x in foodTypesAll:
        foodTypes.add(x[AREA_NAME])

    for x in foodTypes:
        print "<option>" + x + "</option>"

def testSearchDB():
    res = list(restaurantdb.find({AREA_NAME : {'$regex' : '.*' + '三元桥' + '.*'}}))
    for x in res:
        print x[AREA_NAME]

def loadTask():
    dropTaskDB()

    import re
    p = re.compile('\{(.*?)\}')
    File = "./data/task.test"
    file = open(File, "r")
    taskID = 1
    for line in file.readlines():
        user_goal = line
        lookFor = line.split("。")[-1]
        res = p.findall(lookFor)
        task = {TASK_ID: str(taskID), STATUS: 'userTask', SYS_UTC:["Sys: 欢迎! 您可以根据菜系，价格和区域查找餐厅"], USER_GOAL: user_goal}
        insertTask(task)
        taskID += 1
        print taskdb.find_one({'taskId': '123'})
        #print res[0]

def isValidKey(key):
    if len(key) == 0:
        return False
    if "不限" not in key:
        return True
    return False

def buildSearchKey(keyList):
    price = keyList[0]
    foodType = keyList[1]
    area = keyList[2]
    priceLowerBound = -1
    priceUpperBound = -1
    if "高于" in price:
        priceLowerBound = int(re.findall(r'\d+', price)[0])
        priceUpperBound = 9999999
        print priceLowerBound
    if "低于" in price:
        priceUpperBound = int(re.findall(r'\d+', price)[0])
        priceLowerBound = 0
        print priceUpperBound
    if "约" in price:
        center = int(re.findall(r'\d+', price)[0])
        priceLowerBound = center - 5
        if priceLowerBound < -1:
            priceLowerBound = 0
        priceUpperBound = center + 5

    #build search key
    key = {}
    if isValidKey(area):
        key[AREA_NAME] = {'$regex': '.*' + area + '.*'}
    if isValidKey(foodType):
        key[FOOD_TYPE] = foodType
    if priceLowerBound > -1:
        key[PRICE] = {'$gt':  priceLowerBound, '$lt': priceUpperBound}
    print key
    results = list(restaurantdb.find(key))
    return len(results)

def buildQueryKey():
    lenDist = {}
    import re
    p = re.compile('{(.*?)}')
    File = "./data/foo"
    file = open(File, "r")
    idx = 0
    for line in file.readlines():
        user_goal = line
        goal_change = ""
        constraint = line.split("。")[0]
        if len(line.split("。")) == 3:
            goal_change = line.split("。")[1]
        print constraint
        res = p.findall(constraint)
        resLen = buildSearchKey(res)
        #if resLen == 0 && len(goal_change) != 0:
        #    if "地点" in goal_change:
        #        res[2] = p.findall(goal_change)[0]
        #    if "菜试" in goal_change:
        #        res[1] = p.findall(goal_change)[1]

        if resLen in lenDist:
            lenDist[resLen].append(idx)
        else:
            lenDist[resLen] = [idx]
        idx += 1
    keys = lenDist.keys()
    print keys
    sorted(keys)
    for k in keys:
        print k, len(lenDist[k])

def chooseByColum(col):
    resAll = list(restaurantdb.find({},{col:1, "_id":0}))

    used = []
    for r in resAll:
        if r[col] not in used:
            print r[col], len(list(restaurantdb.find(r)))
            used.append(r[col])

if __name__=="__main__":
    #init()
    #resetWUtoUT()
    loadRestaurantData()
    #getAllFoodType()
    #getAllAreaName()
    #testSearchDB()
    #logging.basicConfig(filename='app.log',level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    #loadTask()
    #buildQueryKey()
    resetWWtoWT()
    #chooseByColum(FOOD_TYPE)
