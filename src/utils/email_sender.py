"""
Sistema de envio de emails.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from pathlib import Path
from src.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM


class EmailSender:
    """Gerenciador de envio de emails."""
    
    def __init__(self):
        """Inicializa o gerenciador de emails."""
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
        self.email_from = EMAIL_FROM
    
    def enviar_email(self, destinatarios: List[str], assunto: str, corpo: str, 
                     html: bool = False, anexos: Optional[List[str]] = None) -> bool:
        """Envia um email."""
        if not self.username or not self.password:
            print("Erro: Credenciais de email não configuradas.")
            return False
        
        try:
            # Cria a mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = assunto
            
            # Adiciona o corpo da mensagem
            if html:
                msg.attach(MIMEText(corpo, 'html'))
            else:
                msg.attach(MIMEText(corpo, 'plain'))
            
            # Adiciona anexos
            if anexos:
                for anexo in anexos:
                    self._anexar_arquivo(msg, anexo)
            
            # Envia o email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False
    
    def enviar_relatorio(self, destinatarios: List[str], titulo: str, 
                        arquivo_relatorio: str, corpo_adicional: str = "") -> bool:
        """Envia um relatório por email."""
        assunto = f"Relatório: {titulo}"
        
        corpo = f"""
        Prezado(a),
        
        Segue em anexo o relatório solicitado: {titulo}
        
        {corpo_adicional}
        
        Atenciosamente,
        RH Control
        """
        
        return self.enviar_email(destinatarios, assunto, corpo, anexos=[arquivo_relatorio])
    
    def enviar_notificacao_afastamento(self, destinatarios: List[str], 
                                      funcionario_nome: str, tipo_afastamento: str,
                                      data_inicio: str, data_fim: str) -> bool:
        """Envia uma notificação de afastamento."""
        assunto = f"Notificação de Afastamento: {funcionario_nome}"
        
        corpo = f"""
        Prezado(a),
        
        Informamos que o funcionário {funcionario_nome} será afastado do trabalho.
        
        Detalhes do Afastamento:
        - Tipo: {tipo_afastamento}
        - Data de Início: {data_inicio}
        - Data de Término: {data_fim}
        
        Favor tomar as devidas providências.
        
        Atenciosamente,
        RH Control
        """
        
        return self.enviar_email(destinatarios, assunto, corpo)
    
    def enviar_convite_usuario(self, email: str, nome: str, 
                              username: str, senha_temporaria: str) -> bool:
        """Envia um convite para novo usuário."""
        assunto = "Bem-vindo ao RH Control"
        
        corpo = f"""
        Prezado(a) {nome},
        
        Você foi convidado para usar o sistema RH Control.
        
        Dados de Acesso:
        - Usuário: {username}
        - Senha Temporária: {senha_temporaria}
        
        Acesse o sistema e altere sua senha na primeira oportunidade.
        
        Atenciosamente,
        RH Control
        """
        
        return self.enviar_email([email], assunto, corpo)
    
    def enviar_relatorio_periodico(self, destinatarios: List[str], 
                                  periodo: str, arquivo_relatorio: str) -> bool:
        """Envia um relatório periódico."""
        assunto = f"Relatório Periódico - {periodo}"
        
        corpo = f"""
        Prezado(a),
        
        Segue em anexo o relatório periódico referente ao período de {periodo}.
        
        Atenciosamente,
        RH Control
        """
        
        return self.enviar_email(destinatarios, assunto, corpo, anexos=[arquivo_relatorio])
    
    @staticmethod
    def _anexar_arquivo(msg: MIMEMultipart, arquivo: str) -> None:
        """Anexa um arquivo à mensagem."""
        arquivo_path = Path(arquivo)
        
        if not arquivo_path.exists():
            print(f"Arquivo não encontrado: {arquivo}")
            return
        
        try:
            with open(arquivo_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {arquivo_path.name}')
            msg.attach(part)
        
        except Exception as e:
            print(f"Erro ao anexar arquivo: {e}")
