import uvicorn 
from fastapi import FastAPI
from database import engine, Base 
from app.models import Usuario, Categoria, Livro, Emprestimo, Reserva, Multa

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Biblioteca",
    description="API para gerenciamento de biblioteca com usuários, livros e empréstimos",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

@app.get("/")
def check_api():
    return "API online"

# Aqui serão incluídos os routers quando criarmos
# app.include_router(usuarios.router)
# app.include_router(livros.router)
# app.include_router(emprestimos.router)
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
