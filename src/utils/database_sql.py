"""
Gerenciador de banco de dados SQL usando SQLite.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from src.models import Funcionario, Afastamento, Usuario, PerfilUsuario


class DatabaseSQL:
    """Gerenciador de banco de dados SQL."""
    
    def __init__(self, db_path: str = "src/data/rh_control.db"):
        """Inicializa o gerenciador de banco de dados SQL."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._criar_tabelas()
    
    def _get_connection(self):
        """Obtém uma conexão com o banco de dados."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _criar_tabelas(self):
        """Cria as tabelas do banco de dados."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabela de Funcionários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS funcionarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                telefone TEXT NOT NULL,
                endereco TEXT NOT NULL,
                loja TEXT NOT NULL,
                data_admissao DATETIME,
                cargo TEXT NOT NULL,
                salario REAL,
                ativo BOOLEAN DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Afastamentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS afastamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funcionario_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                data_inicio DATETIME NOT NULL,
                data_fim DATETIME NOT NULL,
                motivo TEXT,
                observacoes TEXT,
                documento_anexo TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
            )
        """)
        
        # Tabela de Usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                perfil TEXT DEFAULT 'Funcionário',
                ativo BOOLEAN DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_acesso DATETIME
            )
        """)
        
        # Tabela de Notificações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notificacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                tipo TEXT DEFAULT 'info',
                lida BOOLEAN DEFAULT 0,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_leitura DATETIME,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        # Tabela de Logs de Auditoria
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                acao TEXT NOT NULL,
                tabela TEXT NOT NULL,
                registro_id INTEGER,
                dados_anteriores TEXT,
                dados_novos TEXT,
                data_acao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ============ OPERAÇÕES COM FUNCIONÁRIOS ============
    
    def criar_funcionario(self, funcionario: Funcionario) -> Funcionario:
        """Cria um novo funcionário."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO funcionarios 
            (nome, cpf, email, telefone, endereco, loja, data_admissao, cargo, salario, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            funcionario.nome,
            funcionario.cpf,
            funcionario.email,
            funcionario.telefone,
            funcionario.endereco,
            funcionario.loja,
            funcionario.data_admissao,
            funcionario.cargo,
            funcionario.salario,
            funcionario.ativo
        ))
        
        funcionario.id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return funcionario
    
    def obter_funcionario(self, funcionario_id: int) -> Optional[Funcionario]:
        """Obtém um funcionário pelo ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM funcionarios WHERE id = ?", (funcionario_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_funcionario(row)
        return None
    
    def listar_funcionarios(self, apenas_ativos: bool = True) -> List[Funcionario]:
        """Lista todos os funcionários."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if apenas_ativos:
            cursor.execute("SELECT * FROM funcionarios WHERE ativo = 1 ORDER BY nome")
        else:
            cursor.execute("SELECT * FROM funcionarios ORDER BY nome")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_funcionario(row) for row in rows]
    
    def atualizar_funcionario(self, funcionario: Funcionario) -> bool:
        """Atualiza um funcionário."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE funcionarios
            SET nome = ?, email = ?, telefone = ?, endereco = ?, loja = ?, cargo = ?, salario = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            funcionario.nome,
            funcionario.email,
            funcionario.telefone,
            funcionario.endereco,
            funcionario.loja,
            funcionario.cargo,
            funcionario.salario,
            funcionario.id
        ))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def deletar_funcionario(self, funcionario_id: int) -> bool:
        """Deleta um funcionário (soft delete)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE funcionarios SET ativo = 0, data_atualizacao = CURRENT_TIMESTAMP WHERE id = ?", (funcionario_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def obter_funcionario_por_cpf(self, cpf: str) -> Optional[Funcionario]:
        """Obtém um funcionário pelo CPF."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM funcionarios WHERE cpf = ? AND ativo = 1", (cpf,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_funcionario(row)
        return None
    
    # ============ OPERAÇÕES COM AFASTAMENTOS ============
    
    def criar_afastamento(self, afastamento: Afastamento) -> Afastamento:
        """Cria um novo afastamento."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO afastamentos 
            (funcionario_id, tipo, data_inicio, data_fim, motivo, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            afastamento.funcionario_id,
            afastamento.tipo,
            afastamento.data_inicio,
            afastamento.data_fim,
            afastamento.motivo,
            afastamento.observacoes
        ))
        
        afastamento.id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return afastamento
    
    def listar_afastamentos_por_funcionario(self, funcionario_id: int) -> List[Afastamento]:
        """Lista afastamentos de um funcionário."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM afastamentos WHERE funcionario_id = ? ORDER BY data_inicio DESC", (funcionario_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_afastamento(row) for row in rows]
    
    def listar_afastamentos_por_periodo(self, data_inicio: datetime, data_fim: datetime) -> List[Afastamento]:
        """Lista afastamentos em um período."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM afastamentos 
            WHERE data_inicio <= ? AND data_fim >= ?
            ORDER BY data_inicio
        """, (data_fim, data_inicio))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_afastamento(row) for row in rows]
    
    def atualizar_afastamento(self, afastamento: Afastamento) -> bool:
        """Atualiza um afastamento."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE afastamentos
            SET tipo = ?, data_inicio = ?, data_fim = ?, motivo = ?, observacoes = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            afastamento.tipo,
            afastamento.data_inicio,
            afastamento.data_fim,
            afastamento.motivo,
            afastamento.observacoes,
            afastamento.id
        ))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def deletar_afastamento(self, afastamento_id: int) -> bool:
        """Deleta um afastamento."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM afastamentos WHERE id = ?", (afastamento_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    # ============ OPERAÇÕES COM USUÁRIOS ============
    
    def criar_usuario(self, usuario: Usuario) -> Usuario:
        """Cria um novo usuário."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO usuarios 
            (nome, email, username, senha_hash, perfil, ativo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            usuario.nome,
            usuario.email,
            usuario.username,
            usuario.senha_hash,
            usuario.perfil,
            usuario.ativo
        ))
        
        usuario.id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return usuario
    
    def obter_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """Obtém um usuário pelo ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_usuario(row)
        return None
    
    def obter_usuario_por_username(self, username: str) -> Optional[Usuario]:
        """Obtém um usuário pelo username."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND ativo = 1", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_usuario(row)
        return None
    
    def obter_usuario_por_email(self, email: str) -> Optional[Usuario]:
        """Obtém um usuário pelo email."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE email = ? AND ativo = 1", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_usuario(row)
        return None
    
    def listar_usuarios(self, apenas_ativos: bool = True) -> List[Usuario]:
        """Lista todos os usuários."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if apenas_ativos:
            cursor.execute("SELECT * FROM usuarios WHERE ativo = 1 ORDER BY nome")
        else:
            cursor.execute("SELECT * FROM usuarios ORDER BY nome")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_usuario(row) for row in rows]
    
    def atualizar_usuario(self, usuario: Usuario) -> bool:
        """Atualiza um usuário."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE usuarios
            SET nome = ?, email = ?, perfil = ?, senha_hash = ?, ultimo_acesso = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            usuario.nome,
            usuario.email,
            usuario.perfil,
            usuario.senha_hash,
            usuario.ultimo_acesso,
            usuario.id
        ))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def deletar_usuario(self, usuario_id: int) -> bool:
        """Deleta um usuário (soft delete)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE usuarios SET ativo = 0, data_atualizacao = CURRENT_TIMESTAMP WHERE id = ?", (usuario_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    # ============ MÉTODOS AUXILIARES ============
    
    @staticmethod
    def _row_to_funcionario(row) -> Funcionario:
        """Converte uma linha do banco para um objeto Funcionario."""
        return Funcionario(
            id=row['id'],
            nome=row['nome'],
            cpf=row['cpf'],
            email=row['email'],
            telefone=row['telefone'],
            endereco=row['endereco'],
            loja=row['loja'],
            data_admissao=datetime.fromisoformat(row['data_admissao']) if row['data_admissao'] else None,
            cargo=row['cargo'],
            salario=row['salario'],
            ativo=bool(row['ativo']),
            data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
            data_atualizacao=datetime.fromisoformat(row['data_atualizacao']) if row['data_atualizacao'] else None
        )
    
    @staticmethod
    def _row_to_afastamento(row) -> Afastamento:
        """Converte uma linha do banco para um objeto Afastamento."""
        return Afastamento(
            id=row['id'],
            funcionario_id=row['funcionario_id'],
            tipo=row['tipo'],
            data_inicio=datetime.fromisoformat(row['data_inicio']) if row['data_inicio'] else None,
            data_fim=datetime.fromisoformat(row['data_fim']) if row['data_fim'] else None,
            motivo=row['motivo'],
            observacoes=row['observacoes'],
            documento_anexo=row['documento_anexo'],
            data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
            data_atualizacao=datetime.fromisoformat(row['data_atualizacao']) if row['data_atualizacao'] else None
        )
    
    @staticmethod
    def _row_to_usuario(row) -> Usuario:
        """Converte uma linha do banco para um objeto Usuario."""
        return Usuario(
            id=row['id'],
            nome=row['nome'],
            email=row['email'],
            username=row['username'],
            senha_hash=row['senha_hash'],
            perfil=row['perfil'],
            ativo=bool(row['ativo']),
            data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
            data_atualizacao=datetime.fromisoformat(row['data_atualizacao']) if row['data_atualizacao'] else None,
            ultimo_acesso=datetime.fromisoformat(row['ultimo_acesso']) if row['ultimo_acesso'] else None
        )
