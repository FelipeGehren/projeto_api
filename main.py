import uvicorn 
from fastapi import FastAPI
from database import engine, Base 
from app.models import Usuario, Categoria, Livro, Emprestimo, Reserva, Multa
from app.routes import usuarios, categorias, livros, emprestimos, reservas, multas

app = FastAPI(
    title="API de Biblioteca",
    description="API para gerenciamento de biblioteca com usuários, livros e empréstimos",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)

@app.get("/")
def check_api():
    return "API online"

# Incluindo os routers
app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(livros.router)
app.include_router(emprestimos.router)
app.include_router(reservas.router)
app.include_router(multas.router)
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
