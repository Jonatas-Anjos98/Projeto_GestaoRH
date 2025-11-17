import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from src.utils import DatabaseSQL
from src.models import Funcionario, Afastamento, Usuario, PerfilUsuario, TipoAfastamento

# Inicializa o banco de dados
db = DatabaseSQL()

print("Inicializando banco de dados com dados de demonstração...")

# Cria usuários de demonstração
print("\n📝 Criando usuários...")

usuarios_demo = [
    {
        'nome': 'Administrador',
        'email': 'admin@rhcontrol.com',
        'username': 'admin',
        'senha': 'admin123',
        'perfil': PerfilUsuario.ADMIN.value
    },
    {
        'nome': 'Gerente de Loja',
        'email': 'gerente@rhcontrol.com',
        'username': 'gerente',
        'senha': 'gerente123',
        'perfil': PerfilUsuario.GERENTE.value
    },
    {
        'nome': 'Recursos Humanos',
        'email': 'rh@rhcontrol.com',
        'username': 'rh',
        'senha': 'rh123',
        'perfil': PerfilUsuario.RH.value
    }
]

for user_data in usuarios_demo:
    usuario = Usuario(
        nome=user_data['nome'],
        email=user_data['email'],
        username=user_data['username'],
        perfil=user_data['perfil']
    )
    usuario.definir_senha(user_data['senha'])
    db.criar_usuario(usuario)
    print(f"✓ Usuário criado: {user_data['username']}")

# Cria funcionários de demonstração
print("\n👥 Criando funcionários...")

funcionarios_demo = [
    {
        'nome': 'João Silva',
        'cpf': '123.456.789-10',
        'email': 'joao@empresa.com',
        'telefone': '(11) 98765-4321',
        'endereco': 'Rua A, 123',
        'loja': 'Loja Centro',
        'cargo': 'Gerente',
        'salario': 5000.00,
        'data_admissao': datetime.now() - timedelta(days=365)
    },
    {
        'nome': 'Maria Santos',
        'cpf': '234.567.890-11',
        'email': 'maria@empresa.com',
        'telefone': '(11) 98765-4322',
        'endereco': 'Rua B, 456',
        'loja': 'Loja Centro',
        'cargo': 'Vendedor',
        'salario': 2500.00,
        'data_admissao': datetime.now() - timedelta(days=180)
    },
    {
        'nome': 'Pedro Oliveira',
        'cpf': '345.678.901-12',
        'email': 'pedro@empresa.com',
        'telefone': '(11) 98765-4323',
        'endereco': 'Rua C, 789',
        'loja': 'Loja Norte',
        'cargo': 'Vendedor',
        'salario': 2500.00,
        'data_admissao': datetime.now() - timedelta(days=90)
    },
    {
        'nome': 'Ana Costa',
        'cpf': '456.789.012-13',
        'email': 'ana@empresa.com',
        'telefone': '(11) 98765-4324',
        'endereco': 'Rua D, 321',
        'loja': 'Loja Sul',
        'cargo': 'Gerente',
        'salario': 5000.00,
        'data_admissao': datetime.now() - timedelta(days=730)
    }
]

funcionarios_criados = []
for func_data in funcionarios_demo:
    funcionario = Funcionario(**func_data)
    funcionario = db.criar_funcionario(funcionario)
    funcionarios_criados.append(funcionario)
    print(f"✓ Funcionário criado: {func_data['nome']}")

# Cria afastamentos de demonstração
print("\n📋 Criando afastamentos...")

afastamentos_demo = [
    {
        'funcionario_id': funcionarios_criados[0].id,
        'tipo': TipoAfastamento.FERIAS.value,
        'data_inicio': datetime.now() - timedelta(days=30),
        'data_fim': datetime.now() - timedelta(days=20),
        'motivo': 'Férias anuais',
        'observacoes': 'Férias planejadas'
    },
    {
        'funcionario_id': funcionarios_criados[1].id,
        'tipo': TipoAfastamento.ATESTADO_MEDICO.value,
        'data_inicio': datetime.now() - timedelta(days=5),
        'data_fim': datetime.now() - timedelta(days=3),
        'motivo': 'Consulta médica',
        'observacoes': 'Atestado médico apresentado'
    },
    {
        'funcionario_id': funcionarios_criados[2].id,
        'tipo': TipoAfastamento.FALTA.value,
        'data_inicio': datetime.now() - timedelta(days=2),
        'data_fim': datetime.now() - timedelta(days=2),
        'motivo': 'Falta injustificada',
        'observacoes': 'Falta não justificada'
    },
    {
        'funcionario_id': funcionarios_criados[3].id,
        'tipo': TipoAfastamento.LICENCA_MATERNIDADE.value,
        'data_inicio': datetime.now() + timedelta(days=30),
        'data_fim': datetime.now() + timedelta(days=150),
        'motivo': 'Licença-maternidade',
        'observacoes': 'Licença-maternidade de 120 dias'
    }
]

for aft_data in afastamentos_demo:
    afastamento = Afastamento(**aft_data)
    db.criar_afastamento(afastamento)
    print(f"✓ Afastamento criado: {aft_data['tipo']}")

print("\n✅ Banco de dados inicializado com sucesso!")
print("\n📝 Dados de acesso para demonstração:")
print("   Usuário: admin")
print("   Senha: admin123")
