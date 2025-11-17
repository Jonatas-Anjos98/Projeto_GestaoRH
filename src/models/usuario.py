"""
Modelo de dados para Usuários.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from enum import Enum
import hashlib


class PerfilUsuario(Enum):
    """Perfis de usuários disponíveis."""
    ADMIN = "Administrador"
    GERENTE = "Gerente"
    RH = "Recursos Humanos"
    FUNCIONARIO = "Funcionário"


@dataclass
class Usuario:
    """Classe que representa um usuário do sistema."""
    
    id: Optional[int] = None
    nome: str = ""
    email: str = ""
    username: str = ""
    senha_hash: str = ""
    perfil: str = PerfilUsuario.FUNCIONARIO.value
    ativo: bool = True
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    ultimo_acesso: Optional[datetime] = None
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Cria um objeto Usuario a partir de um dicionário."""
        return cls(**data)
    
    @staticmethod
    def hash_senha(senha: str) -> str:
        """Gera o hash de uma senha usando SHA-256."""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def verificar_senha(self, senha: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return self.senha_hash == self.hash_senha(senha)
    
    def definir_senha(self, senha: str):
        """Define uma nova senha (armazenada como hash)."""
        self.senha_hash = self.hash_senha(senha)
    
    def tem_permissao(self, acao: str) -> bool:
        """Verifica se o usuário tem permissão para realizar uma ação."""
        permissoes = {
            PerfilUsuario.ADMIN.value: [
                "criar_usuario", "editar_usuario", "deletar_usuario",
                "criar_funcionario", "editar_funcionario", "deletar_funcionario",
                "criar_afastamento", "editar_afastamento", "deletar_afastamento",
                "gerar_relatorio", "exportar_dados", "backup", "configuracoes"
            ],
            PerfilUsuario.GERENTE.value: [
                "criar_funcionario", "editar_funcionario",
                "criar_afastamento", "editar_afastamento",
                "gerar_relatorio", "exportar_dados"
            ],
            PerfilUsuario.RH.value: [
                "criar_funcionario", "editar_funcionario", "deletar_funcionario",
                "criar_afastamento", "editar_afastamento", "deletar_afastamento",
                "gerar_relatorio", "exportar_dados"
            ],
            PerfilUsuario.FUNCIONARIO.value: [
                "visualizar_dados_pessoais", "solicitar_afastamento"
            ]
        }
        
        return acao in permissoes.get(self.perfil, [])
