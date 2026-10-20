"""Pruebas de la API de Órdenes. Ejecutar con: pytest -v"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository import OrderRepository, get_repo
from app.schemas import OrderStatus

ORDEN = {
    "cliente": "Ana López",
    "producto": "Teclado",
    "cantidad": 2,
    "precio_unitario": 350.0,
}


@pytest.fixture
def client():
    # Cada prueba usa un repositorio vacío
    repo = OrderRepository()
    app.dependency_overrides[get_repo] = lambda: repo
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_crear_orden_calcula_total(client):
    r = client.post("/orders", json=ORDEN)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["total"] == 700.0
    assert body["status"] == "pendiente"


def test_crear_orden_invalida_devuelve_422(client):
    r = client.post("/orders", json={**ORDEN, "cantidad": 0})
    assert r.status_code == 422


def test_obtener_orden_inexistente_devuelve_404(client):
    r = client.get("/orders/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Orden no encontrada"


def test_listar_actualizar_y_eliminar(client):
    client.post("/orders", json=ORDEN)
    assert len(client.get("/orders").json()) == 1

    r = client.put("/orders/1", json={**ORDEN, "cantidad": 3})
    assert r.status_code == 200
    assert r.json()["total"] == 1050.0

    assert client.delete("/orders/1").status_code == 204
    assert client.get("/orders/1").status_code == 404


def test_pagar_orden(client):
    client.post("/orders", json=ORDEN)

    r = client.patch("/orders/1/pagar")
    assert r.status_code == 200
    assert r.json()["status"] == "pagada"


def test_pagar_orden_cancelada_devuelve_409(client):
    client.post("/orders", json=ORDEN)
    repo = app.dependency_overrides[get_repo]()
    repo.set_status(1, OrderStatus.cancelada)

    r = client.patch("/orders/1/pagar")
    assert r.status_code == 409


def test_filtrar_por_estado_pagada(client):
    client.post("/orders", json=ORDEN)
    client.post("/orders", json=ORDEN)
    client.patch("/orders/1/pagar")

    r = client.get("/orders", params={"estado": "pagada"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["id"] == 1
    assert body[0]["status"] == "pagada"


def test_paginacion(client):
    for _ in range(3):
        client.post("/orders", json=ORDEN)

    r = client.get("/orders", params={"limit": 2, "offset": 1})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2
    assert body[0]["id"] == 2

    assert client.get("/orders", params={"limit": 0}).status_code == 422
    assert client.get("/orders", params={"limit": 51}).status_code == 422
    assert client.get("/orders", params={"offset": -1}).status_code == 422
