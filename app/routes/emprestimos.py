from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from database import get_db
from app.models import Emprestimo, StatusEmprestimo, Livro, Usuario
from pydantic import BaseModel

router = APIRouter(
    prefix="/emprestimos",
    tags=["emprestimos"]
)

class EmprestimoBase(BaseModel):
    usuario_id: int
    livro_id: int
    funcionario_id: int
    data_devolucao_prevista: datetime
    dias_emprestimo: int = 15
    observacoes: str | None = None

class EmprestimoCreate(EmprestimoBase):
    pass

class EmprestimoResponse(EmprestimoBase):
    id: int
    data_emprestimo: datetime
    data_devolucao_real: datetime | None
    status: StatusEmprestimo

    class Config:
        from_attributes = True

@router.post("/", response_model=EmprestimoResponse, status_code=status.HTTP_201_CREATED)
def create_emprestimo(emprestimo: EmprestimoCreate, db: Session = Depends(get_db)):
    # Verificar se o livro está disponível
    livro = db.query(Livro).filter(Livro.id == emprestimo.livro_id).first()
    if not livro or livro.quantidade_disponivel <= 0:
        raise HTTPException(status_code=400, detail="Livro não disponível para empréstimo")
    
    # Verificar se o usuário existe e está ativo
    usuario = db.query(Usuario).filter(Usuario.id == emprestimo.usuario_id).first()
    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou inativo")
    
    # Verificar se o funcionário existe e é do tipo funcionário
    funcionario = db.query(Usuario).filter(Usuario.id == emprestimo.funcionario_id).first()
    if not funcionario or funcionario.tipo != "funcionario":
        raise HTTPException(status_code=400, detail="Funcionário não encontrado ou inválido")
    
    # Criar o empréstimo
    db_emprestimo = Emprestimo(**emprestimo.model_dump())
    db.add(db_emprestimo)
    
    # Atualizar quantidade disponível do livro
    livro.quantidade_disponivel -= 1
    
    db.commit()
    db.refresh(db_emprestimo)
    return db_emprestimo

@router.get("/", response_model=List[EmprestimoResponse])
def read_emprestimos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    emprestimos = db.query(Emprestimo).offset(skip).limit(limit).all()
    return emprestimos

@router.get("/{emprestimo_id}", response_model=EmprestimoResponse)
def read_emprestimo(emprestimo_id: int, db: Session = Depends(get_db)):
    db_emprestimo = db.query(Emprestimo).filter(Emprestimo.id == emprestimo_id).first()
    if db_emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    return db_emprestimo

@router.put("/{emprestimo_id}/devolver", response_model=EmprestimoResponse)
def devolver_livro(emprestimo_id: int, db: Session = Depends(get_db)):
    db_emprestimo = db.query(Emprestimo).filter(Emprestimo.id == emprestimo_id).first()
    if db_emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    
    if db_emprestimo.status != StatusEmprestimo.ATIVO:
        raise HTTPException(status_code=400, detail="Este empréstimo já foi devolvido")
    
    # Atualizar status e data de devolução
    db_emprestimo.status = StatusEmprestimo.DEVOLVIDO
    db_emprestimo.data_devolucao_real = datetime.utcnow()
    
    # Atualizar quantidade disponível do livro
    livro = db.query(Livro).filter(Livro.id == db_emprestimo.livro_id).first()
    livro.quantidade_disponivel += 1
    
    db.commit()
    db.refresh(db_emprestimo)
    return db_emprestimo

@router.delete("/{emprestimo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_emprestimo(emprestimo_id: int, db: Session = Depends(get_db)):
    db_emprestimo = db.query(Emprestimo).filter(Emprestimo.id == emprestimo_id).first()
    if db_emprestimo is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    
    # Se o empréstimo estiver ativo, devolver o livro
    if db_emprestimo.status == StatusEmprestimo.ATIVO:
        livro = db.query(Livro).filter(Livro.id == db_emprestimo.livro_id).first()
        livro.quantidade_disponivel += 1
    
    db.delete(db_emprestimo)
    db.commit()
    return None 