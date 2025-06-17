from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from app.models import Usuario, TipoUsuario
from pydantic import BaseModel, EmailStr, constr

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

class UsuarioBase(BaseModel):
    nome_completo: constr(min_length=3, max_length=100)
    cpf: constr(min_length=11, max_length=14)
    telefone: constr(min_length=10, max_length=15)
    endereco: constr(min_length=5, max_length=200)
    email: EmailStr
    tipo: TipoUsuario
    matricula: str | None = None
    limite_emprestimos: int = 3

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioResponse(UsuarioBase):
    id: int
    data_cadastro: datetime
    data_atualizacao: datetime
    ativo: bool

    class Config:
        from_attributes = True

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        # Verificar se já existe um usuário com o mesmo CPF
        db_usuario_cpf = db.query(Usuario).filter(Usuario.cpf == usuario.cpf).first()
        if db_usuario_cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )

        # Verificar se já existe um usuário com o mesmo email
        db_usuario_email = db.query(Usuario).filter(Usuario.email == usuario.email).first()
        if db_usuario_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )

        # Verificar se já existe um usuário com a mesma matrícula (se for funcionário)
        if usuario.tipo == TipoUsuario.FUNCIONARIO and usuario.matricula:
            db_usuario_matricula = db.query(Usuario).filter(Usuario.matricula == usuario.matricula).first()
            if db_usuario_matricula:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Matrícula já cadastrada"
                )

        # Criar novo usuário
        db_usuario = Usuario(
            nome_completo=usuario.nome_completo,
            cpf=usuario.cpf,
            telefone=usuario.telefone,
            endereco=usuario.endereco,
            email=usuario.email,
            tipo=usuario.tipo,
            matricula=usuario.matricula,
            limite_emprestimos=usuario.limite_emprestimos,
            data_cadastro=datetime.utcnow(),
            data_atualizacao=datetime.utcnow(),
            ativo=True
        )
        
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return db_usuario

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {str(e)}"
        )

@router.get("/", response_model=List[UsuarioResponse])
def read_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def read_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def update_usuario(usuario_id: int, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    try:
        # Atualizar os campos
        for key, value in usuario.model_dump().items():
            setattr(db_usuario, key, value)
        
        db_usuario.data_atualizacao = datetime.utcnow()
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar usuário: {str(e)}"
        )

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    try:
        db.delete(db_usuario)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar usuário: {str(e)}"
        ) 