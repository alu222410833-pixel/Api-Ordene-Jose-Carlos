"""Práctica 1 · Mi primer servidor web con FastAPI."""

from fastapi import FastAPI

app = FastAPI(title="API de Órdenes", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Verifica que el servidor está vivo."""
    return {"status": "ok"}


@app.get("/saludo/{nombre}")
def saludar(nombre: str, mayusculas: bool = False) -> dict[str, str]:
    """`nombre` es parámetro de ruta; `mayusculas` es parámetro de query."""
    mensaje = f"Hola, {nombre}"
    if mayusculas:
        mensaje = mensaje.upper()
    return {"mensaje": mensaje}


@app.get("/cuadrado/{n}")
def cuadrado(n: int) -> dict[str, int]:
    """FastAPI convierte y valida `n` gracias al type hint `int`."""
    return {"n": n, "cuadrado": n * n}
