import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://faceattendencerealtime-e6285-default-rtdb.firebaseio.com/'
})

ref = db.reference('Students')

# Save data
data={
    "123":
        {
            "name":"Samruddhi Shewale",
            "major":"Robotics",
            "starting year":2025,
            "total_attendence":6,
            "standing":"G",
            "year":4,
            "last_attendence_time":"2022-12-11 00:54:34",
            "image_url": "https://xwqlpoyihrjoogthsfuu.supabase.co/storage/v1/object/sign/attendance-images/Images/123.png?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV8yYjkyODQyYS1kNjNhLTQ1NDktYjM2NC05YTYzMGI3YmMwYzYiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJhdHRlbmRhbmNlLWltYWdlcy9JbWFnZXMvMTIzLnBuZyIsImlhdCI6MTc1NDA3MzA1MywiZXhwIjoxNzU0Njc3ODUzfQ.2FVSTMflIq1qz_xCvU9YySMfU9gvtwA4dhQdYuIMMcI"
        },
    "456":
        {
            "name": "MS Dnoni",
            "major": "Sports",
            "starting year": 2022,
            "total_attendence": 4,
            "standing": "G",
            "year": 4,
            "last_attendence_time": "2022-12-11 00:54:34", #this will get updated from our main code i.e. time
            "image_url":"https://xwqlpoyihrjoogthsfuu.supabase.co/storage/v1/object/sign/attendance-images/Images/456.png?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV8yYjkyODQyYS1kNjNhLTQ1NDktYjM2NC05YTYzMGI3YmMwYzYiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJhdHRlbmRhbmNlLWltYWdlcy9JbWFnZXMvNDU2LnBuZyIsImlhdCI6MTc1NDA3MzA4NiwiZXhwIjoxNzU0Njc3ODg2fQ.GWjllIGpgr8L6Flivau42HAZaxDGIdSRf1E5B1rR7hA"
        },
    "789":
        {
            "name": "Taylor Swift",
            "major": "Singing",
            "starting year": 2015,
            "total_attendence": 8,
            "standing": "G",
            "year": 4,
            "last_attendence_time": "2022-12-11 00:54:34",
            "image_url":"https://xwqlpoyihrjoogthsfuu.supabase.co/storage/v1/object/sign/attendance-images/Images/789.png?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV8yYjkyODQyYS1kNjNhLTQ1NDktYjM2NC05YTYzMGI3YmMwYzYiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJhdHRlbmRhbmNlLWltYWdlcy9JbWFnZXMvNzg5LnBuZyIsImlhdCI6MTc1NDA3MzExOSwiZXhwIjoxNzU0Njc3OTE5fQ.QM6wlN9r7Kpx8dp5g4cBd8_s2kvExrCsdzOPe6ZgfuA"
        }

}
for key,value in data.items():
    ref.child(key).set(value)
