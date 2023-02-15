import json


with open('parameters.json') as json_file:

    data = json.load(json_file)
    databaseP = data['database']
    email = data['mailLogin']
    hostDB = databaseP['host']
    userDB = databaseP['user']
    passwordDB = databaseP['password']
    database = databaseP['database']

    