from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.enums import TipoUsuario
from database import Base

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
    emprestimos = relationship(
        "Emprestimo",
        back_populates="usuario",
        primaryjoin="Usuario.id == Emprestimo.usuario_id",
        cascade="all, delete-orphan"
    )
    
    reservas = relationship(
        "Reserva",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )
    
    emprestimos_registrados = relationship(
        "Emprestimo",
        back_populates="funcionario",
        primaryjoin="Usuario.id == Emprestimo.funcionario_id"
    )

    __table_args__ = (
        CheckConstraint('(tipo = \'funcionario\' AND matricula IS NOT NULL) OR (tipo != \'funcionario\' AND matricula IS NULL)',
                       name='check_matricula_funcionario'),
        CheckConstraint('limite_emprestimos > 0', name='check_limite_emprestimos'),
        Index('idx_usuario_ativo', 'ativo', 'tipo'),
    ) 