#*********URL expires within a week so update the link of the url in fb.py also
import cv2 #to use camera
import os
import pickle
import face_recognition
import numpy as np
import cvzone
from supabase import create_client, Client
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime


# Supabase config
url = "https://xwqlpoyihrjoogthsfuu.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3cWxwb3lpaHJqb29ndGhzZnV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3MjIxNjksImV4cCI6MjA2OTI5ODE2OX0.Qvd4xp4YhrFs6GETHc8mwACYzYWqiteu81tjU9i0tBY"  # 🔒 Replace with real key and keep it safe!
supabase: Client = create_client(url, key)
bucket_name = "attendance-images"

# Firebase config
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://faceattendencerealtime-e6285-default-rtdb.firebaseio.com/'
})

bucket=supabase.storage.from_('attendance-images')

cap=cv2.VideoCapture(0)
cap.set(3,640) #get width of camera
cap.set(4,480) #height . we are using graphics and graphics are based on these dimensions

imgBackground=cv2.imread('Resources/background.png')

#Importing the mode images into a list
folderModePath='Resources/Modes'
modePathList= os.listdir(folderModePath)
imgModeList=[]
loadingCounter = 0
studentInfo = {}  # move this up to avoid undefined later

#print(modePathList)
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
    #print(len(imgModeList))#commenting because it will run again if we run it

#Load the  encoding file
print("Loading encode file...")
file=open('EncodeFile.p','rb')
encodeListKnownWithIds=pickle.load(file) #this will add all the info in encodeListKnownWithIds
file.close()
encodeListKnown,studentIds=encodeListKnownWithIds
#print(studentIds)
print("Encode file loaded")

modeType = 0
counter=0
id=0
imgStudent=[]

while True:
    success, img=cap.read()

    imgS=cv2.resize(img,(0,0),None,0.25,0.25)#make the image small
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame=face_recognition.face_locations(imgS)
    encodeCurframe=face_recognition.face_encodings(imgS,faceCurFrame)#here in () we are giving the img and its locatio so it will compare curr img with the old img from usiing its address


    imgBackground[162:162+480,55:55+640]=img #overlayed webcam img on our graphics
   # cv2.imshow("Webcam", img) now no need of this because in reall time we get our face on graphics itself with help of above line
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]#in place of 0 we can add 1,2 or 3 also as it will have the 4 modes we can use

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurframe,faceCurFrame):
            matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis=face_recognition.face_distance(encodeListKnown,encodeFace)
           # print("matches:",matches)
           # print("faceDistance:",faceDis)

            matchIndex=np.argmin(faceDis)#it gives the count or we can say if mine img is stored first in list and i go in front of camera it will give value zero
            #print("Match Index",matchIndex)

            if matches[matchIndex]: #it checks if face detected or not first
                #print("Known faces detected")
                #print(studentIds[matchIndex])
                y1,x2,y2,x1=faceLoc
                y1, x2, y2, x1 =y1*4,x2*4,y2*4,x1*4  #we multiplied it by 4 as we were reducing it by 4 ,hence it will fit properly
                bbox=55+x1,162+y1,x2-x1,y2-y1 #bbox is nothing but the bounding box in our camera window or its similar to the incomplete box we get while clicking picture so that the person is visible clearly
                imgBackground=cvzone.cornerRect(imgBackground,bbox,rt=0)#cvzone prvides its rectangular frame so we take it from there and rt is rectangle thickness
                id=studentIds[matchIndex]

                if counter ==0:
                    cvzone.putTextRect(imgBackground,"Loading",(275,400))
                    cv2.imshow("Face Attendence", imgBackground)
                    cv2.waitKey(1)
                    counter=1
                    modeType=1
        if counter!=0:


           if counter ==1:
               #Get the data
                studentInfo=db.reference(f'Students/{id}').get()
                print(studentInfo)
           # Download image binary from Supabase Storage
           # Try both .jpg and .png extensions
                image_path_jpg = f"Images/{id}.jpg"
                image_path_png = f"Images/{id}.png"

                try:
                    try:
                        response = supabase.storage.from_("attendance-images").download(image_path_jpg)
                    except Exception:
                        response = supabase.storage.from_("attendance-images").download(image_path_png)

                    array = np.frombuffer(response, np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(f"❌ Failed to load image for {id}: {e}")
                    imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)  # fallback: blank image


               # Convert to numpy and decode
                array = np.frombuffer(response, np.uint8)
                imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
           #update data of attendance
                #see here  iam keeping the updation time 3 second only as iam testing later u can do it for 24 hours
                #********AGAIN REPEATING IN THIS CODE IAM DOING ONLY FOR TESTING BUT TO DO IN REAL TIME I NEED TO UPDATE THE TIME TO 24 HOURS SO EACH LINE IN THIS SNIPPET CHANGES
                last_attendance_time = studentInfo.get('last_attendence_time')

                if last_attendance_time:
                    date_timeObject = datetime.strptime(last_attendance_time, "%Y-%m-%d %H:%M:%S")
                else:
                    date_timeObject = datetime.strptime("2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")  # or use datetime.min

                secondsElapsed=(datetime.now()-date_timeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed >30:
                    ref=db.reference(f'Students/{id}')
                        # Increment attendance
                    studentInfo['total_attendence'] += 1

                        # Update back to database
                    db.reference(f'Students/{id}').update({
                        'total_attendence': studentInfo['total_attendence'],
                        'last_attendence_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

                    ref.child('total_attendence').set(studentInfo['total_attendence'])
                    ref.child('last_attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  #it converting into sec instead of getting the value in thoudands
                else:
                    modeType=3
                    counter=0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
           if modeType!=3:
            if 10<counter<20:
                modeType=2

            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            if counter<=10:
                cv2.putText(imgBackground,str(studentInfo['total_attendence']),(861,125),
                        cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(id), (1006, 493),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo.get('starting year', 'N/A')), (1125, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                (w,h),_=cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                offset=(414-w)//2 #// because it might not be a integer it can be float
                cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                if imgStudent is not None:
                    imgStudent = cv2.resize(imgStudent, (216, 216))  # Resize to fit the background slot
                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

            counter+=1

            if counter>=20:
                counter=0
                modeType=0
                studentInfo=[]
                imgStudent=[]
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType=0
        counter=0

    #cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendence",imgBackground)
    cv2.waitKey(1)













