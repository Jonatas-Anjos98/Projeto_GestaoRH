"""
Sistema de backup automático de dados.
"""

import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class BackupManager:
    """Gerenciador de backup de dados."""
    
    def __init__(self, data_dir: str = "src/data", backup_dir: str = "backups"):
        """Inicializa o gerenciador de backup."""
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def criar_backup(self, descricao: str = "") -> Optional[str]:
        """Cria um backup completo dos dados."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Cria o diretório de backup
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copia todos os arquivos JSON
            for arquivo in self.data_dir.glob("*.json"):
                shutil.copy2(arquivo, backup_path / arquivo.name)
            
            # Cria um arquivo de metadados
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'descricao': descricao,
                'arquivos': [f.name for f in self.data_dir.glob("*.json")]
            }
            
            with open(backup_path / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)
            
            return str(backup_path)
        
        except Exception as e:
            print(f"Erro ao criar backup: {e}")
            return None
    
    def listar_backups(self) -> List[dict]:
        """Lista todos os backups disponíveis."""
        backups = []
        
        for backup_dir in sorted(self.backup_dir.iterdir(), reverse=True):
            if backup_dir.is_dir():
                metadata_file = backup_dir / "metadata.json"
                
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # Calcula o tamanho do backup
                        tamanho = sum(f.stat().st_size for f in backup_dir.glob("*"))
                        
                        backups.append({
                            'nome': backup_dir.name,
                            'caminho': str(backup_dir),
                            'timestamp': metadata.get('timestamp'),
                            'descricao': metadata.get('descricao', ''),
                            'arquivos': metadata.get('arquivos', []),
                            'tamanho': tamanho,
                            'tamanho_formatado': self._formatar_tamanho(tamanho)
                        })
                    except Exception as e:
                        print(f"Erro ao ler backup {backup_dir.name}: {e}")
        
        return backups
    
    def restaurar_backup(self, backup_name: str) -> bool:
        """Restaura um backup anterior."""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            return False
        
        try:
            # Cria um backup da situação atual antes de restaurar
            self.criar_backup(descricao="Backup automático antes de restauração")
            
            # Copia os arquivos do backup para o diretório de dados
            for arquivo in backup_path.glob("*.json"):
                if arquivo.name != "metadata.json":
                    shutil.copy2(arquivo, self.data_dir / arquivo.name)
            
            return True
        
        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            return False
    
    def deletar_backup(self, backup_name: str) -> bool:
        """Deleta um backup."""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            return False
        
        try:
            shutil.rmtree(backup_path)
            return True
        
        except Exception as e:
            print(f"Erro ao deletar backup: {e}")
            return False
    
    def limpar_backups_antigos(self, dias: int = 30) -> int:
        """Remove backups com mais de X dias."""
        from datetime import timedelta
        
        data_limite = datetime.now() - timedelta(days=dias)
        backups_deletados = 0
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                metadata_file = backup_dir / "metadata.json"
                
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        timestamp_str = metadata.get('timestamp')
                        if timestamp_str:
                            timestamp = datetime.fromisoformat(timestamp_str)
                            
                            if timestamp < data_limite:
                                self.deletar_backup(backup_dir.name)
                                backups_deletados += 1
                    
                    except Exception as e:
                        print(f"Erro ao processar backup {backup_dir.name}: {e}")
        
        return backups_deletados
    
    @staticmethod
    def _formatar_tamanho(bytes: int) -> str:
        """Formata um tamanho em bytes para um formato legível."""
        for unidade in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unidade}"
            bytes /= 1024.0
        
        return f"{bytes:.2f} TB"
