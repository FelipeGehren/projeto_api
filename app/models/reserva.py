from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .enums import StatusReserva
from database import Base

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