import sys
import base64
import cv2
import os
from PIL import Image
import PIL
import face_recognition
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
        #f_image1 = f_image1.save("./data/"+cnic+"-front.jpg", optimize=True, quality=30)
        b64str = request.get_json()['image1_name']
        f_image1.write(base64.b64decode(b64str))
        f_image1.close()
        data["image1_name"] = "/data/"+cnic+"-front.jpg"

        f_image2 = open("./data/"+cnic+"-right.jpg", "wb")
        #f_image2 = f_image2.save("./data/"+cnic+"-front.jpg", optimize=True, quality=30)
        b64str = request.get_json()['image2_name']
        f_image2.write(base64.b64decode(b64str))
        f_image2.close()
        data["image2_name"] = "/data/"+cnic+"-right.jpg"

        f_image3 = open("./data/"+cnic+"-left.jpg", "wb")
        #f_image3 = f_image3.save("./data/"+cnic+"-front.jpg", optimize=True, quality=30)
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

@app.route('/facematch', methods=['POST'] )
def facematch():
    if request.method == "POST":
        data = request.get_json()
        try:
            # creating a folder named data
            if not os.path.exists('video'):
                os.makedirs('video')
            # if not created then raise error
        except OSError:
            print('Error: Creating directory of data')

        db = client['Citizen']
        citizenData = db.CitizenData
        f_video = open("./video/video.mp4", "wb")
        b64str = request.get_json()['videoData']
        f_video.write(base64.b64decode(b64str))
        f_video.close()
        path = './video/video.mp4'
        pathdb = './data'
            
        cam = cv2.VideoCapture(path)

        while(True):
            # reading from frame
            found = False
            foundfilename = ""
            ret, frame = cam.read()
            if ret:
                f_face_encoding = face_recognition.face_encodings(frame)
                if(len(f_face_encoding) == 0):
                    print("f_face_encoding empty")
                    continue
                else:
                    print("f_face_encoding not empty")
                    f_face_encoding = f_face_encoding[0]
                    for filename in os.listdir(pathdb):
                        image_of_emp = face_recognition.load_image_file(os.path.join(pathdb, filename))
                        emp_face_encoding = face_recognition.face_encodings(image_of_emp)
                        if(len(emp_face_encoding) == 0):
                            continue
                        else:
                            emp_face_encoding = emp_face_encoding[0]
          
                        match = face_recognition.compare_faces([emp_face_encoding], f_face_encoding, 0.55)
                        print(match)
                        if(match[0] == True):
                            print("Match Found")
                            found = True
                            foundfilename = filename
                            break
                        else:
                            print("Match not found")     

                if(found == True):
                    break        
                else:
                    break
        
        # Release all space and windows once done
        cam.release()
        cv2.destroyAllWindows()
        cnic = foundfilename.split("-")
        if(len(cnic) > 0):
            print("CNIC: " + str(cnic[0]))
            return {"Cnic": cnic[0]}
        else:
            return {"Cnic": None}

    if request.method == "GET":
        cnic=request.args.get('cnic')
        print(cnic)
        db=client['Citizen']
        citizenData=db.CitizenData
        reqcitizen=citizenData.find_one({"cnic": cnic})
        reqcitizen["_id"]=str(reqcitizen["_id"])
        obj={"citizen": reqcitizen}
        print(type(obj), obj)
        return obj
        
app.run(host="0.0.0.0")
