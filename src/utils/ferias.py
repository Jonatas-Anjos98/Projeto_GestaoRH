"""
Sistema de cálculo automático de férias.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from src.models import Funcionario
from src.config import DIAS_FERIAS_ANUAL, MESES_PARA_FERIAS


class FeriasManager:
    """Gerenciador de cálculo de férias."""
    
    @staticmethod
    def calcular_dias_ferias_disponiveis(funcionario: Funcionario) -> int:
        """Calcula os dias de férias disponíveis para um funcionário."""
        if not funcionario.data_admissao:
            return 0
        
        # Calcula o tempo de serviço em meses
        agora = datetime.now()
        tempo_servico = (agora.year - funcionario.data_admissao.year) * 12
        tempo_servico += agora.month - funcionario.data_admissao.month
        
        # Verifica se o funcionário tem direito a férias
        if tempo_servico < MESES_PARA_FERIAS:
            return 0
        
        # Calcula o número de períodos completos de férias
        periodos_completos = tempo_servico // MESES_PARA_FERIAS
        
        # Calcula os dias de férias (30 dias por período)
        dias_totais = periodos_completos * DIAS_FERIAS_ANUAL
        
        return int(dias_totais)
    
    @staticmethod
    def calcular_dias_ferias_usados(funcionario: Funcionario, afastamentos: List) -> int:
        """Calcula os dias de férias já utilizados."""
        dias_usados = 0
        
        for afastamento in afastamentos:
            if afastamento.tipo == "Férias":
                dias_usados += afastamento.dias_afastamento()
        
        return dias_usados
    
    @staticmethod
    def calcular_dias_ferias_restantes(funcionario: Funcionario, afastamentos: List) -> int:
        """Calcula os dias de férias restantes."""
        disponíveis = FeriasManager.calcular_dias_ferias_disponiveis(funcionario)
        usados = FeriasManager.calcular_dias_ferias_usados(funcionario, afastamentos)
        
        return max(0, disponíveis - usados)
    
    @staticmethod
    def obter_proxima_data_ferias(funcionario: Funcionario) -> Optional[datetime]:
        """Obtém a próxima data em que o funcionário terá direito a férias."""
        if not funcionario.data_admissao:
            return None
        
        agora = datetime.now()
        tempo_servico = (agora.year - funcionario.data_admissao.year) * 12
        tempo_servico += agora.month - funcionario.data_admissao.month
        
        # Se já tem direito, retorna a data de hoje
        if tempo_servico >= MESES_PARA_FERIAS:
            return agora
        
        # Calcula a próxima data
        meses_faltantes = MESES_PARA_FERIAS - tempo_servico
        proxima_data = funcionario.data_admissao + timedelta(days=MESES_PARA_FERIAS * 30)
        
        return proxima_data
    
    @staticmethod
    def gerar_relatorio_ferias(funcionario: Funcionario, afastamentos: List) -> Dict:
        """Gera um relatório completo de férias para um funcionário."""
        disponíveis = FeriasManager.calcular_dias_ferias_disponiveis(funcionario)
        usados = FeriasManager.calcular_dias_ferias_usados(funcionario, afastamentos)
        restantes = FeriasManager.calcular_dias_ferias_restantes(funcionario, afastamentos)
        proxima_data = FeriasManager.obter_proxima_data_ferias(funcionario)
        
        return {
            'funcionario_id': funcionario.id,
            'funcionario_nome': funcionario.nome,
            'dias_disponiveis': disponíveis,
            'dias_usados': usados,
            'dias_restantes': restantes,
            'proxima_data_ferias': proxima_data.strftime('%d/%m/%Y') if proxima_data else 'N/A',
            'data_admissao': funcionario.data_admissao.strftime('%d/%m/%Y') if funcionario.data_admissao else 'N/A'
        }
    
    @staticmethod
    def validar_ferias(funcionario: Funcionario, data_inicio: datetime, data_fim: datetime, afastamentos: List) -> tuple:
        """Valida se um período de férias é válido."""
        dias_solicitados = (data_fim - data_inicio).days + 1
        dias_restantes = FeriasManager.calcular_dias_ferias_restantes(funcionario, afastamentos)
        
        if dias_solicitados > dias_restantes:
            return False, f"Funcionário tem apenas {dias_restantes} dias de férias disponíveis, mas solicitou {dias_solicitados} dias."
        
        # Verifica se há conflito com outros afastamentos
        for afastamento in afastamentos:
            if afastamento.data_inicio and afastamento.data_fim:
                # Verifica se há sobreposição
                if not (data_fim < afastamento.data_inicio or data_inicio > afastamento.data_fim):
                    return False, f"Há um conflito com outro afastamento ({afastamento.tipo}) no período solicitado."
        
        return True, "Férias validadas com sucesso."
