import os
from dotenv import load_dotenv
import pyrebase

# 🔄 Carrega variáveis do arquivo .env (somente em ambiente local)
load_dotenv()

# ✅ Configurações do Firebase (via variáveis de ambiente)
firebase_config = {
    "apiKey": os.environ.get("FIREBASE_API_KEY"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.environ.get("FIREBASE_APP_ID"),
    "databaseURL": os.environ.get("FIREBASE_DB_URL")
}

# ✅ Inicializa Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# 🔐 Função de login
def firebase_login(email, senha):
    try:
        auth.sign_in_with_email_and_password(email, senha)
        return True
    except Exception as e:
        print("🔥 ERRO NO LOGIN FIREBASE:", e)
        return False
