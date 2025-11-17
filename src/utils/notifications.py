"""
Sistema de notificações da aplicação.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path
import json
from src.models import Afastamento
from src.utils.database import DatabaseManager


class NotificationManager:
    """Gerenciador de notificações."""
    
    def __init__(self, db: DatabaseManager, data_dir: str = "src/data"):
        """Inicializa o gerenciador de notificações."""
        self.db = db
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.notifications_file = self.data_dir / "notificacoes.json"
        
        # Inicializa o arquivo se não existir
        if not self.notifications_file.exists():
            self._save_json([])
    
    def _load_json(self) -> List:
        """Carrega notificações do arquivo JSON."""
        try:
            with open(self.notifications_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_json(self, data: List):
        """Salva notificações em arquivo JSON."""
        with open(self.notifications_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, default=str)
    
    def criar_notificacao(self, usuario_id: int, titulo: str, mensagem: str, tipo: str = "info") -> dict:
        """Cria uma nova notificação."""
        notificacoes = self._load_json()
        
        novo_id = max([n.get('id', 0) for n in notificacoes], default=0) + 1
        
        notificacao = {
            'id': novo_id,
            'usuario_id': usuario_id,
            'titulo': titulo,
            'mensagem': mensagem,
            'tipo': tipo,  # info, warning, error, success
            'lida': False,
            'data_criacao': datetime.now().isoformat(),
            'data_leitura': None
        }
        
        notificacoes.append(notificacao)
        self._save_json(notificacoes)
        
        return notificacao
    
    def obter_notificacoes(self, usuario_id: int, apenas_nao_lidas: bool = False) -> List[dict]:
        """Obtém notificações de um usuário."""
        notificacoes = self._load_json()
        
        resultado = []
        for notif in notificacoes:
            if notif.get('usuario_id') == usuario_id:
                if apenas_nao_lidas and notif.get('lida'):
                    continue
                resultado.append(notif)
        
        return sorted(resultado, key=lambda x: x['data_criacao'], reverse=True)
    
    def marcar_como_lida(self, notificacao_id: int) -> bool:
        """Marca uma notificação como lida."""
        notificacoes = self._load_json()
        
        for notif in notificacoes:
            if notif.get('id') == notificacao_id:
                notif['lida'] = True
                notif['data_leitura'] = datetime.now().isoformat()
                self._save_json(notificacoes)
                return True
        
        return False
    
    def deletar_notificacao(self, notificacao_id: int) -> bool:
        """Deleta uma notificação."""
        notificacoes = self._load_json()
        notificacoes = [n for n in notificacoes if n.get('id') != notificacao_id]
        self._save_json(notificacoes)
        return True
    
    def gerar_notificacoes_afastamentos(self, dias_antes: int = 7):
        """Gera notificações para afastamentos próximos."""
        funcionarios = self.db.listar_funcionarios(apenas_ativos=True)
        
        data_limite = datetime.now() + timedelta(days=dias_antes)
        
        for funcionario in funcionarios:
            afastamentos = self.db.listar_afastamentos_por_funcionario(funcionario.id)
            
            for afastamento in afastamentos:
                if afastamento.data_inicio:
                    dias_restantes = (afastamento.data_inicio - datetime.now()).days
                    
                    if 0 < dias_restantes <= dias_antes:
                        titulo = f"Afastamento próximo: {afastamento.tipo}"
                        mensagem = f"{funcionario.nome} terá um afastamento ({afastamento.tipo}) em {dias_restantes} dia(s) ({afastamento.data_inicio.strftime('%d/%m/%Y')})"
                        
                        # Cria notificação para gerentes e RH
                        usuarios_rh = self.db.listar_usuarios(apenas_ativos=True)
                        for usuario in usuarios_rh:
                            if usuario.perfil in ["Gerente", "Recursos Humanos", "Administrador"]:
                                self.criar_notificacao(usuario.id, titulo, mensagem, "warning")
    
    def limpar_notificacoes_antigas(self, dias: int = 30):
        """Remove notificações lidas com mais de X dias."""
        notificacoes = self._load_json()
        
        data_limite = datetime.now() - timedelta(days=dias)
        
        notificacoes_filtradas = []
        for notif in notificacoes:
            data_criacao = datetime.fromisoformat(notif['data_criacao'])
            
            # Mantém notificações não lidas ou recentes
            if not notif.get('lida') or data_criacao > data_limite:
                notificacoes_filtradas.append(notif)
        
        self._save_json(notificacoes_filtradas)
