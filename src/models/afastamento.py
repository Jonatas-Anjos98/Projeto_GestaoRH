"""
Modelo de dados para Afastamentos.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from enum import Enum


class TipoAfastamento(Enum):
    """Tipos de afastamento disponíveis."""
    ATESTADO_MEDICO = "Atestado Médico"
    FERIAS = "Férias"
    LICENCA_MATERNIDADE = "Licença-Maternidade"
    FALTA = "Falta"
    LICENCA_PATERNIDADE = "Licença-Paternidade"
    LICENCA_LUTO = "Licença por Luto"
    OUTRO = "Outro"


@dataclass
class Afastamento:
    """Classe que representa um afastamento de funcionário."""
    
    id: Optional[int] = None
    funcionario_id: int = 0
    tipo: str = ""
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    motivo: str = ""
    observacoes: str = ""
    documento_anexo: Optional[str] = None
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Cria um objeto Afastamento a partir de um dicionário."""
        return cls(**data)
    
    def dias_afastamento(self) -> int:
        """Calcula o número de dias de afastamento."""
        if self.data_inicio and self.data_fim:
            return (self.data_fim - self.data_inicio).days + 1
        return 0
