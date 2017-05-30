#-*-coding:utf-8-*-
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
restdb = client['restdb']
restdb.tasks.drop()
restdb.restaurant.drop()

#call bash
bashCommand = "mongorestore db/backups/20170530/"
import subprocess
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()