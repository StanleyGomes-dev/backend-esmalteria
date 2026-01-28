from config.database import get_db
from models.servico import Servico

def listar_todos_servicos():
    """
    Busca os dados no banco, valida usando a Classe e retorna a lista pronta.
    """
    try:
        # 1. Chama o Gerente de Banco para pegar a conexão
        db = get_db()
        
        # 2. Executa a busca no Supabase (SELECT * FROM tb_servicos)
        response = db.table("tb_servicos").select("*").execute()
        
        # 3. A Mágica do MVC (Conversão)
        lista_final = []
        
        for item in response.data:
            # Aqui transformamos o dicionário "bruto" do banco em um Objeto Python seguro
            servico_obj = Servico(
                id=item['id'],
                nome=item['nome'],
                preco=item['preco'],
                descricao=item.get('descricao') # Usa .get() para não dar erro se vier vazio
            )
            # Adicionamos na lista já convertido para dicionário limpo
            lista_final.append(servico_obj.to_dict())

        return lista_final

    except Exception as e:
        print(f"Erro ao buscar serviços: {e}")
        return {"erro": "Falha no sistema ao buscar serviços."}