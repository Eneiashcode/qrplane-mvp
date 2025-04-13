from flask import Flask, render_template, request, redirect, session, flash, jsonify, send_from_directory
from firebase_config import firebase_login, db
from datetime import datetime
import pytz
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# 🔄 Carrega histórico do Firebase
def carregar_historico(email):
    try:
        raw = db.child("historico").child(email.replace('.', '_')).get()
        dados = raw.val() or {}
        projetos = list(dados.values())
        ultimos = {}
        for h in projetos:
            ultimos[h["projeto"]] = h["timestamp"]
        historico = [{"projeto": p, "timestamp": ultimos[p]} for p in ultimos]
        historico.sort(key=lambda x: x["timestamp"], reverse=True)
        return historico
    except Exception as e:
        print("❌ Erro ao carregar histórico do Firebase:", e)
        return []

# 🔄 Salva histórico no Firebase
def salvar_historico(email, projeto):
    fuso_brasil = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_brasil).strftime('%d/%m/%Y %H:%M')
    data = {
        'projeto': projeto,
        'timestamp': agora
    }
    db.child("historico").child(email.replace('.', '_')).push(data)

# 🔐 Login
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

# 🏠 Tela inicial (home)
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')
    historico = carregar_historico(session['user'])
    return render_template('home.html', historico=historico)

# 📂 Tela do projeto
@app.route('/projeto')
def projeto():
    if 'user' not in session:
        return redirect('/')
    historico = carregar_historico(session['user'])
    if not historico:
        return "Nenhum projeto encontrado."
    ultimo_projeto = historico[-1]['projeto']
    projeto_id = ultimo_projeto.split("://")[-1]
    pasta = f'projetos/{projeto_id}'
    arquivos = {
        'pdf': f'{pasta}/planta.pdf',
        'imagem': f'{pasta}/imagem3d.png',
        'tabela': f'{pasta}/blocos.xlsx',
        'video': f'{pasta}/video.mp4'
    }
    return render_template('projeto.html', arquivos=arquivos, projeto_nome=projeto_id)

# 🔍 Visualizar tipo de projeto
@app.route('/visualizar/<tipo>')
def visualizar(tipo):
    if 'user' not in session:
        return redirect('/')
    salvar_historico(session['user'], tipo)
    return render_template('visualizar.html', tipo=tipo)

# 📷 Leitura via câmera
@app.route('/ler_qr_camera')
def ler_qr_camera():
    if 'user' not in session:
        return redirect('/')
    return render_template('camera_qr.html')

# ✅ Salvar leitura de QRCode
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

# 📁 Servir arquivos do projeto (corrigido)
@app.route('/projetos/<path:filename>')
def arquivos_projeto(filename):
    return send_from_directory('projetos', filename)

# 🔒 Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ↩ Abrir projeto do histórico
@app.route('/abrir_projeto', methods=['POST'])
def abrir_projeto():
    if 'user' not in session:
        return redirect('/')
    projeto = request.form.get('projeto')
    if projeto:
        salvar_historico(session['user'], projeto)
        return redirect('/projeto')
    return redirect('/home')

# 🚀 Roda app localmente ou no Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
