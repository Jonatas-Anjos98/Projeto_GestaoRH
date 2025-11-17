"""
Modelo de dados para Funcionários.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Funcionario:
    """Classe que representa um funcionário."""
    
    id: Optional[int] = None
    nome: str = ""
    cpf: str = ""
    email: str = ""
    telefone: str = ""
    endereco: str = ""
    loja: str = ""
    data_admissao: Optional[datetime] = None
    cargo: str = ""
    salario: float = 0.0
    ativo: bool = True
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Cria um objeto Funcionario a partir de um dicionário."""
        return cls(**data)
