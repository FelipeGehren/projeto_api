from fastapi import APIRouter
from pydantic import BaseModel
from typing import List


router = APIRouter(prefix="/empresas")

class CompanyResponse(BaseModel):
    id: int
    cnpj:str
    razao_social:str
    email_contato:str

@router.get("/", response_model=List[CompanyResponse])
def listar_empresas():
    return[
        CompanyResponse(
            id = 1,
            cnpj = "12345678912345",
            razao_social = "Empresa Teste Ltda.",
            email_contato = "contato@teste.com"
        )
    ]

@router.post("/")
def criar_empresas():
    return[
        {"id": 1,
        "cnpj": "12345678912345",
        "razao_social": "Empresa Teste Ltda.",
        "email_contato": "contato@teste.com"
        },
        {"id": 2,
        "cnpj": "98765432198712",
        "razao_social": "Empresa ABC",
        "email_contato": "contato@abc.com.br"
        },
    ]