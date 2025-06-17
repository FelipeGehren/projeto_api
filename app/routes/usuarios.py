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

# Schema para criação de usuário
class UsuarioCreate(BaseModel):
    nome_completo: constr(min_length=3, max_length=100)
    cpf: constr(regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    telefone: constr(regex=r'^\(\d{2}\) \d{5}-\d{4}$')
    endereco: constr(min_length=5, max_length=200)
    email: EmailStr
    tipo: TipoUsuario = TipoUsuario.CLIENTE
    matricula: str | None = None
    limite_emprestimos: int = 3

    class Config:
        json_schema_extra = {
            "example": {
                "nome_completo": "João Silva",
                "cpf": "123.456.789-00",
                "telefone": "(11) 98765-4321",
                "endereco": "Rua Exemplo, 123",
                "email": "joao@email.com",
                "tipo": "cliente",
                "matricula": None,
                "limite_emprestimos": 3
            }
        }

# Schema para resposta de usuário
class UsuarioResponse(BaseModel):
    id: int
    nome_completo: str
    cpf: str
    telefone: str
    endereco: str
    email: str
    tipo: TipoUsuario
    matricula: str | None
    data_cadastro: datetime
    data_atualizacao: datetime
    ativo: bool
    limite_emprestimos: int

    class Config:
        from_attributes = True

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        # Verificar se CPF já existe
        if db.query(Usuario).filter(Usuario.cpf == usuario.cpf).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
        
        # Verificar se email já existe
        if db.query(Usuario).filter(Usuario.email == usuario.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Verificar se matrícula já existe (apenas para funcionários)
        if usuario.tipo == TipoUsuario.FUNCIONARIO:
            if not usuario.matricula:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Matrícula é obrigatória para funcionários"
                )
            if db.query(Usuario).filter(Usuario.matricula == usuario.matricula).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Matrícula já cadastrada"
                )
        
        # Criar novo usuário
        db_usuario = Usuario(**usuario.model_dump())
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
def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    tipo: TipoUsuario | None = None,
    ativo: bool | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Usuario)
    
    if tipo:
        query = query.filter(Usuario.tipo == tipo)
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    try:
        # Verificar se CPF já existe (exceto para o próprio usuário)
        if db.query(Usuario).filter(
            Usuario.cpf == usuario.cpf,
            Usuario.id != usuario_id
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
        
        # Verificar se email já existe (exceto para o próprio usuário)
        if db.query(Usuario).filter(
            Usuario.email == usuario.email,
            Usuario.id != usuario_id
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Verificar se matrícula já existe (apenas para funcionários)
        if usuario.tipo == TipoUsuario.FUNCIONARIO:
            if not usuario.matricula:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Matrícula é obrigatória para funcionários"
                )
            if db.query(Usuario).filter(
                Usuario.matricula == usuario.matricula,
                Usuario.id != usuario_id
            ).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Matrícula já cadastrada"
                )
        
        # Atualizar usuário
        for key, value in usuario.model_dump().items():
            setattr(db_usuario, key, value)
        
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
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    try:
        # Verificar se usuário tem empréstimos ativos
        if db_usuario.emprestimos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível deletar usuário com empréstimos ativos"
            )
        
        # Verificar se usuário tem reservas ativas
        if db_usuario.reservas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível deletar usuário com reservas ativas"
            )
        
        db.delete(db_usuario)
        db.commit()
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar usuário: {str(e)}"
        )

@router.patch("/{usuario_id}/status", response_model=UsuarioResponse)
def alterar_status_usuario(
    usuario_id: int,
    ativo: bool,
    db: Session = Depends(get_db)
):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    try:
        # Verificar se usuário tem empréstimos ativos ao desativar
        if not ativo and db_usuario.emprestimos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível desativar usuário com empréstimos ativos"
            )
        
        db_usuario.ativo = ativo
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar status do usuário: {str(e)}"
        ) 