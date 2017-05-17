import os
from flask import Flask,render_template, request,json
import logging

app = Flask(__name__)

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
    taskId = 123
    foodType = "Sichuan food"
    priceRange = "don't care"
    address = "*"
    lookingFor = "address"
    global sents
    return render_template('user.html', taskId=taskId, foodType=foodType, priceRange=priceRange, address=address, lookingFor=lookingFor, sents=sents)

@app.route('/userUpdateTask', methods=['POST'])
def userUpdateTask():
    if request.method == "POST":
        print request
        content = request.get_json()
        print content
        taskId = content['taskId']
        userResponse = content['userResponse']
        print userResponse
        global sents
        sents.append("User: " + userResponse)
        #print taskId
        return json.dumps({'status':'OK','taskId': taskId, 'userResponse': userResponse})

#Wizard
@app.route('/newWizardTask')
def newWizardTask():
    taskId = 234
    global sents2
    return render_template('wizard.html', taskId=taskId, sents = sents2)
if __name__=="__main__":
    logging.basicConfig(filename='app.log',level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    app.run(host='0.0.0.0', port=9005, debug=True)
