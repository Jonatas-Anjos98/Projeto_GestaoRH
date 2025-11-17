"""
Página de login da aplicação.
"""

import streamlit as st
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import DatabaseSQL, AuthManager
from src.models import PerfilUsuario

# Configuração da página
st.set_page_config(
    page_title="RH Control - Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS customizado
st.markdown("""
<style>
    .login-container {
        max-width: 400px;
        margin: 50px auto;
        padding: 2rem;
        border-radius: 10px;
        background-color: #f0f2f6;
    }
    .login-title {
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicializa o banco de dados
if 'db' not in st.session_state:
    st.session_state.db = DatabaseSQL()

if 'auth' not in st.session_state:
    st.session_state.auth = AuthManager(st.session_state.db)

# Se o usuário já está logado, redireciona para a página principal
if 'usuario_logado' in st.session_state and st.session_state.usuario_logado:
    st.switch_page("pages/dashboard.py")

# Página de Login
st.markdown("<h1 class='login-title'>🏢 RH Control</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='login-title'>Sistema de Gestão de RH</h3>", unsafe_allow_html=True)

st.markdown("---")

# Tabs para Login e Registro
tab1, tab2 = st.tabs(["Login", "Criar Conta"])

with tab1:
    st.subheader("Fazer Login")
    
    with st.form("form_login"):
        username = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        
        submitted = st.form_submit_button("🔓 Entrar", use_container_width=True)
        
        if submitted:
            if not username or not senha:
                st.error("Por favor, preencha todos os campos.")
            else:
                usuario = st.session_state.auth.autenticar(username, senha)
                
                if usuario:
                    st.session_state.usuario_logado = usuario
                    st.success(f"Bem-vindo, {usuario.nome}!")
                    st.balloons()
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("Usuário ou senha incorretos.")

with tab2:
    st.subheader("Criar Nova Conta")
    
    st.info("Entre em contato com um administrador para criar uma nova conta.")
    
    # Formulário de registro (apenas para demonstração)
    with st.form("form_registro"):
        nome = st.text_input("Nome Completo", placeholder="Digite seu nome completo")
        email = st.text_input("Email", placeholder="Digite seu email")
        username = st.text_input("Usuário", placeholder="Escolha um usuário")
        senha = st.text_input("Senha", type="password", placeholder="Escolha uma senha")
        confirmar_senha = st.text_input("Confirmar Senha", type="password", placeholder="Confirme a senha")
        
        submitted = st.form_submit_button("📝 Criar Conta", use_container_width=True)
        
        if submitted:
            if not all([nome, email, username, senha, confirmar_senha]):
                st.error("Por favor, preencha todos os campos.")
            elif senha != confirmar_senha:
                st.error("As senhas não correspondem.")
            elif len(senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                # Verifica se o username já existe
                if st.session_state.auth.obter_usuario_por_username(username):
                    st.error("Este usuário já existe.")
                elif st.session_state.auth.obter_usuario_por_email(email):
                    st.error("Este email já está cadastrado.")
                else:
                    novo_usuario = st.session_state.auth.criar_usuario(
                        nome=nome,
                        email=email,
                        username=username,
                        senha=senha,
                        perfil=PerfilUsuario.FUNCIONARIO.value
                    )
                    
                    if novo_usuario:
                        st.success("Conta criada com sucesso! Faça login para continuar.")
                    else:
                        st.error("Erro ao criar a conta.")

st.markdown("---")

# Informações de demonstração
st.markdown("""
### 📝 Dados de Demonstração

Para testar a aplicação, use:

- **Usuário**: admin
- **Senha**: admin123

> **Nota**: Altere a senha na primeira oportunidade.
""")
