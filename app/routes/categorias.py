from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from app.models import Categoria
from pydantic import BaseModel

router = APIRouter(
    prefix="/categorias",
    tags=["categorias"]
)

class CategoriaBase(BaseModel):
    nome: str
    descricao: str | None = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int
    data_cadastro: datetime
    data_atualizacao: datetime
    ativo: bool

    class Config:
        from_attributes = True

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def create_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = Categoria(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@router.get("/", response_model=List[CategoriaResponse])
def read_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categorias = db.query(Categoria).offset(skip).limit(limit).all()
    return categorias

@router.get("/{categoria_id}", response_model=CategoriaResponse)
def read_categoria(categoria_id: int, db: Session = Depends(get_db)):
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return db_categoria

@router.put("/{categoria_id}", response_model=CategoriaResponse)
def update_categoria(categoria_id: int, categoria: CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    for key, value in categoria.model_dump().items():
        setattr(db_categoria, key, value)
    
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    db.delete(db_categoria)
    db.commit()
    return None 