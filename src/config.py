"""
Configurações da aplicação RH Control.
"""

import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent.parent

# Diretório de dados
DATA_DIR = BASE_DIR / "src" / "data"

# Configurações de banco de dados
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "json")  # json ou sqlite
DATABASE_URL = os.getenv("DATABASE_URL", str(DATA_DIR / "rh_control.db"))

# Configurações de email
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@rhcontrol.com")

# Configurações de segurança
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-aqui-mude-em-producao")
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 3600))  # 1 hora em segundos

# Configurações de backup
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", 86400))  # 24 horas em segundos

# Configurações de notificações
NOTIFICATIONS_ENABLED = os.getenv("NOTIFICATIONS_ENABLED", "true").lower() == "true"
NOTIFICATION_DAYS_BEFORE = int(os.getenv("NOTIFICATION_DAYS_BEFORE", 7))  # Dias antes do afastamento

# Configurações de cálculo de férias
DIAS_FERIAS_ANUAL = int(os.getenv("DIAS_FERIAS_ANUAL", 30))
MESES_PARA_FERIAS = int(os.getenv("MESES_PARA_FERIAS", 12))

# Configurações de aplicação
APP_NAME = "RH Control"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Sistema de Gestão de Recursos Humanos"

# Configurações do Streamlit
STREAMLIT_CONFIG = {
    "theme": {
        "primaryColor": "#FF6B6B",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F0F2F6",
        "textColor": "#262730",
        "font": "sans serif"
    }
}
