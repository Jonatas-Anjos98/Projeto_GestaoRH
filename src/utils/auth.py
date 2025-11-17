"""
Gerenciador de autenticação e controle de acesso.
"""

from datetime import datetime
from typing import Optional
from src.models import Usuario, PerfilUsuario
from src.utils.database import DatabaseManager


class AuthManager:
    """Gerenciador de autenticação de usuários."""
    
    def __init__(self, db: DatabaseManager):
        """Inicializa o gerenciador de autenticação."""
        self.db = db
    
    def criar_usuario(self, nome: str, email: str, username: str, senha: str, perfil: str = PerfilUsuario.FUNCIONARIO.value) -> Optional[Usuario]:
        """Cria um novo usuário."""
        # Verifica se o username já existe
        if self.obter_usuario_por_username(username):
            return None
        
        # Verifica se o email já existe
        if self.obter_usuario_por_email(email):
            return None
        
        usuario = Usuario(
            nome=nome,
            email=email,
            username=username,
            perfil=perfil,
            ativo=True
        )
        
        usuario.definir_senha(senha)
        
        return self.db.criar_usuario(usuario)
    
    def autenticar(self, username: str, senha: str) -> Optional[Usuario]:
        """Autentica um usuário com username e senha."""
        usuario = self.obter_usuario_por_username(username)
        
        if usuario and usuario.ativo and usuario.verificar_senha(senha):
            # Atualiza o último acesso
            usuario.ultimo_acesso = datetime.now()
            self.db.atualizar_usuario(usuario)
            return usuario
        
        return None
    
    def obter_usuario_por_username(self, username: str) -> Optional[Usuario]:
        """Obtém um usuário pelo username."""
        return self.db.obter_usuario_por_username(username)
    
    def obter_usuario_por_email(self, email: str) -> Optional[Usuario]:
        """Obtém um usuário pelo email."""
        return self.db.obter_usuario_por_email(email)
    
    def obter_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """Obtém um usuário pelo ID."""
        return self.db.obter_usuario(usuario_id)
    
    def listar_usuarios(self, apenas_ativos: bool = True) -> list:
        """Lista todos os usuários."""
        return self.db.listar_usuarios(apenas_ativos)
    
    def atualizar_usuario(self, usuario: Usuario) -> bool:
        """Atualiza um usuário."""
        usuario.data_atualizacao = datetime.now()
        return self.db.atualizar_usuario(usuario)
    
    def deletar_usuario(self, usuario_id: int) -> bool:
        """Deleta um usuário (soft delete)."""
        return self.db.deletar_usuario(usuario_id)
    
    def alterar_senha(self, usuario_id: int, senha_atual: str, senha_nova: str) -> bool:
        """Altera a senha de um usuário."""
        usuario = self.obter_usuario(usuario_id)
        
        if not usuario or not usuario.verificar_senha(senha_atual):
            return False
        
        usuario.definir_senha(senha_nova)
        return self.atualizar_usuario(usuario)
    
    def redefinir_senha(self, usuario_id: int, nova_senha: str) -> bool:
        """Redefine a senha de um usuário (apenas admin)."""
        usuario = self.obter_usuario(usuario_id)
        
        if not usuario:
            return False
        
        usuario.definir_senha(nova_senha)
        return self.atualizar_usuario(usuario)
    
    def verificar_permissao(self, usuario: Usuario, acao: str) -> bool:
        """Verifica se um usuário tem permissão para realizar uma ação."""
        if not usuario or not usuario.ativo:
            return False
        
        return usuario.tem_permissao(acao)
