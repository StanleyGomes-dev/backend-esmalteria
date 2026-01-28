from flask import Blueprint, jsonify
from controllers.servico_controller import listar_todos_servicos

# Cria um "mini-aplicativo" (Blueprint) só para serviços
servico_bp = Blueprint('servico_bp', __name__)

@servico_bp.route('/api/servicos', methods=['GET'])
def get_servicos():
    # O Garçom (Rota) apenas chama o Chefe (Controller)
    resultado = listar_todos_servicos()
    
    # E entrega o prato para o cliente (JSON)
    return jsonify(resultado)