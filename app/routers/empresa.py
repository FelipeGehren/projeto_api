from fastapi import APIRouter


router = APIRouter(prefix="/empresas")

"meulink.com/empresas"

@router.get("/")
def listar_empresas():
    return[
        {"id": 1,
        "cnpj": "12345678912345",
        "razao_social": "Empresa Teste Ltda.",
        "email_contato": "contato@teste.com"
        },
        {"id": 2,
        "cnpj": "98765432198712",
        "razao_social": "Empresa ABC",
        "email_contato": "contato@abc.com.br"}
    ]