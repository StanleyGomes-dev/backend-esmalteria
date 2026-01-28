import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("ERRO FATAL: Esqueceram de configurar o .env!")

# Cria a conexão única
supabase: Client = create_client(url, key)

def get_db():
    """Retorna o cliente do Supabase pronto para uso"""
    return supabase