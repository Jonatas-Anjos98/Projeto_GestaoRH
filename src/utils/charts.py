"""
Utilitários para criação de gráficos e visualizações.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.models import Afastamento, Funcionario


class ChartManager:
    """Gerenciador de gráficos e visualizações."""
    
    @staticmethod
    def gráfico_funcionarios_por_loja(funcionarios: List[Funcionario]) -> go.Figure:
        """Cria um gráfico de funcionários por loja."""
        lojas_count = {}
        for func in funcionarios:
            if func.loja:
                lojas_count[func.loja] = lojas_count.get(func.loja, 0) + 1
        
        df = pd.DataFrame(list(lojas_count.items()), columns=['Loja', 'Quantidade'])
        
        fig = px.bar(
            df,
            x='Loja',
            y='Quantidade',
            title='Distribuição de Funcionários por Loja',
            labels={'Quantidade': 'Número de Funcionários'},
            color='Quantidade',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            showlegend=False,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def gráfico_afastamentos_por_tipo(afastamentos: List[Afastamento]) -> go.Figure:
        """Cria um gráfico de afastamentos por tipo."""
        tipos_count = {}
        for aft in afastamentos:
            tipos_count[aft.tipo] = tipos_count.get(aft.tipo, 0) + 1
        
        df = pd.DataFrame(list(tipos_count.items()), columns=['Tipo', 'Quantidade'])
        
        fig = px.pie(
            df,
            names='Tipo',
            values='Quantidade',
            title='Distribuição de Afastamentos por Tipo',
            hole=0.3
        )
        
        fig.update_layout(template='plotly_white')
        
        return fig
    
    @staticmethod
    def gráfico_dias_afastamento_por_tipo(afastamentos: List[Afastamento]) -> go.Figure:
        """Cria um gráfico de dias de afastamento por tipo."""
        tipos_dias = {}
        for aft in afastamentos:
            dias = aft.dias_afastamento()
            tipos_dias[aft.tipo] = tipos_dias.get(aft.tipo, 0) + dias
        
        df = pd.DataFrame(list(tipos_dias.items()), columns=['Tipo', 'Dias'])
        df = df.sort_values('Dias', ascending=False)
        
        fig = px.bar(
            df,
            x='Tipo',
            y='Dias',
            title='Total de Dias de Afastamento por Tipo',
            labels={'Dias': 'Número de Dias'},
            color='Dias',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(
            showlegend=False,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def gráfico_afastamentos_por_mes(afastamentos: List[Afastamento]) -> go.Figure:
        """Cria um gráfico de afastamentos por mês."""
        meses_count = {}
        
        for aft in afastamentos:
            if aft.data_inicio:
                mes_ano = aft.data_inicio.strftime('%Y-%m')
                meses_count[mes_ano] = meses_count.get(mes_ano, 0) + 1
        
        df = pd.DataFrame(list(meses_count.items()), columns=['Mês', 'Quantidade'])
        df = df.sort_values('Mês')
        
        fig = px.line(
            df,
            x='Mês',
            y='Quantidade',
            title='Afastamentos por Mês',
            labels={'Quantidade': 'Número de Afastamentos'},
            markers=True
        )
        
        fig.update_layout(
            showlegend=False,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def gráfico_folha_pagamento_por_loja(funcionarios: List[Funcionario]) -> go.Figure:
        """Cria um gráfico de folha de pagamento por loja."""
        lojas_salario = {}
        
        for func in funcionarios:
            if func.loja and func.ativo:
                lojas_salario[func.loja] = lojas_salario.get(func.loja, 0) + func.salario
        
        df = pd.DataFrame(list(lojas_salario.items()), columns=['Loja', 'Folha de Pagamento'])
        df = df.sort_values('Folha de Pagamento', ascending=False)
        
        fig = px.bar(
            df,
            x='Loja',
            y='Folha de Pagamento',
            title='Folha de Pagamento por Loja',
            labels={'Folha de Pagamento': 'Valor (R$)'},
            color='Folha de Pagamento',
            color_continuous_scale='Greens'
        )
        
        fig.update_layout(
            showlegend=False,
            hovermode='x unified',
            template='plotly_white'
        )
        
        # Formata o eixo Y como moeda
        fig.update_yaxes(tickformat='$,.0f')
        
        return fig
    
    @staticmethod
    def gráfico_distribuicao_cargos(funcionarios: List[Funcionario]) -> go.Figure:
        """Cria um gráfico de distribuição de cargos."""
        cargos_count = {}
        
        for func in funcionarios:
            if func.cargo and func.ativo:
                cargos_count[func.cargo] = cargos_count.get(func.cargo, 0) + 1
        
        df = pd.DataFrame(list(cargos_count.items()), columns=['Cargo', 'Quantidade'])
        df = df.sort_values('Quantidade', ascending=True)
        
        fig = px.barh(
            df,
            x='Quantidade',
            y='Cargo',
            title='Distribuição de Funcionários por Cargo',
            labels={'Quantidade': 'Número de Funcionários'},
            color='Quantidade',
            color_continuous_scale='Purples'
        )
        
        fig.update_layout(
            showlegend=False,
            hovermode='y unified',
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def gráfico_timeline_afastamentos(afastamentos: List[Afastamento], funcionarios_dict: Dict) -> go.Figure:
        """Cria um gráfico de timeline de afastamentos."""
        data = []
        
        for aft in afastamentos:
            funcionario = funcionarios_dict.get(aft.funcionario_id)
            if funcionario and aft.data_inicio and aft.data_fim:
                data.append({
                    'Funcionário': funcionario.nome,
                    'Tipo': aft.tipo,
                    'Início': aft.data_inicio,
                    'Fim': aft.data_fim
                })
        
        if not data:
            return go.Figure().add_annotation(text="Nenhum afastamento para exibir")
        
        df = pd.DataFrame(data)
        
        fig = px.timeline(
            df,
            x_start='Início',
            x_end='Fim',
            y='Funcionário',
            color='Tipo',
            title='Timeline de Afastamentos',
            hover_data=['Tipo']
        )
        
        fig.update_layout(
            showlegend=True,
            hovermode='closest',
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def gráfico_salarios_por_cargo(funcionarios: List[Funcionario]) -> go.Figure:
        """Cria um gráfico de salários por cargo."""
        cargo_salarios = {}
        
        for func in funcionarios:
            if func.cargo and func.ativo:
                if func.cargo not in cargo_salarios:
                    cargo_salarios[func.cargo] = []
                cargo_salarios[func.cargo].append(func.salario)
        
        data = []
        for cargo, salarios in cargo_salarios.items():
            data.append({
                'Cargo': cargo,
                'Salário Médio': sum(salarios) / len(salarios),
                'Salário Mínimo': min(salarios),
                'Salário Máximo': max(salarios)
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('Salário Médio', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['Cargo'],
            y=df['Salário Médio'],
            name='Salário Médio',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title='Salários por Cargo',
            xaxis_title='Cargo',
            yaxis_title='Salário (R$)',
            template='plotly_white',
            hovermode='x unified'
        )
        
        fig.update_yaxes(tickformat='$,.0f')
        
        return fig
    
    @staticmethod
    def gráfico_taxa_afastamento(funcionarios: List[Funcionario], afastamentos: List[Afastamento]) -> go.Figure:
        """Cria um gráfico de taxa de afastamento."""
        total_funcionarios = len([f for f in funcionarios if f.ativo])
        funcionarios_afastados = len(set(aft.funcionario_id for aft in afastamentos))
        
        taxa = (funcionarios_afastados / total_funcionarios * 100) if total_funcionarios > 0 else 0
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=taxa,
            title={'text': "Taxa de Afastamento (%)"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 25], 'color': "lightgray"},
                    {'range': [25, 50], 'color': "gray"},
                    {'range': [50, 75], 'color': "orange"},
                    {'range': [75, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(template='plotly_white')
        
        return fig
