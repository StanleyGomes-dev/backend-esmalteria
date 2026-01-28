import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- COLOCAR LOGO NO COMEÇO DO ARQUIVO, APÓS OS IMPORTS ---

def inicializar_banco():
    conn = sqlite3.connect('agendamentos.db')
    cursor = conn.cursor()
    
    # 1. Garante que a tabela de usuários existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    
    # 2. Verifica se o admin já existe
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", ('admin',))
    usuario = cursor.fetchone()
    
    # 3. Se não existir, cria o ADMIN padrão
    if not usuario:
        # ATENÇÃO: Aqui definimos a senha padrão 'admin123'
        cursor.execute("INSERT INTO usuarios (username, senha) VALUES (?, ?)", ('admin', 'admin123'))
        conn.commit()
        print("✅ Usuário ADMIN criado com sucesso!")
    
    conn.close()

# --- IMPORTANTE: CHAMAR A FUNÇÃO PARA ELA RODAR ---
inicializar_banco()

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
    usuario_form = dados.get('usuario')
    senha_form = dados.get('senha')

    # 1. Conecta no banco para conferir a senha
    conn = sqlite3.connect('agendamentos.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 2. Busca o usuário que a pessoa digitou
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (usuario_form,))
    usuario_banco = cursor.fetchone()
    conn.close()

    # 3. Verifica: O usuário existe? A senha bate?
    if usuario_banco and usuario_banco['senha'] == senha_form:
        return jsonify({
            'mensagem': 'Login aprovado!', 
            'token': 'acesso-liberado-vip',
            'usuario': usuario_banco['username']
        })
    else:
        return jsonify({'mensagem': 'Usuário ou senha incorretos!'}), 401
    
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