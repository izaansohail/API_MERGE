
import flask
from flask import request
from flask_pymongo import PyMongo
from pymongo import MongoClient
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app = flask.Flask(__name__)
app.config["DEBUG"] = True
#app.config['MONGO_DBNAME'] = 'Citizen'
#app.config["MONGO_URI"] = "mongodb+srv://usama:usama@izaan.0y3eq.mongodb.net/Citizen?retryWrites=true&w=majority"
client = MongoClient(
    "mongodb+srv://usama:usama@izaan.0y3eq.mongodb.net/Izaan?retryWrites=true&w=majority")


@app.route('/citizen', methods=['POST' , "PUT" , "GET"] )
def citizen():
    if request.method == "POST":
        data = request.get_json()
        #print(data)
        db = client['Citizen']
        citizenData = db.CitizenData
        citizenid = citizenData.insert_one(data)
        return {"citizenId" :str(citizenid.inserted_id) }
    
    if request.method == "GET":
        db = client['Citizen']
        citizenData = db.CitizenData
        citizens = citizenData.find()
        res=[]
        for citizen in citizens:
            print(citizen)
            citizen["_id"] = str(citizen["_id"])
            res.append(citizen)
        obj= {"citizens": res}
        print(type(obj), obj)
        return obj
    
    if request.method == "PUT":
        data = request.json
        cnic = request.get_json()["cnic"]
        print(cnic)
        db =  client['Citizen']
        citizenData = db.CitizenData
        reqcitizen = citizenData.find_one({"cnic": cnic})
        if reqcitizen == None :
            return {"error" : "could not find the cnic"}
        else:
            citizenid = citizenData.update_one(reqcitizen , {"$set": data})
            if  citizenid != None : 
                return  {"msg" :  "record Updated"}
            else :
                return {"msg" : "record cannot be updated"}


# D: \izaan\Work\University\university docs\Semester 5\Database Systems\Project\BackEnd

app.run(host="0.0.0.0")
