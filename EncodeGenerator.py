import os
import cv2
import face_recognition
import pickle
from supabase import create_client, Client
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Supabase config
url = "https://xwqlpoyihrjoogthsfuu.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3cWxwb3lpaHJqb29ndGhzZnV1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcyMjE2OSwiZXhwIjoyMDY5Mjk4MTY5fQ.T9HSGwlVHWYKxfADzlPjekcjt1iOrCMWS6r966fvcu4"  # 🔒 Replace with real key and keep it safe!
supabase: Client = create_client(url, key)
bucket_name = "attendance-images"

# Firebase config
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://faceattendencerealtime-e6285-default-rtdb.firebaseio.com/'
})

ref = db.reference('Students')

folderPath = 'Images'
pathList = os.listdir(folderPath)
print("Image files found:", pathList)

imgList = []
studentsIds = []

for path in pathList:
    img = cv2.imread(os.path.join(folderPath, path))
    imgList.append(img)
    student_id = os.path.splitext(path)[0]
    studentsIds.append(student_id)

    file_path = os.path.join(folderPath, path)
    file_ext = path.split('.')[-1]
    supabase_file_path = f"Images/{student_id}.{file_ext}"

    # Upload image to Supabase (only if not exists or you want to overwrite)
    with open(file_path, 'rb') as f:
        res = supabase.storage.from_(bucket_name).upload(
            supabase_file_path,
            f,
            {"content-type": f"image/{file_ext}"}
        )
    # Get public URL of uploaded image
    image_url = f"https://xwqlpoyihrjoogthsfuu.supabase.co/storage/v1/object/public/{bucket_name}/{supabase_file_path}"

    # Save student data to Firebase
    student_data = {
        "name": student_id,
        "major": "Robotics",
        "starting year": 2017,
        "total_attendence": 0,
        "standing": "G",
        "year": 4,
        "last_attendence_time": str(datetime.now()),
        "image_url": image_url
    }
    ref.child(student_id).set(student_data)

print("Student IDs processed:", studentsIds)

# ---------- Face Encoding ----------
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:  # Ensure at least one face found
            encodeList.append(encodings[0])
        else:
            print("⚠️ Face not found in image.")
    return encodeList

print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentsIds]
print("Encoding Complete.")

# Save encodings using pickle
with open("EncodeFile.p", "wb") as file:
    pickle.dump(encodeListKnownWithIds, file)
print("Encodings file saved as 'EncodeFile.p'")
