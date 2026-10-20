"""Práctica 2 · API de Órdenes con FastAPI y Pydantic."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routers import orders

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Evento de arranque
    logger.info("API de Órdenes iniciada")
    yield
    # Evento de apagado
    logger.info("API de Órdenes detenida")


app = FastAPI(title="API de Órdenes", version="0.2.0", lifespan=lifespan)
app.include_router(orders.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
