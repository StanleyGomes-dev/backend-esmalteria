from dataclasses import dataclass

@dataclass
class Servico:
    id: int
    nome: str
    preco: float
    descricao: str = None  # Opcional

    def to_dict(self):
        """Converte o objeto da Classe para um dicionário (JSON)"""
        return {
            "id": self.id,
            "nome": self.nome,
            "preco": self.preco,
            "descricao": self.descricao
        }