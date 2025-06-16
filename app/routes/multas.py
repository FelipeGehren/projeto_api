from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from decimal import Decimal

from database import get_db
from app.models import Multa, StatusMulta, Emprestimo
from pydantic import BaseModel

router = APIRouter(
    prefix="/multas",
    tags=["multas"]
)

class MultaBase(BaseModel):
    emprestimo_id: int
    valor: Decimal
    motivo: str
    dias_atraso: int
    valor_por_dia: Decimal

class MultaCreate(MultaBase):
    pass

class MultaResponse(MultaBase):
    id: int
    data_geracao: datetime
    data_pagamento: datetime | None
    status: StatusMulta

    class Config:
        from_attributes = True

@router.post("/", response_model=MultaResponse, status_code=status.HTTP_201_CREATED)
def create_multa(multa: MultaCreate, db: Session = Depends(get_db)):
    # Verificar se o empréstimo existe e está atrasado
    emprestimo = db.query(Emprestimo).filter(Emprestimo.id == multa.emprestimo_id).first()
    if not emprestimo:
        raise HTTPException(status_code=400, detail="Empréstimo não encontrado")
    
    if emprestimo.status != "atrasado":
        raise HTTPException(status_code=400, detail="Multa só pode ser gerada para empréstimos atrasados")
    
    # Verificar se já existe uma multa pendente para este empréstimo
    multa_existente = db.query(Multa).filter(
        Multa.emprestimo_id == multa.emprestimo_id,
        Multa.status == StatusMulta.PENDENTE
    ).first()
    
    if multa_existente:
        raise HTTPException(status_code=400, detail="Já existe uma multa pendente para este empréstimo")
    
    # Criar a multa
    db_multa = Multa(**multa.model_dump())
    db.add(db_multa)
    db.commit()
    db.refresh(db_multa)
    return db_multa

@router.get("/", response_model=List[MultaResponse])
def read_multas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    multas = db.query(Multa).offset(skip).limit(limit).all()
    return multas

@router.get("/{multa_id}", response_model=MultaResponse)
def read_multa(multa_id: int, db: Session = Depends(get_db)):
    db_multa = db.query(Multa).filter(Multa.id == multa_id).first()
    if db_multa is None:
        raise HTTPException(status_code=404, detail="Multa não encontrada")
    return db_multa

@router.put("/{multa_id}/pagar", response_model=MultaResponse)
def pagar_multa(multa_id: int, db: Session = Depends(get_db)):
    db_multa = db.query(Multa).filter(Multa.id == multa_id).first()
    if db_multa is None:
        raise HTTPException(status_code=404, detail="Multa não encontrada")
    
    if db_multa.status != StatusMulta.PENDENTE:
        raise HTTPException(status_code=400, detail="Esta multa já foi paga ou cancelada")
    
    db_multa.status = StatusMulta.PAGO
    db_multa.data_pagamento = datetime.utcnow()
    
    db.commit()
    db.refresh(db_multa)
    return db_multa

@router.put("/{multa_id}/cancelar", response_model=MultaResponse)
def cancelar_multa(multa_id: int, db: Session = Depends(get_db)):
    db_multa = db.query(Multa).filter(Multa.id == multa_id).first()
    if db_multa is None:
        raise HTTPException(status_code=404, detail="Multa não encontrada")
    
    if db_multa.status != StatusMulta.PENDENTE:
        raise HTTPException(status_code=400, detail="Esta multa não pode ser cancelada")
    
    db_multa.status = StatusMulta.CANCELADA
    db.commit()
    db.refresh(db_multa)
    return db_multa

@router.delete("/{multa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_multa(multa_id: int, db: Session = Depends(get_db)):
    db_multa = db.query(Multa).filter(Multa.id == multa_id).first()
    if db_multa is None:
        raise HTTPException(status_code=404, detail="Multa não encontrada")
    
    db.delete(db_multa)
    db.commit()
    return None 