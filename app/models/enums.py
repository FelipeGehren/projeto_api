import enum

class TipoUsuario(enum.Enum):
    CLIENTE = "cliente"
    FUNCIONARIO = "funcionario"
    ADMINISTRADOR = "administrador"

class StatusEmprestimo(enum.Enum):
    ATIVO = "ativo"
    DEVOLVIDO = "devolvido"
    ATRASADO = "atrasado"
    PERDIDO = "perdido"

class StatusReserva(enum.Enum):
    PENDENTE = "pendente"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"
    EXPIRADA = "expirada"

class StatusMulta(enum.Enum):
    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADA = "cancelada" 