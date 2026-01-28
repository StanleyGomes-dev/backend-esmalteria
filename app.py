import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÃO DO BANCO DE DADOS (SQLite) ---
def init_db():
    conn = sqlite3.connect('agendamentos.db')
    cursor = conn.cursor()
    # Cria a tabela se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            whatsapp TEXT,
            servico TEXT NOT NULL,
            data TEXT NOT NULL,
            horario TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Roda a criação do banco assim que o Python liga
init_db()

# --- SEUS SERVIÇOS ---
servicos = [
    {'id': 1, 'nome': 'Manicure Simples', 'preco': 35},
    {'id': 2, 'nome': 'Pedicure Simples', 'preco': 35},
    {'id': 3, 'nome': 'Esmaltação em Gel', 'preco': 50},
    {'id': 4, 'nome': 'Banho de Gel', 'preco': 55},
    {'id': 5, 'nome': 'Molde F1 (Aplicação)', 'preco': 85},
    {'id': 6, 'nome': 'Gel na Tips (Aplicação)', 'preco': 90}
]

# --- ROTAS ---

@app.route('/api/servicos', methods=['GET'])
def get_servicos():
    return jsonify(servicos)

@app.route('/api/horarios', methods=['GET'])
def get_horarios():
    data_str = request.args.get('data')

    if not data_str:
        return jsonify({'mensagem': 'Data inválida', 'horarios_livres': []}), 400

    # Converte string para data
    try:
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'mensagem': 'Formato inválido', 'horarios_livres': []}), 400

    dia_semana = data_obj.weekday()

    # --- SUAS REGRAS DE HORÁRIO ---
    horarios_dia_util = ['09:00', '19:00']
    horarios_fim_semana = ['09:00', '11:00', '14:00', '16:00', '18:00']

    if dia_semana < 5:
        horarios_do_dia = horarios_dia_util
        msg = 'Horários de Semana (Restritos)'
    else:
        horarios_do_dia = horarios_fim_semana
        msg = 'Horários de Fim de Semana'

    # --- BUSCA OS OCUPADOS NO BANCO DE DADOS ---
    conn = sqlite3.connect('agendamentos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT horario FROM agendamentos WHERE data = ?", (data_str,))
    agendamentos_banco = cursor.fetchall()
    conn.close()

    # Transforma a lista do banco numa lista simples: ['09:00', '14:00']
    ocupados = [item[0] for item in agendamentos_banco]

    # 1. Filtra removendo os que já estão ocupados
    livres = [h for h in horarios_do_dia if h not in ocupados]

    # --- NOVO: FILTRO DE TEMPO REAL 🕒 ---
    # Só executa isso se a data for HOJE
    agora = datetime.now()
    hoje_str = agora.strftime('%Y-%m-%d') # Data de hoje (ex: 2026-01-24)
    hora_atual_str = agora.strftime('%H:%M') # Hora atual (ex: 12:30)

    if data_str == hoje_str:
        # Mantém apenas horários que são "maiores" que a hora atual
        livres = [h for h in livres if h > hora_atual_str]

    return jsonify({
        'mensagem': msg,
        'horarios_livres': livres
    })

@app.route('/api/agendar', methods=['POST'])
def salvar_agendamento():
    dados = request.json
    
    # --- SALVA NO BANCO DE DADOS ---
    conn = sqlite3.connect('agendamentos.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO agendamentos (cliente, whatsapp, servico, data, horario)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        dados.get('cliente'),
        dados.get('whatsapp'),
        dados.get('servico_id'), # Agora vai salvar o NOME se você ajustou o frontend
        dados.get('data'),
        dados.get('horario')
    ))
    conn.commit()
    conn.close()
    
    print(f"✅ Agendamento salvo no SQLite: {dados['cliente']}")
    return jsonify({'mensagem': 'Agendamento realizado com sucesso!'})

@app.route('/api/agendamentos', methods=['GET'])
def listar_agendamentos():
    # --- LÊ DO BANCO DE DADOS ---
    conn = sqlite3.connect('agendamentos.db')
    conn.row_factory = sqlite3.Row # Permite chamar as colunas pelo nome
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agendamentos ORDER BY data, horario")
    dados = cursor.fetchall()
    conn.close()
    
    # Converte os dados do banco para JSON pro Angular entender
    lista_formatada = []
    for linha in dados:
        lista_formatada.append({
            'id': linha['id'],
            'cliente': linha['cliente'],
            'whatsapp': linha['whatsapp'],
            'servico_id': linha['servico'],
            'data': linha['data'],
            'horario': linha['horario']
        })

    return jsonify(lista_formatada)

# ROTA DE LOGIN
@app.route('/api/login', methods=['POST'])
def login():
    dados = request.json
    usuario = dados.get('usuario')
    senha = dados.get('senha')

    # Aqui definimos a senha fixa (depois podemos melhorar)
    if usuario == 'admin' and senha == 'admin123':
        return jsonify({'mensagem': 'Login aprovado!', 'token': 'acesso-liberado'})
    else:
        return jsonify({'mensagem': 'Senha incorreta!'}), 401
    
    # ROTA PARA EXCLUIR AGENDAMENTO
@app.route('/api/agendamentos/<int:id>', methods=['DELETE'])
def excluir_agendamento(id):
    conn = sqlite3.connect('agendamentos.db')
    cursor = conn.cursor()
    
    # Deleta a linha que tem aquele ID específico
    cursor.execute("DELETE FROM agendamentos WHERE id = ?", (id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'mensagem': 'Agendamento excluído!'})

if __name__ == '__main__':
    app.run(debug=True)