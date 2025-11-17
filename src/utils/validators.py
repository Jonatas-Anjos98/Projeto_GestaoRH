"""
Utilitários para validação de dados.
"""

import re
from datetime import datetime


class Validators:
    """Classe com métodos estáticos para validação."""
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida um CPF."""
        # Remove caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)
        
        # CPF deve ter 11 dígitos
        if len(cpf) != 11:
            return False
        
        # CPF não pode ter todos os dígitos iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Valida o primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 > 9 else digito1
        
        if int(cpf[9]) != digito1:
            return False
        
        # Valida o segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 > 9 else digito2
        
        if int(cpf[10]) != digito2:
            return False
        
        return True
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida um email."""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None
    
    @staticmethod
    def validar_telefone(telefone: str) -> bool:
        """Valida um telefone."""
        # Remove caracteres não numéricos
        telefone = re.sub(r'\D', '', telefone)
        
        # Telefone deve ter 10 ou 11 dígitos
        return len(telefone) in [10, 11]
    
    @staticmethod
    def validar_data(data: datetime) -> bool:
        """Valida uma data."""
        return isinstance(data, datetime)
    
    @staticmethod
    def formatar_cpf(cpf: str) -> str:
        """Formata um CPF para o padrão XXX.XXX.XXX-XX."""
        cpf = re.sub(r'\D', '', cpf)
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    @staticmethod
    def formatar_telefone(telefone: str) -> str:
        """Formata um telefone para o padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."""
        telefone = re.sub(r'\D', '', telefone)
        
        if len(telefone) == 11:
            return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
        elif len(telefone) == 10:
            return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
        
        return telefone
