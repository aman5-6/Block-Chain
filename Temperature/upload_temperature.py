import os
import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate('Link of the web service')

firebase_admin.initialize_app(cred)

db = firestore.client()

def upload_temperature_to_firestore(temperature):
    doc_ref = db.collection('temperatures').document()
    data = {
        'temperature': temperature,
        'timestamp': datetime.now().isoformat()
    }
    doc_ref.set(data)
    print(f'Temperature {temperature} uploaded successfully.')

def main():
    
    #current_temperature = 34.0
    current_temp = input("Enter the current temperature displayed :")
    current_temperature = float(current_temp)
    upload_temperature_to_firestore(current_temperature)

if __name__ == "__main__":
    main()
