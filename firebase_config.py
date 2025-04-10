import os

firebase_config = {
    "apiKey": os.environ.get("FIREBASE_API_KEY"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MSG_SENDER_ID"),
    "appId": os.environ.get("FIREBASE_APP_ID"),
    "databaseURL": os.environ.get("FIREBASE_DB_URL")
}

import pyrebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def firebase_login(email, senha):
    try:
        auth.sign_in_with_email_and_password(email, senha)
        return True
    except Exception as e:
        print("Erro no login:", e)
        return False
