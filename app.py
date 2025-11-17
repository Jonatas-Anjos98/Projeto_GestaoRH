"""
Aplicação principal de Gestão de RH com Streamlit.
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import DatabaseManager
from src.models import TipoAfastamento

# Configuração da página
st.set_page_config(
    page_title="RH Control - Gestão de Recursos Humanos",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa o gerenciador de banco de dados
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# CSS customizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Barra lateral com navegação
st.sidebar.title("🏢 RH Control")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação",
    [
        "📊 Dashboard",
        "👤 Funcionários",
        "📋 Afastamentos",
        "📈 Relatórios",
        "⚙️ Configurações"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**RH Control** é um sistema de gestão de recursos humanos "
    "desenvolvido com Streamlit para facilitar o gerenciamento "
    "de funcionários e afastamentos."
)

# ============ PÁGINA: DASHBOARD ============
if menu == "📊 Dashboard":
    st.markdown("<h1 class='main-header'>📊 Dashboard</h1>", unsafe_allow_html=True)
    
    # Obtém estatísticas
    funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=True)
    total_funcionarios = len(funcionarios)
    
    # Cria colunas para métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Funcionários", total_funcionarios, delta=None)
    
    with col2:
        lojas = len(set(f.loja for f in funcionarios if f.loja))
        st.metric("Lojas Cadastradas", lojas, delta=None)
    
    with col3:
        cargos = len(set(f.cargo for f in funcionarios if f.cargo))
        st.metric("Cargos Diferentes", cargos, delta=None)
    
    with col4:
        salario_total = sum(f.salario for f in funcionarios)
        st.metric("Folha de Pagamento", f"R$ {salario_total:,.2f}", delta=None)
    
    st.markdown("---")
    
    # Distribuição por loja
    if funcionarios:
        st.subheader("Distribuição de Funcionários por Loja")
        
        lojas_count = {}
        for func in funcionarios:
            if func.loja:
                lojas_count[func.loja] = lojas_count.get(func.loja, 0) + 1
        
        if lojas_count:
            import pandas as pd
            df_lojas = pd.DataFrame(list(lojas_count.items()), columns=['Loja', 'Quantidade'])
            st.bar_chart(df_lojas.set_index('Loja'))
    
    st.markdown("---")
    
    # Últimos funcionários cadastrados
    st.subheader("Últimos Funcionários Cadastrados")
    
    if funcionarios:
        # Ordena por data de criação (mais recentes primeiro)
        funcionarios_recentes = sorted(
            funcionarios,
            key=lambda x: x.data_criacao or datetime.min,
            reverse=True
        )[:5]
        
        import pandas as pd
        df_recentes = pd.DataFrame([
            {
                'Nome': f.nome,
                'CPF': f.cpf,
                'Cargo': f.cargo,
                'Loja': f.loja,
                'Data Admissão': f.data_admissao.strftime('%d/%m/%Y') if f.data_admissao else 'N/A'
            }
            for f in funcionarios_recentes
        ])
        
        st.dataframe(df_recentes, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum funcionário cadastrado ainda.")

# ============ PÁGINA: FUNCIONÁRIOS ============
elif menu == "👤 Funcionários":
    st.markdown("<h1 class='main-header'>👤 Gerenciar Funcionários</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Listar", "Adicionar", "Editar/Deletar"])
    
    # TAB 1: LISTAR FUNCIONÁRIOS
    with tab1:
        st.subheader("Lista de Funcionários")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=True)
        
        if funcionarios:
            import pandas as pd
            
            df_data = []
            for func in funcionarios:
                df_data.append({
                    'ID': func.id,
                    'Nome': func.nome,
                    'CPF': func.cpf,
                    'Email': func.email,
                    'Telefone': func.telefone,
                    'Cargo': func.cargo,
                    'Loja': func.loja,
                    'Admissão': func.data_admissao.strftime('%d/%m/%Y') if func.data_admissao else 'N/A',
                    'Salário': f"R$ {func.salario:,.2f}"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Botão para exportar
            if st.button("📥 Exportar para Excel"):
                try:
                    st.session_state.db.exportar_funcionarios_excel("funcionarios.xlsx")
                    st.success("Arquivo exportado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao exportar: {e}")
        else:
            st.info("Nenhum funcionário cadastrado.")
    
    # TAB 2: ADICIONAR FUNCIONÁRIO
    with tab2:
        st.subheader("Adicionar Novo Funcionário")
        
        with st.form("form_novo_funcionario"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome Completo *", key="novo_nome")
                cpf = st.text_input("CPF (XXX.XXX.XXX-XX) *", key="novo_cpf")
                email = st.text_input("Email *", key="novo_email")
                telefone = st.text_input("Telefone (XX) XXXXX-XXXX *", key="novo_telefone")
            
            with col2:
                endereco = st.text_area("Endereço *", key="novo_endereco", height=100)
                loja = st.text_input("Loja *", key="novo_loja") 
                cargo = st.text_input("Cargo *", key="novo_cargo")
                salario = st.number_input("Salário *", min_value=0.0, step=100.0, key="novo_salario")
            
            data_admissao = st.date_input("Data de Admissão *", key="novo_data_admissao")
            
            submitted = st.form_submit_button("✅ Adicionar Funcionário", use_container_width=True)
            
            if submitted:
                # Validações
                if not nome or not cpf or not email or not telefone or not endereco or not loja or not cargo:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    from src.utils import Validators
                    
                    # Valida CPF
                    if not Validators.validar_cpf(cpf):
                        st.error("CPF inválido.")
                    # Valida Email
                    elif not Validators.validar_email(email):
                        st.error("Email inválido.")
                    # Valida Telefone
                    elif not Validators.validar_telefone(telefone):
                        st.error("Telefone inválido.")
                    # Verifica se CPF já existe
                    elif st.session_state.db.obter_funcionario_por_cpf(cpf):
                        st.error("CPF já cadastrado no sistema.")
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
    
    # TAB 3: EDITAR/DELETAR FUNCIONÁRIO
    with tab3:
        st.subheader("Editar ou Deletar Funcionário")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=True)
        
        if funcionarios:
            # Cria um dicionário para facilitar a seleção
            funcionarios_dict = {f.nome: f for f in funcionarios}
            funcionario_selecionado_nome = st.selectbox(
                "Selecione um funcionário",
                list(funcionarios_dict.keys())
            )
            
            funcionario_selecionado = funcionarios_dict[funcionario_selecionado_nome]
            
            st.info(f"**ID:** {funcionario_selecionado.id}")
            
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
                        from src.utils import Validators
                        
                        if not Validators.validar_email(email):
                            st.error("Email inválido.")
                        elif not Validators.validar_telefone(telefone):
                            st.error("Telefone inválido.")
                        else:
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
                st.warning(f"Tem certeza que deseja deletar **{funcionario_selecionado.nome}**?")
                
                if st.button("🗑️ Deletar Funcionário", use_container_width=True, type="secondary"):
                    st.session_state.db.deletar_funcionario(funcionario_selecionado.id)
                    st.success("Funcionário deletado com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum funcionário cadastrado.")

# ============ PÁGINA: AFASTAMENTOS ============
elif menu == "📋 Afastamentos":
    st.markdown("<h1 class='main-header'>📋 Gerenciar Afastamentos</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Listar", "Adicionar", "Editar/Deletar"])
    
    # TAB 1: LISTAR AFASTAMENTOS
    with tab1:
        st.subheader("Lista de Afastamentos")
        
        afastamentos = []
        for aft in st.session_state.db._load_json(st.session_state.db.afastamentos_file):
            afastamentos.append(st.session_state.db._dict_to_afastamento(aft))
        
        if afastamentos:
            import pandas as pd
            
            df_data = []
            for aft in afastamentos:
                funcionario = st.session_state.db.obter_funcionario(aft.funcionario_id)
                df_data.append({
                    'ID': aft.id,
                    'Funcionário': funcionario.nome if funcionario else 'N/A',
                    'Tipo': aft.tipo,
                    'Início': aft.data_inicio.strftime('%d/%m/%Y') if aft.data_inicio else 'N/A',
                    'Fim': aft.data_fim.strftime('%d/%m/%Y') if aft.data_fim else 'N/A',
                    'Dias': aft.dias_afastamento(),
                    'Motivo': aft.motivo
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum afastamento registrado.")
    
    # TAB 2: ADICIONAR AFASTAMENTO
    with tab2:
        st.subheader("Registrar Novo Afastamento")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=True)
        
        if funcionarios:
            with st.form("form_novo_afastamento"):
                funcionario_nome = st.selectbox(
                    "Selecione o Funcionário *",
                    [f.nome for f in funcionarios],
                    key="novo_aft_funcionario"
                )
                
                funcionario = next((f for f in funcionarios if f.nome == funcionario_nome), None)
                
                tipo_afastamento = st.selectbox(
                    "Tipo de Afastamento *",
                    [t.value for t in TipoAfastamento],
                    key="novo_aft_tipo"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    data_inicio = st.date_input("Data de Início *", key="novo_aft_inicio")
                with col2:
                    data_fim = st.date_input("Data de Fim *", key="novo_aft_fim")
                
                motivo = st.text_area("Motivo *", key="novo_aft_motivo", height=100)
                observacoes = st.text_area("Observações", key="novo_aft_obs", height=80)
                
                submitted = st.form_submit_button("✅ Registrar Afastamento", use_container_width=True)
                
                if submitted:
                    if not funcionario or not tipo_afastamento or not motivo:
                        st.error("Por favor, preencha todos os campos obrigatórios.")
                    elif data_fim < data_inicio:
                        st.error("A data de fim não pode ser anterior à data de início.")
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
                        st.success("Afastamento registrado com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum funcionário cadastrado. Cadastre um funcionário primeiro.")
    
    # TAB 3: EDITAR/DELETAR AFASTAMENTO
    with tab3:
        st.subheader("Editar ou Deletar Afastamento")
        
        afastamentos = []
        for aft in st.session_state.db._load_json(st.session_state.db.afastamentos_file):
            afastamentos.append(st.session_state.db._dict_to_afastamento(aft))
        
        if afastamentos:
            # Cria um dicionário para facilitar a seleção
            afastamentos_dict = {}
            for aft in afastamentos:
                funcionario = st.session_state.db.obter_funcionario(aft.funcionario_id)
                chave = f"{funcionario.nome if funcionario else 'N/A'} - {aft.tipo} ({aft.data_inicio.strftime('%d/%m/%Y')})"
                afastamentos_dict[chave] = aft
            
            afastamento_selecionado_chave = st.selectbox(
                "Selecione um afastamento",
                list(afastamentos_dict.keys())
            )
            
            afastamento_selecionado = afastamentos_dict[afastamento_selecionado_chave]
            
            st.info(f"**ID:** {afastamento_selecionado.id}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Editar Informações")
                
                with st.form("form_editar_afastamento"):
                    tipo = st.selectbox(
                        "Tipo de Afastamento",
                        [t.value for t in TipoAfastamento],
                        index=[t.value for t in TipoAfastamento].index(afastamento_selecionado.tipo)
                    )
                    
                    motivo = st.text_area("Motivo", value=afastamento_selecionado.motivo, height=100)
                    observacoes = st.text_area("Observações", value=afastamento_selecionado.observacoes, height=80)
                    
                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        afastamento_selecionado.tipo = tipo
                        afastamento_selecionado.motivo = motivo
                        afastamento_selecionado.observacoes = observacoes
                        
                        st.session_state.db.atualizar_afastamento(afastamento_selecionado)
                        st.success("Afastamento atualizado com sucesso!")
                        st.rerun()
            
            with col2:
                st.subheader("Deletar Afastamento")
                st.warning("Tem certeza que deseja deletar este afastamento?")
                
                if st.button("🗑️ Deletar Afastamento", use_container_width=True, type="secondary"):
                    st.session_state.db.deletar_afastamento(afastamento_selecionado.id)
                    st.success("Afastamento deletado com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum afastamento registrado.")

# ============ PÁGINA: RELATÓRIOS ============
elif menu == "📈 Relatórios":
    st.markdown("<h1 class='main-header'>📈 Relatórios</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Afastamentos por Período", "Resumo por Tipo", "Relatório de Férias"])
    
    # TAB 1: AFASTAMENTOS POR PERÍODO
    with tab1:
        st.subheader("Afastamentos por Período")
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data de Início", key="rel_data_inicio")
        with col2:
            data_fim = st.date_input("Data de Fim", key="rel_data_fim")
        
        if st.button("🔍 Gerar Relatório", key="btn_rel_periodo"):
            afastamentos = st.session_state.db.listar_afastamentos_por_periodo(
                datetime.combine(data_inicio, datetime.min.time()),
                datetime.combine(data_fim, datetime.min.time())
            )
            
            if afastamentos:
                import pandas as pd
                
                df_data = []
                for aft in afastamentos:
                    funcionario = st.session_state.db.obter_funcionario(aft.funcionario_id)
                    df_data.append({
                        'Funcionário': funcionario.nome if funcionario else 'N/A',
                        'Tipo': aft.tipo,
                        'Início': aft.data_inicio.strftime('%d/%m/%Y'),
                        'Fim': aft.data_fim.strftime('%d/%m/%Y'),
                        'Dias': aft.dias_afastamento(),
                        'Motivo': aft.motivo
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.success(f"Total de {len(afastamentos)} afastamento(s) encontrado(s).")
            else:
                st.info("Nenhum afastamento encontrado no período.")
    
    # TAB 2: RESUMO POR TIPO
    with tab2:
        st.subheader("Resumo de Afastamentos por Tipo")
        
        afastamentos = []
        for aft in st.session_state.db._load_json(st.session_state.db.afastamentos_file):
            afastamentos.append(st.session_state.db._dict_to_afastamento(aft))
        
        if afastamentos:
            import pandas as pd
            
            # Conta afastamentos por tipo
            tipos_count = {}
            for aft in afastamentos:
                tipos_count[aft.tipo] = tipos_count.get(aft.tipo, 0) + 1
            
            df_tipos = pd.DataFrame(list(tipos_count.items()), columns=['Tipo', 'Quantidade'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(df_tipos, use_container_width=True, hide_index=True)
            
            with col2:
                st.bar_chart(df_tipos.set_index('Tipo'))
        else:
            st.info("Nenhum afastamento registrado.")
    
    # TAB 3: RELATÓRIO DE FÉRIAS
    with tab3:
        st.subheader("Relatório de Férias")
        
        funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=True)
        
        if funcionarios:
            import pandas as pd
            from src.utils.ferias import FeriasManager
            
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

# ============ PÁGINA: CONFIGURAÇÕES ============
elif menu == "⚙️ Configurações":
    st.markdown("<h1 class='main-header'>⚙️ Configurações</h1>", unsafe_allow_html=True)
    
    st.subheader("Informações do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(
            "**RH Control v2.0.0**\n\n"
            "Sistema de Gestão de Recursos Humanos\n\n"
            "Desenvolvido com Streamlit e Python"
        )
    
    with col2:
        st.success(
            "**Funcionalidades:**\n\n"
            "✅ CRUD de Funcionários\n"
            "✅ Gerenciamento de Afastamentos\n"
            "✅ Relatórios Personalizados\n"
            "✅ Cálculo de Férias"
        )
    
    st.markdown("---")
    
    st.subheader("Ações de Manutenção")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Estatísticas do Sistema", use_container_width=True):
            funcionarios = st.session_state.db.listar_funcionarios(apenas_ativos=False)
            
            st.write(f"**Total de Funcionários:** {len(funcionarios)}")
            st.write(f"**Funcionários Ativos:** {len([f for f in funcionarios if f.ativo])}")
            st.write(f"**Funcionários Inativos:** {len([f for f in funcionarios if not f.ativo])}")
    
    with col2:
        if st.button("🔄 Recarregar Dados", use_container_width=True):
            st.session_state.db = DatabaseManager()
            st.success("Dados recarregados com sucesso!")
            st.rerun()
