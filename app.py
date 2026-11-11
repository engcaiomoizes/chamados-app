from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import sqlite3
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__, static_folder='static')

app.secret_key = os.getenv('SECRET_KEY', 'INSECURE-DEFAULT-KEY')

DB_PATH = 'data/chamados.db'

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de chamados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            requester TEXT NOT NULL,
            assigned_to TEXT,
            sla TEXT NOT NULL,
            solution TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Criar um usuário padrão de TI se não existir (admin / admin123)
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('admin123')
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            ('admin', hashed_pw)
        )

    conn.commit()
    conn.close()

# Middleware simples para verificar se o usuário está logado
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Não autorizado'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Rotas de Autenticação
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['username'] = username
        return jsonify({'status': 'success', 'username': username})

    return jsonify({'error': 'Usuário ou senha incorretos.'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'logged_out'})

@app.route('/api/me', methods=['GET'])
def me():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'username': session.get('username')})
    return jsonify({'logged_in': False})

# Rota para servir a interface web
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Endpoints REST API
@app.route('/api/chamados', methods=['GET'])
def get_chamados():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chamados ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/chamados', methods=['POST'])
def add_chamado():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chamados (title, description, category, priority, status, requester, assigned_to, sla) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['title'],
        data['description'],
        data['category'],
        data['priority'],
        data.get('status', 'Aberto'),
        data['requester'],
        data.get('assigned_to', 'Não atribuído'),
        data.get('sla', '4h')
    ))
    conn.commit()
    chamado_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': chamado_id, 'status': 'success'}), 201

@app.route('/api/chamados/<int:id>', methods=['PUT'])
def edit_chamado(id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE chamados 
        SET title = ?, description = ?, requester = ?, assigned_to = ?, 
            category = ?, priority = ?, sla = ? 
        WHERE id = ?
    ''', (
        data['title'],
        data.get('description', ''),
        data['requester'],
        data.get('assigned_to', 'Não atribuído'),
        data['category'],
        data['priority'],
        data['sla'],
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'updated'})

@app.route('/api/chamados/<int:id>/status', methods=['PATCH'])
def update_status(id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE chamados SET status = ?, solution = ? WHERE id = ?',
        (data['status'], data['solution'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({'status', 'updated'})

@app.route('/api/chamados/<int:id>/priority', methods=['PATCH'])
def update_priority(id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE chamados SET priority = ? WHERE id = ?',
        (data['priority'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'updated'})

@app.route('/api/chamados/<int:id>', methods=['DELETE'])
def delete_chamado(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chamados WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'status', 'deleted'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)