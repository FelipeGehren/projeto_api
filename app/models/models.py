from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class TipoUsuario(enum.Enum):
    CLIENTE = "cliente"
    FUNCIONARIO = "funcionario"
    ADMINISTRADOR = "administrador"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    telefone = Column(String(15), nullable=False)
    endereco = Column(String(200), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    tipo = Column(Enum(TipoUsuario), nullable=False, default=TipoUsuario.CLIENTE)
    matricula = Column(String(20), unique=True, nullable=True)  # Para funcionários
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    emprestimos = relationship("Emprestimo", back_populates="usuario")
    reservas = relationship("Reserva", back_populates="usuario")

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Relacionamentos
    livros = relationship("Livro", back_populates="categoria")

class Livro(Base):
    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    autor = Column(String(100), nullable=False)
    isbn = Column(String(13), unique=True, nullable=False)
    editora = Column(String(100), nullable=False)
    ano_publicacao = Column(Integer, nullable=False)
    edicao = Column(String(20), nullable=True)
    quantidade_total = Column(Integer, default=1)
    quantidade_disponivel = Column(Integer, default=1)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    localizacao = Column(String(50), nullable=False)  # Ex: "Prateleira A-1"
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    categoria = relationship("Categoria", back_populates="livros")
    emprestimos = relationship("Emprestimo", back_populates="livro")
    reservas = relationship("Reserva", back_populates="livro")

class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    livro_id = Column(Integer, ForeignKey("livros.id"), nullable=False)
    funcionario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)  # Funcionário que registrou o empréstimo
    data_emprestimo = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_devolucao_prevista = Column(DateTime, nullable=False)
    data_devolucao_real = Column(DateTime, nullable=True)
    status = Column(String(20), default="ativo")  # ativo, devolvido, atrasado
    observacoes = Column(Text, nullable=True)
    
    # Relacionamentos
    usuario = relationship("Usuario", foreign_keys=[usuario_id], back_populates="emprestimos")
    livro = relationship("Livro", back_populates="emprestimos")
    funcionario = relationship("Usuario", foreign_keys=[funcionario_id])

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    livro_id = Column(Integer, ForeignKey("livros.id"), nullable=False)
    data_reserva = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_limite = Column(DateTime, nullable=False)  # Data limite para retirar o livro
    status = Column(String(20), default="pendente")  # pendente, concluida, cancelada, expirada
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="reservas")
    livro = relationship("Livro", back_populates="reservas")

class Multa(Base):
    __tablename__ = "multas"

    id = Column(Integer, primary_key=True, index=True)
    emprestimo_id = Column(Integer, ForeignKey("emprestimos.id"), nullable=False)
    valor = Column(Integer, nullable=False)  # Valor em centavos
    data_geracao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_pagamento = Column(DateTime, nullable=True)
    status = Column(String(20), default="pendente")  # pendente, pago
    motivo = Column(Text, nullable=False)
    
    # Relacionamentos
    emprestimo = relationship("Emprestimo") 