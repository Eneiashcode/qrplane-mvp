from flask import Flask, render_template, request, redirect, session, flash, jsonify, send_from_directory
from firebase_config import firebase_login
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

HISTORICO_FILE = 'historico.json'


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


@app.route('/projeto')
def projeto():
    if 'user' not in session:
        return redirect('/')

    historico = carregar_historico()
    projetos_usuario = [h for h in historico if h['usuario'] == session['user']]
    if not projetos_usuario:
        return "Nenhum projeto encontrado."

    ultimo_projeto = projetos_usuario[-1]['projeto']
    projeto_id = ultimo_projeto.split("://")[-1]
    pasta = f'projetos/{projeto_id}'

    arquivos = {
        'pdf': f'{pasta}/planta.pdf',
        'imagem': f'{pasta}/imagem3d.png',
        'tabela': f'{pasta}/blocos.xlsx',
        'video': f'{pasta}/video.mp4'
    }

    return render_template('projeto.html', arquivos=arquivos, projeto_nome=projeto_id)


@app.route('/visualizar/<tipo>')
def visualizar(tipo):
    if 'user' not in session:
        return redirect('/')
    salvar_historico(session['user'], tipo)
    return render_template('visualizar.html', tipo=tipo)


@app.route('/ler_qr_camera')
def ler_qr_camera():
    if 'user' not in session:
        return redirect('/')
    return render_template('camera_qr.html')


@app.route('/salvar_qr_lido', methods=['POST'])
def salvar_qr_lido():
    if 'user' not in session:
        return redirect('/')
    data = request.get_json()
    qr_data = data.get('qr_data')
    if qr_data:
        salvar_historico(session['user'], qr_data)
        return redirect('/projeto')
    return jsonify({'error': 'QR inválido'}), 400


@app.route('/projetos/<path:filename>')
def arquivos_projeto(filename):
    return send_from_directory('projetos', filename)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
