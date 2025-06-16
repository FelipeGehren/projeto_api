from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from database import get_db
from app.models import Reserva, StatusReserva, Livro, Usuario
from pydantic import BaseModel

router = APIRouter(
    prefix="/reservas",
    tags=["reservas"]
)

class ReservaBase(BaseModel):
    usuario_id: int
    livro_id: int
    data_limite: datetime
    prioridade: int = 1

class ReservaCreate(ReservaBase):
    pass

class ReservaResponse(ReservaBase):
    id: int
    data_reserva: datetime
    status: StatusReserva

    class Config:
        from_attributes = True

@router.post("/", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
def create_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    # Verificar se o livro existe
    livro = db.query(Livro).filter(Livro.id == reserva.livro_id).first()
    if not livro:
        raise HTTPException(status_code=400, detail="Livro não encontrado")
    
    # Verificar se o usuário existe e está ativo
    usuario = db.query(Usuario).filter(Usuario.id == reserva.usuario_id).first()
    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou inativo")
    
    # Verificar se já existe uma reserva ativa para este usuário e livro
    reserva_existente = db.query(Reserva).filter(
        Reserva.usuario_id == reserva.usuario_id,
        Reserva.livro_id == reserva.livro_id,
        Reserva.status == StatusReserva.PENDENTE
    ).first()
    
    if reserva_existente:
        raise HTTPException(status_code=400, detail="Usuário já possui uma reserva ativa para este livro")
    
    # Criar a reserva
    db_reserva = Reserva(**reserva.model_dump())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@router.get("/", response_model=List[ReservaResponse])
def read_reservas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reservas = db.query(Reserva).offset(skip).limit(limit).all()
    return reservas

@router.get("/{reserva_id}", response_model=ReservaResponse)
def read_reserva(reserva_id: int, db: Session = Depends(get_db)):
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if db_reserva is None:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return db_reserva

@router.put("/{reserva_id}/cancelar", response_model=ReservaResponse)
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if db_reserva is None:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    if db_reserva.status != StatusReserva.PENDENTE:
        raise HTTPException(status_code=400, detail="Esta reserva não pode ser cancelada")
    
    db_reserva.status = StatusReserva.CANCELADA
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reserva(reserva_id: int, db: Session = Depends(get_db)):
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if db_reserva is None:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    db.delete(db_reserva)
    db.commit()
    return None 