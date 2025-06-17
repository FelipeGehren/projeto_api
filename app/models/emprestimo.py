from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Text, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .enums import StatusEmprestimo
from database import Base

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
    usuario = relationship(
        "Usuario",
        back_populates="emprestimos",
        foreign_keys=[usuario_id]
    )
    livro = relationship("Livro", back_populates="emprestimos")
    funcionario = relationship(
        "Usuario",
        back_populates="emprestimos_registrados",
        foreign_keys=[funcionario_id]
    )
    multas = relationship("Multa", back_populates="emprestimo", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('data_devolucao_prevista > data_emprestimo', name='check_data_devolucao'),
        CheckConstraint('dias_emprestimo > 0', name='check_dias_emprestimo'),
        Index('idx_emprestimo_status', 'status', 'data_devolucao_prevista'),
    ) 