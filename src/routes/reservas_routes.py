import random

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import select

from src.config.database import get_session
from src.models.reservas_model import Reserva
from src.models.voos_model import Voo

reservas_router = APIRouter(prefix="/reservas")

@reservas_router.get("/voos/vendas")
def vendas_voo_com_limite(limite: int = 2):
    # Lógica da rota aqui
    pass

@reservas_router.get("/voos")
def lista_voos():
    with get_session() as session:
        voos = session.exec(select(Voo)).all()
        return voos

@reservas_router.post("/voos")
def cria_voo(voo: Voo):
    with get_session() as session:
        session.add(voo)
        session.commit()
        session.refresh(voo)
        return voo

@reservas_router.post("")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        # Verifique se já existe uma reserva para o mesmo documento
        existente = session.exec(select(Reserva).where(Reserva.documento == reserva.documento)).first()
        if existente:
            return JSONResponse(
                content={"message": "Já existe uma reserva para este documento."},
                status_code=400,
            )

        # Restante da lógica da rota
        # ...

@reservas_router.post("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        reserva = session.exec(select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)).first()

        if not reserva:
            return JSONResponse(
                content={"message": f"Reserva com código {codigo_reserva} não encontrada."},
                status_code=404,
            )

        # Verifique se a poltrona está disponível
        if not reserva.poltrona_disponivel(num_poltrona):
            return JSONResponse(
                content={"message": f"A poltrona {num_poltrona} não está disponível."},
                status_code=400,
            )

        # Realize o check-in
        reserva.realiza_checkin(num_poltrona)
        session.commit()
        
        return JSONResponse(content={"message": "Check-in realizado com sucesso."})

@reservas_router.patch("/{codigo_reserva}/checkin/{num_poltrona}")
def atualiza_checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        reserva = session.exec(select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)).first()

        if not reserva:
            return JSONResponse(
                content={"message": f"Reserva com código {codigo_reserva} não encontrada."},
                status_code=404,
            )

        # Verifique se a poltrona está disponível
        if not reserva.poltrona_disponivel(num_poltrona):
            return JSONResponse(
                content={"message": f"A poltrona {num_poltrona} não está disponível."},
                status_code=400,
            )

        # Atualize o check-in
        reserva.atualiza_checkin(num_poltrona)
        session.commit()
        
        return JSONResponse(content={"message": "Check-in atualizado com sucesso."})
