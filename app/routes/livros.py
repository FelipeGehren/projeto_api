from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from app.models import Livro
from pydantic import BaseModel

router = APIRouter(
    prefix="/livros",
    tags=["livros"]
)

class LivroBase(BaseModel):
    titulo: str
    autor: str
    isbn: str
    editora: str
    ano_publicacao: int
    edicao: str | None = None
    quantidade_total: int = 1
    quantidade_disponivel: int = 1
    categoria_id: int
    localizacao: str
    sinopse: str | None = None
    capa_url: str | None = None

class LivroCreate(LivroBase):
    pass

class LivroResponse(LivroBase):
    id: int
    data_cadastro: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=LivroResponse, status_code=status.HTTP_201_CREATED)
def create_livro(livro: LivroCreate, db: Session = Depends(get_db)):
    db_livro = Livro(**livro.model_dump())
    db.add(db_livro)
    db.commit()
    db.refresh(db_livro)
    return db_livro

@router.get("/", response_model=List[LivroResponse])
def read_livros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    livros = db.query(Livro).offset(skip).limit(limit).all()
    return livros

@router.get("/{livro_id}", response_model=LivroResponse)
def read_livro(livro_id: int, db: Session = Depends(get_db)):
    db_livro = db.query(Livro).filter(Livro.id == livro_id).first()
    if db_livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return db_livro

@router.put("/{livro_id}", response_model=LivroResponse)
def update_livro(livro_id: int, livro: LivroCreate, db: Session = Depends(get_db)):
    db_livro = db.query(Livro).filter(Livro.id == livro_id).first()
    if db_livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    for key, value in livro.model_dump().items():
        setattr(db_livro, key, value)
    
    db.commit()
    db.refresh(db_livro)
    return db_livro

@router.delete("/{livro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_livro(livro_id: int, db: Session = Depends(get_db)):
    db_livro = db.query(Livro).filter(Livro.id == livro_id).first()
    if db_livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    db.delete(db_livro)
    db.commit()
    return None 