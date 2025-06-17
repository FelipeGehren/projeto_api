from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

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