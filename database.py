from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import pymysql

# Primeiro, conectamos sem especificar o banco de dados
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root'
)

try:
    with connection.cursor() as cursor:
        # Criar o banco de dados se não existir
        cursor.execute("CREATE DATABASE IF NOT EXISTS meu_projeto")
    connection.commit()
finally:
    connection.close()

# Agora conectamos ao banco de dados criado
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/meu_projeto"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = DeclarativeBase()

class Base(DeclarativeBase):
    __abstract__ = True
    __table_args__ = {'extend_existing': True}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()