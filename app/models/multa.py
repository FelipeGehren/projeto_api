from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Numeric, Text, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .enums import StatusMulta
from database import Base

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