from flask import Flask, render_template, request, redirect, session, flash
from firebase_config import firebase_login
import json
import os
from pyzbar.pyzbar import decode
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

HISTORICO_FILE = 'historico.json'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, 'r') as f:
            return json.load(f)
    return []


def salvar_historico(email, projeto):
    historico = carregar_historico()
    historico.append({'usuario': email, 'projeto': projeto})
    with open(HISTORICO_FILE, 'w') as f:
        json.dump(historico, f)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/auth', methods=['POST'])
def auth():
    email = request.form['email']
    senha = request.form['senha']
    if firebase_login(email, senha):
        session['user'] = email
        return redirect('/home')
    else:
        return render_template('login.html', erro='Email ou senha inválidos.')


@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')
    historico = carregar_historico()
    historico_usuario = [h for h in historico if h['usuario'] == session['user']]
    return render_template('home.html', historico=historico_usuario)


@app.route('/upload_qr', methods=['POST'])
def upload_qr():
    if 'user' not in session:
        return redirect('/')

    if 'qrfile' not in request.files:
        flash('Nenhum arquivo enviado.')
        return redirect('/home')

    file = request.files['qrfile']
    if file.filename == '':
        flash('Nome do arquivo inválido.')
        return redirect('/home')

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Tentar ler o QR Code
    try:
        image = Image.open(filepath)
        decoded = decode(image)
        if decoded:
            qr_data = decoded[0].data.decode('utf-8')
            salvar_historico(session['user'], qr_data)
            return redirect('/projeto')
        else:
            flash('QR Code não reconhecido.')
            return redirect('/home')
    except Exception as e:
        print("Erro ao processar imagem:", e)
        flash('Erro ao processar a imagem.')
        return redirect('/home')


@app.route('/projeto')
def projeto():
    if 'user' not in session:
        return redirect('/')
    return render_template('projeto.html')


@app.route('/visualizar/<tipo>')
def visualizar(tipo):
    if 'user' not in session:
        return redirect('/')
    salvar_historico(session['user'], tipo)
    return render_template('visualizar.html', tipo=tipo)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/ler_qr_camera')
def ler_qr_camera():
    if 'user' not in session:
        return redirect('/')
    return render_template('camera_qr.html')


if __name__ == '__main__':
    app.run(debug=True)
