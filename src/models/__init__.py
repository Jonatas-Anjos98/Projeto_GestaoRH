"""Modelos de dados da aplicação."""

from .funcionario import Funcionario
from .afastamento import Afastamento, TipoAfastamento
from .usuario import Usuario, PerfilUsuario

__all__ = ["Funcionario", "Afastamento", "TipoAfastamento", "Usuario", "PerfilUsuario"]
