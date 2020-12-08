import sys
import base64
import cv2
import os
import flask
from flask import request, send_from_directory, send_file
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
client = MongoClient(
    "mongodb+srv://usama:usama@izaan.0y3eq.mongodb.net/Izaan?retryWrites=true&w=majority")


@app.route('/citizen', methods=['POST' , "PUT" , "GET", "DELETE"] )
def citizen():
    if request.method == "POST":
        print("here")
        data = request.get_json()
        try:
            # creating a folder named data
            if not os.path.exists('data'):
                os.makedirs('data')
            # if not created then raise error
        except OSError:
            print('Error: Creating directory of data')

        #print(data)
        db = client['Citizen']
        citizenData = db.CitizenData
        cnic = request.get_json()["cnic"]
        f_image1 = open("./data/"+cnic+"-front.jpg", "wb")
        b64str = request.get_json()['image1_name']
        f_image1.write(base64.b64decode(b64str))
        f_image1.close()
        data["image1_name"] = "/data/"+cnic+"-front.jpg"

        f_image2 = open("./data/"+cnic+"-right.jpg", "wb")
        b64str = request.get_json()['image2_name']
        f_image2.write(base64.b64decode(b64str))
        f_image2.close()
        data["image2_name"] = "/data/"+cnic+"-right.jpg"

        f_image3 = open("./data/"+cnic+"-left.jpg", "wb")
        b64str = request.get_json()['image3_name']
        f_image3.write(base64.b64decode(b64str))
        f_image3.close()
        data["image3_name"] = "/data/"+cnic+"-left.jpg"
        citizenid = citizenData.insert_one(data)
        return {"citizenId" :str(citizenid.inserted_id) }
    
    if request.method == "GET":
        cnic = request.args.get('cnic')
        print(cnic)
        db = client['Citizen']
        citizenData = db.CitizenData
        reqcitizen = citizenData.find_one({"cnic": cnic})
        reqcitizen["_id"] = str(reqcitizen["_id"])
        obj= {"citizen": reqcitizen}
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

    if request.method == "DELETE":
        data = request.json
        cnic = request.get_json()["cnic"]
        print(cnic)
        db = client['Citizen']
        citizenData = db.CitizenData
        reqcitizen = citizenData.find_one({"cnic": cnic})
        if reqcitizen == None:
            return {"error": "could not find the cnic"}
        else:
            citizenid = citizenData.delete_one(reqcitizen)
            if  citizenid != None:
                return {"msg":  "record Deleted"}
            else:
                return {"msg": "record cannot be deleted"}


@app.route('/data/<path:path>')
def send_js(path):
    return send_file('./data/'+path, mimetype="image/jpg")

app.run(host="0.0.0.0")
