from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

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