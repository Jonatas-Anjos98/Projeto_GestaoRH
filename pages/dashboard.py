"""
Página de dashboard da aplicação.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import DatabaseSQL, AuthManager
from src.utils.charts import ChartManager
from src.utils.ferias import FeriasManager
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="RH Control - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verifica se o usuário está logado
if 'usuario_logado' not in st.session_state:
    st.warning("Por favor, faça login primeiro.")
    st.switch_page("pages/login.py")

# Inicializa o banco de dados
if 'db' not in st.session_state:
    st.session_state.db = DatabaseSQL()

if 'auth' not in st.session_state:
    st.session_state.auth = AuthManager(st.session_state.db)

# Obtém o usuário logado
usuario = st.session_state.usuario_logado

# Barra lateral
st.sidebar.title(f"👤 {usuario.nome}")
st.sidebar.markdown(f"**Perfil**: {usuario.perfil}")
st.sidebar.markdown("---")

# Menu de navegação
menu = st.sidebar.radio(
    "Navegação",
    [
        "📊 Dashboard",
        "👥 Funcionários",
        "📋 Afastamentos",
        "📈 Relatórios",
        "👨‍💼 Usuários",
        "⚙️ Configurações"
    ]
)

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.switch_page("pages/login.py")

# ============ PÁGINA: DASHBOARD ============
if menu == "📊 Dashboard":
    st.markdown("<h1 style='text-align: center; color: #FF6B6B;'>📊 Dashboard</h1>", unsafe_allow_html=True)
    
    # Obtém dados
    funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=True)
    
    # Cria colunas para métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Funcionários", len(funcionarios))
    
    with col2:
        lojas = len(set(f.loja for f in funcionarios if f.loja))
        st.metric("Lojas Cadastradas", lojas)
    
    with col3:
        cargos = len(set(f.cargo for f in funcionarios if f.cargo))
        st.metric("Cargos Diferentes", cargos)
    
    with col4:
        salario_total = sum(f.salario for f in funcionarios)
        st.metric("Folha de Pagamento", f"R$ {salario_total:,.2f}")
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        if funcionarios:
            fig = ChartManager.gráfico_funcionarios_por_loja(funcionarios)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if funcionarios:
            fig = ChartManager.gráfico_distribuicao_cargos(funcionarios)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if funcionarios:
            fig = ChartManager.gráfico_folha_pagamento_por_loja(funcionarios)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if funcionarios:
            fig = ChartManager.gráfico_salarios_por_cargo(funcionarios)
            st.plotly_chart(fig, use_container_width=True)
# ============ PÁGINA: FUNCIONÁRIOS ============
elif menu == "👥 Funcionários":
    st.markdown("<h1 style='text-align: center; color: #FF6B6B;'>👥 Gerenciar Funcionários</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Listar", "Adicionar", "Editar/Deletar"])
    
    with tab1:
        st.subheader("Lista de Funcionários")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=True)
        
        if funcionarios:
            df_data = []
            for func in funcionarios:
                df_data.append({
                    'ID': func.id,
                    'Nome': func.nome,
                    'CPF': func.cpf,
                    'Email': func.email,
                    'Cargo': func.cargo,
                    'Loja': func.loja,
                    'Salário': f"R$ {func.salario:,.2f}"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum funcionário cadastrado.")
    
    with tab2:
        st.subheader("Adicionar Novo Funcionário")
        
        with st.form("form_novo_funcionario"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome Completo *")
                cpf = st.text_input("CPF *")
                email = st.text_input("Email *")
                telefone = st.text_input("Telefone *")
            
            with col2:
                endereco = st.text_area("Endereço *", height=100)
                loja = st.text_input("Loja *")
                cargo = st.text_input("Cargo *")
                salario = st.number_input("Salário *", min_value=0.0, step=100.0)
            
            data_admissao = st.date_input("Data de Admissão *")
            
            submitted = st.form_submit_button("✅ Adicionar Funcionário", use_container_width=True)
            
            if submitted:
                if not all([nome, cpf, email, telefone, endereco, loja, cargo]):
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    from src.models import Funcionario
                    
                    novo_funcionario = Funcionario(
                        nome=nome,
                        cpf=cpf,
                        email=email,
                        telefone=telefone,
                        endereco=endereco,
                        loja=loja,
                        cargo=cargo,
                        salario=salario,
                        data_admissao=datetime.combine(data_admissao, datetime.min.time())
                    )
                    
                    st.session_state.db.criar_funcionario(novo_funcionario)
                    st.success("Funcionário adicionado com sucesso!")
                    st.rerun()
    
    with tab3:
        st.subheader("Editar ou Deletar Funcionário")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=True)
        
        if funcionarios:
            funcionarios_dict = {f.nome: f for f in funcionarios}
            funcionario_selecionado_nome = st.selectbox(
                "Selecione um funcionário",
                list(funcionarios_dict.keys())
            )
            
            funcionario_selecionado = funcionarios_dict[funcionario_selecionado_nome]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Editar Informações")
                
                with st.form("form_editar_funcionario"):
                    nome = st.text_input("Nome Completo", value=funcionario_selecionado.nome)
                    email = st.text_input("Email", value=funcionario_selecionado.email)
                    telefone = st.text_input("Telefone", value=funcionario_selecionado.telefone)
                    endereco = st.text_area("Endereço", value=funcionario_selecionado.endereco, height=100)
                    loja = st.text_input("Loja", value=funcionario_selecionado.loja)
                    cargo = st.text_input("Cargo", value=funcionario_selecionado.cargo)
                    salario = st.number_input("Salário", value=funcionario_selecionado.salario, step=100.0)
                    
                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        funcionario_selecionado.nome = nome
                        funcionario_selecionado.email = email
                        funcionario_selecionado.telefone = telefone
                        funcionario_selecionado.endereco = endereco
                        funcionario_selecionado.loja = loja
                        funcionario_selecionado.cargo = cargo
                        funcionario_selecionado.salario = salario
                        
                        st.session_state.db.atualizar_funcionario(funcionario_selecionado)
                        st.success("Funcionário atualizado com sucesso!")
                        st.rerun()
            
            with col2:
                st.subheader("Deletar Funcionário")
                
                st.warning(f"⚠️ Você está prestes a deletar **{funcionario_selecionado.nome}**.")
                
                if st.button("🗑️ Deletar Funcionário", use_container_width=True, type="secondary"):
                    st.session_state.db.deletar_funcionario(funcionario_selecionado.id)
                    st.success("Funcionário deletado com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum funcionário cadastrado.")
# ============ PÁGINA: AFASTAMENTOS ============
elif menu == "📋 Afastamentos":
    st.markdown("<h1 style='text-align: center; color: #FF6B6B;'>📋 Gerenciar Afastamentos</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Listar", "Adicionar", "Editar/Deletar"])
    
    with tab1:
        st.subheader("Lista de Afastamentos")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=False)
        
        if funcionarios:
            todos_afastamentos = []
            for func in funcionarios:
                afastamentos = st.session_state.db.listar_afastamentos_por_funcionario(func.id)
                todos_afastamentos.extend([(aft, func) for aft in afastamentos])
            
            if todos_afastamentos:
                df_data = []
                for aft, func in todos_afastamentos:
                    df_data.append({
                        'Funcionário': func.nome,
                        'Tipo': aft.tipo,
                        'Início': aft.data_inicio.strftime('%d/%m/%Y') if aft.data_inicio else 'N/A',
                        'Fim': aft.data_fim.strftime('%d/%m/%Y') if aft.data_fim else 'N/A',
                        'Dias': aft.dias_afastamento(),
                        'Motivo': aft.motivo
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum afastamento cadastrado.")
        else:
            st.info("Nenhum funcionário cadastrado.")
    
    with tab2:
        st.subheader("Adicionar Novo Afastamento")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=True)
        
        if funcionarios:
            from src.models import TipoAfastamento
            
            with st.form("form_novo_afastamento"):
                funcionario_nome = st.selectbox(
                    "Selecione o Funcionário *",
                    [f.nome for f in funcionarios]
                )
                
                funcionario = next(f for f in funcionarios if f.nome == funcionario_nome)
                
                tipo_afastamento = st.selectbox(
                    "Tipo de Afastamento *",
                    [t.value for t in TipoAfastamento]
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    data_inicio = st.date_input("Data de Início *")
                
                with col2:
                    data_fim = st.date_input("Data de Fim *")
                
                motivo = st.text_input("Motivo *")
                observacoes = st.text_area("Observações", height=100)
                
                submitted = st.form_submit_button("✅ Adicionar Afastamento", use_container_width=True)
                
                if submitted:
                    if not motivo:
                        st.error("Por favor, preencha o motivo do afastamento.")
                    elif data_inicio > data_fim:
                        st.error("A data de início não pode ser posterior à data de fim.")
                    else:
                        from src.models import Afastamento
                        
                        novo_afastamento = Afastamento(
                            funcionario_id=funcionario.id,
                            tipo=tipo_afastamento,
                            data_inicio=datetime.combine(data_inicio, datetime.min.time()),
                            data_fim=datetime.combine(data_fim, datetime.min.time()),
                            motivo=motivo,
                            observacoes=observacoes
                        )
                        
                        st.session_state.db.criar_afastamento(novo_afastamento)
                        st.success("Afastamento adicionado com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum funcionário cadastrado.")
    
    with tab3:
        st.subheader("Editar ou Deletar Afastamento")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=False)
        
        if funcionarios:
            todos_afastamentos = []
            afastamento_info = {}
            
            for func in funcionarios:
                afastamentos = st.session_state.db.listar_afastamentos_por_funcionario(func.id)
                for aft in afastamentos:
                    label = f"{func.nome} - {aft.tipo} ({aft.data_inicio.strftime('%d/%m/%Y')})"
                    todos_afastamentos.append(label)
                    afastamento_info[label] = (aft, func)
            
            if todos_afastamentos:
                afastamento_selecionado_label = st.selectbox(
                    "Selecione um afastamento",
                    todos_afastamentos
                )
                
                afastamento_selecionado, funcionario_selecionado = afastamento_info[afastamento_selecionado_label]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Editar Informações")
                    
                    with st.form("form_editar_afastamento"):
                        from src.models import TipoAfastamento
                        
                        tipo = st.selectbox(
                            "Tipo de Afastamento",
                            [t.value for t in TipoAfastamento],
                            index=[t.value for t in TipoAfastamento].index(afastamento_selecionado.tipo)
                        )
                        
                        data_inicio = st.date_input(
                            "Data de Início",
                            value=afastamento_selecionado.data_inicio.date()
                        )
                        
                        data_fim = st.date_input(
                            "Data de Fim",
                            value=afastamento_selecionado.data_fim.date()
                        )
                        
                        motivo = st.text_input("Motivo", value=afastamento_selecionado.motivo)
                        observacoes = st.text_area("Observações", value=afastamento_selecionado.observacoes, height=100)
                        
                        if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                            if data_inicio > data_fim:
                                st.error("A data de início não pode ser posterior à data de fim.")
                            else:
                                afastamento_selecionado.tipo = tipo
                                afastamento_selecionado.data_inicio = datetime.combine(data_inicio, datetime.min.time())
                                afastamento_selecionado.data_fim = datetime.combine(data_fim, datetime.min.time())
                                afastamento_selecionado.motivo = motivo
                                afastamento_selecionado.observacoes = observacoes
                                
                                st.session_state.db.atualizar_afastamento(afastamento_selecionado)
                                st.success("Afastamento atualizado com sucesso!")
                                st.rerun()
                
                with col2:
                    st.subheader("Deletar Afastamento")
                    
                    st.warning(f"⚠️ Você está prestes a deletar o afastamento de **{funcionario_selecionado.nome}**.")
                    
                    if st.button("🗑️ Deletar Afastamento", use_container_width=True, type="secondary"):
                        st.session_state.db.deletar_afastamento(afastamento_selecionado.id)
                        st.success("Afastamento deletado com sucesso!")
                        st.rerun()
            else:
                st.info("Nenhum afastamento cadastrado.")
        else:
            st.info("Nenhum funcionário cadastrado.")
# ============ PÁGINA: RELATÓRIOS ============
elif menu == "📈 Relatórios":
    st.markdown("<h1 style='text-align: center; color: #FF6B6B;'>📈 Relatórios</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Afastamentos por Período", "Resumo por Tipo", "Férias"])
    
    with tab1:
        st.subheader("Relatório de Afastamentos por Período")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_inicio = st.date_input("Data de Início")
        
        with col2:
            data_fim = st.date_input("Data de Fim")
        
        if st.button("📊 Gerar Relatório"):
            if data_inicio > data_fim:
                st.error("A data de início não pode ser posterior à data de fim.")
            else:
                afastamentos = st.session_state.db.listar_afastamentos_por_periodo(
                    datetime.combine(data_inicio, datetime.min.time()),
                    datetime.combine(data_fim, datetime.min.time())
                )
                
                if afastamentos:
                    df_data = []
                    for aft in afastamentos:
                        func = st.session_state.db.obter_funcionario(aft.funcionario_id)
                        df_data.append({
                            'Funcionário': func.nome if func else 'N/A',
                            'Tipo': aft.tipo,
                            'Início': aft.data_inicio.strftime('%d/%m/%Y'),
                            'Fim': aft.data_fim.strftime('%d/%m/%Y'),
                            'Dias': aft.dias_afastamento(),
                            'Motivo': aft.motivo
                        })
                    
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Estatísticas
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total de Afastamentos", len(afastamentos))
                    
                    with col2:
                        total_dias = sum(aft.dias_afastamento() for aft in afastamentos)
                        st.metric("Total de Dias", total_dias)
                    
                    with col3:
                        funcionarios_unicos = len(set(aft.funcionario_id for aft in afastamentos))
                        st.metric("Funcionários Afastados", funcionarios_unicos)
                else:
                    st.info("Nenhum afastamento encontrado no período.")
    
    with tab2:
        st.subheader("Resumo de Afastamentos por Tipo")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=False)
        
        if funcionarios:
            todos_afastamentos = []
            for func in funcionarios:
                afastamentos = st.session_state.db.listar_afastamentos_por_funcionario(func.id)
                todos_afastamentos.extend(afastamentos)
            
            if todos_afastamentos:
                # Conta afastamentos por tipo
                tipos_count = {}
                tipos_dias = {}
                
                for aft in todos_afastamentos:
                    tipos_count[aft.tipo] = tipos_count.get(aft.tipo, 0) + 1
                    tipos_dias[aft.tipo] = tipos_dias.get(aft.tipo, 0) + aft.dias_afastamento()
                
                df_tipos = pd.DataFrame({
                    'Tipo': list(tipos_count.keys()),
                    'Quantidade': list(tipos_count.values()),
                    'Total de Dias': [tipos_dias[t] for t in tipos_count.keys()]
                })
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.dataframe(df_tipos, use_container_width=True, hide_index=True)
                
                with col2:
                    fig = ChartManager.gráfico_afastamentos_por_tipo(todos_afastamentos)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhum afastamento registrado.")
        else:
            st.info("Nenhum funcionário cadastrado.")
    
    with tab3:
        st.subheader("Relatório de Férias")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=True)
        
        if funcionarios:
            ferias_manager = FeriasManager()
            
            df_data = []
            for func in funcionarios:
                dias_disponiveis = ferias_manager.calcular_dias_ferias(func.data_admissao)
                
                # Calcula dias utilizados
                afastamentos = st.session_state.db.listar_afastamentos_por_funcionario(func.id)
                dias_utilizados = sum(
                    aft.dias_afastamento() for aft in afastamentos
                    if aft.tipo == "Férias"
                )
                
                df_data.append({
                    'Nome': func.nome,
                    'Data Admissão': func.data_admissao.strftime('%d/%m/%Y') if func.data_admissao else 'N/A',
                    'Dias Disponíveis': dias_disponiveis,
                    'Dias Utilizados': dias_utilizados,
                    'Saldo': dias_disponiveis - dias_utilizados
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum funcionário cadastrado.")
# ============ PÁGINA: USUÁRIOS ============
elif menu == "👨‍💼 Usuários":
    if not usuario.tem_permissao("criar_usuario"):
        st.error("Você não tem permissão para acessar esta página.")
    else:
        st.markdown("<h1 style='text-align: center; color: #FF6B6B;'>👨‍💼 Gerenciar Usuários</h1>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Listar", "Adicionar"])
        
        with tab1:
            st.subheader("Lista de Usuários")
            
            usuarios = st.session_state.db.listar_usuarios(apenas_ativos=True)
            
            if usuarios:
                df_data = []
                for user in usuarios:
                    df_data.append({
                        'Nome': user.nome,
                        'Email': user.email,
                        'Usuário': user.username,
                        'Perfil': user.perfil,
                        'Último Acesso': user.ultimo_acesso.strftime('%d/%m/%Y %H:%M') if user.ultimo_acesso else 'Nunca'
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum usuário cadastrado.")
        
        with tab2:
            st.subheader("Adicionar Novo Usuário")
            
            from src.models import PerfilUsuario
            
            with st.form("form_novo_usuario"):
                nome = st.text_input("Nome Completo *")
                email = st.text_input("Email *")
                username = st.text_input("Usuário *")
                senha = st.text_input("Senha *", type="password")
                perfil = st.selectbox(
                    "Perfil *",
                    [p.value for p in PerfilUsuario]
                )
                
                submitted = st.form_submit_button("✅ Adicionar Usuário", use_container_width=True)
                
                if submitted:
                    if not all([nome, email, username, senha]):
                        st.error("Por favor, preencha todos os campos obrigatórios.")
                    else:
                        novo_usuario = st.session_state.auth.criar_usuario(
                            nome=nome,
                            email=email,
                            username=username,
                            senha=senha,
                            perfil=perfil
                        )
                        
                        if novo_usuario:
                            st.success("Usuário adicionado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Erro ao criar o usuário. Verifique se o username ou email já existem.")

# ============ PÁGINA: CONFIGURAÇÕES ============
elif menu == "⚙️ Configurações":
    st.markdown("<h1 style='text-align: center; color: #FF6B6B;'>⚙️ Configurações</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Perfil", "Segurança", "Sobre"])
    
    with tab1:
        st.subheader("Meu Perfil")
        
        st.info(f"""
        **Nome**: {usuario.nome}
        **Email**: {usuario.email}
        **Usuário**: {usuario.username}
        **Perfil**: {usuario.perfil}
        **Ativo**: {'Sim' if usuario.ativo else 'Não'}
        """)
    
    with tab2:
        st.subheader("Alterar Senha")
        
        with st.form("form_alterar_senha"):
            senha_atual = st.text_input("Senha Atual *", type="password")
            senha_nova = st.text_input("Nova Senha *", type="password")
            confirmar_senha = st.text_input("Confirmar Nova Senha *", type="password")
            
            submitted = st.form_submit_button("🔐 Alterar Senha", use_container_width=True)
            
            if submitted:
                if not all([senha_atual, senha_nova, confirmar_senha]):
                    st.error("Por favor, preencha todos os campos.")
                elif senha_nova != confirmar_senha:
                    st.error("As senhas não correspondem.")
                elif len(senha_nova) < 6:
                    st.error("A nova senha deve ter pelo menos 6 caracteres.")
                else:
                    if st.session_state.auth.alterar_senha(usuario.id, senha_atual, senha_nova):
                        st.success("Senha alterada com sucesso!")
                    else:
                        st.error("Senha atual incorreta.")
    
    with tab3:
        st.subheader("Sobre a Aplicação")
        
        st.info("""
        **RH Control - Sistema de Gestão de Recursos Humanos**
        
        Versão: 2.0.0
        
        Um sistema completo para gerenciar funcionários, afastamentos e gerar relatórios.
        
        **Funcionalidades**:
        - ✅ Cadastro de funcionários
        - ✅ Gestão de afastamentos
        - ✅ Cálculo automático de férias
        - ✅ Relatórios e gráficos
        - ✅ Autenticação de usuários
        - ✅ Backup automático
        - ✅ Notificações
        """)
