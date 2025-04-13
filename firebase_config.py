import os
from dotenv import load_dotenv
import pyrebase

load_dotenv()  # Carrega variáveis do .env em DEV

firebase_config = {
    "apiKey": os.environ.get("FIREBASE_API_KEY"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.environ.get("FIREBASE_APP_ID"),
    "databaseURL": os.environ.get("FIREBASE_DB_URL")  # 🔥 ESSA É A MAIS IMPORTANTE AQUI
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

def firebase_login(email, senha):
    try:
        auth.sign_in_with_email_and_password(email, senha)
        return True
    except Exception as e:
        print("🔥 ERRO NO LOGIN FIREBASE:", e)
        return False
