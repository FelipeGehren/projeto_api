from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, Text, Numeric, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base
from .enums import TipoUsuario, StatusEmprestimo, StatusReserva, StatusMulta
from .usuario import Usuario
from .categoria import Categoria
from .livro import Livro
from .emprestimo import Emprestimo
from .reserva import Reserva
from .multa import Multa

__all__ = [
    'TipoUsuario',
    'StatusEmprestimo',
    'StatusReserva',
    'StatusMulta',
    'Usuario',
    'Categoria',
    'Livro',
    'Emprestimo',
    'Reserva',
    'Multa'
]

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    telefone = Column(String(15), nullable=False)
    endereco = Column(String(200), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    tipo = Column(Enum(TipoUsuario), nullable=False, default=TipoUsuario.CLIENTE, index=True)
    matricula = Column(String(20), unique=True, nullable=True, index=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    limite_emprestimos = Column(Integer, default=3, nullable=False)
    
    # Relacionamentos
    emprestimos = relationship("Emprestimo", back_populates="usuario", cascade="all, delete-orphan")
    reservas = relationship("Reserva", back_populates="usuario", cascade="all, delete-orphan")
    emprestimos_registrados = relationship("Emprestimo", back_populates="funcionario", 
                                         foreign_keys="Emprestimo.funcionario_id")

    __table_args__ = (
        CheckConstraint('(tipo = \'funcionario\' AND matricula IS NOT NULL) OR (tipo != \'funcionario\' AND matricula IS NULL)',
                       name='check_matricula_funcionario'),
        CheckConstraint('limite_emprestimos > 0', name='check_limite_emprestimos'),
        Index('idx_usuario_ativo', 'ativo', 'tipo'),
    )

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    livros = relationship("Livro", back_populates="categoria", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_categoria_ativo', 'ativo'),
    )

class Livro(Base):
    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False, index=True)
    autor = Column(String(100), nullable=False, index=True)
    isbn = Column(String(13), unique=True, nullable=False, index=True)
    editora = Column(String(100), nullable=False)
    ano_publicacao = Column(Integer, nullable=False)
    edicao = Column(String(20), nullable=True)
    quantidade_total = Column(Integer, default=1, nullable=False)
    quantidade_disponivel = Column(Integer, default=1, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False, index=True)
    localizacao = Column(String(50), nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    sinopse = Column(Text, nullable=True)
    capa_url = Column(String(255), nullable=True)
    
    # Relacionamentos
    categoria = relationship("Categoria", back_populates="livros")
    emprestimos = relationship("Emprestimo", back_populates="livro", cascade="all, delete-orphan")
    reservas = relationship("Reserva", back_populates="livro", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('quantidade_disponivel >= 0', name='check_quantidade_disponivel'),
        CheckConstraint('quantidade_total >= quantidade_disponivel', name='check_quantidade_total'),
        CheckConstraint('ano_publicacao > 0', name='check_ano_publicacao'),
        Index('idx_livro_disponivel', 'quantidade_disponivel', 'categoria_id'),
    )

class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    livro_id = Column(Integer, ForeignKey("livros.id"), nullable=False, index=True)
    funcionario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    data_emprestimo = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_devolucao_prevista = Column(DateTime, nullable=False)
    data_devolucao_real = Column(DateTime, nullable=True)
    status = Column(Enum(StatusEmprestimo), default=StatusEmprestimo.ATIVO, nullable=False, index=True)
    observacoes = Column(Text, nullable=True)
    dias_emprestimo = Column(Integer, default=15, nullable=False)
    
    # Relacionamentos
    usuario = relationship("Usuario", foreign_keys=[usuario_id], back_populates="emprestimos")
    livro = relationship("Livro", back_populates="emprestimos")
    funcionario = relationship("Usuario", foreign_keys=[funcionario_id], back_populates="emprestimos_registrados")
    multas = relationship("Multa", back_populates="emprestimo", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('data_devolucao_prevista > data_emprestimo', name='check_data_devolucao'),
        CheckConstraint('dias_emprestimo > 0', name='check_dias_emprestimo'),
        Index('idx_emprestimo_status', 'status', 'data_devolucao_prevista'),
    )

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    livro_id = Column(Integer, ForeignKey("livros.id"), nullable=False, index=True)
    data_reserva = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_limite = Column(DateTime, nullable=False)
    status = Column(Enum(StatusReserva), default=StatusReserva.PENDENTE, nullable=False, index=True)
    prioridade = Column(Integer, default=1, nullable=False)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="reservas")
    livro = relationship("Livro", back_populates="reservas")

    __table_args__ = (
        CheckConstraint('data_limite > data_reserva', name='check_data_limite'),
        CheckConstraint('prioridade > 0', name='check_prioridade'),
        Index('idx_reserva_status', 'status', 'data_limite'),
    )

class Multa(Base):
    __tablename__ = "multas"

    id = Column(Integer, primary_key=True, index=True)
    emprestimo_id = Column(Integer, ForeignKey("emprestimos.id"), nullable=False, index=True)
    valor = Column(Numeric(10, 2), nullable=False)
    data_geracao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_pagamento = Column(DateTime, nullable=True)
    status = Column(Enum(StatusMulta), default=StatusMulta.PENDENTE, nullable=False, index=True)
    motivo = Column(Text, nullable=False)
    dias_atraso = Column(Integer, nullable=False)
    valor_por_dia = Column(Numeric(10, 2), nullable=False)
    
    # Relacionamentos
    emprestimo = relationship("Emprestimo", back_populates="multas")

    __table_args__ = (
        CheckConstraint('valor >= 0', name='check_valor_multa'),
        CheckConstraint('dias_atraso >= 0', name='check_dias_atraso'),
        CheckConstraint('valor_por_dia >= 0', name='check_valor_por_dia'),
        Index('idx_multa_status', 'status', 'data_geracao'),
    )
