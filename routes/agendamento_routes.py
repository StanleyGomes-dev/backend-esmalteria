from flask import Blueprint, jsonify, request
from controllers.agendamento_controller import calcular_horarios_disponiveis

# Cria um "mini-aplicativo" só para agendamentos
agendamento_bp = Blueprint('agendamento_bp', __name__)

@agendamento_bp.route('/api/horarios', methods=['GET'])
def get_horarios():
    # 1. Pega o dado da URL (ex: ?data=2026-01-20)
    data_recebida = request.args.get('data')
    
    # 2. Passa para o Controller pensar
    resposta = calcular_horarios_disponiveis(data_recebida)
    
    # 3. Verifica se o Controller devolveu um erro
    if "erro" in resposta:
        return jsonify(resposta), 400 # Código 400 = Bad Request (Erro do Cliente)
        
    return jsonify(resposta)