from pymongo import MongoClient

#TODO : Make this singleton with decorators ...
dbclient = MongoClient('localhost', 27017)
