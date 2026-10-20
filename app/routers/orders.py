"""Router de Órdenes: CRUD completo sobre el repositorio en memoria."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from ..repository import OrderRepository, get_repo
from ..schemas import OrderIn, OrderOut, OrderStatus

router = APIRouter(prefix="/orders", tags=["Órdenes"])

Repo = Annotated[OrderRepository, Depends(get_repo)]


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def crear_orden(data: OrderIn, repo: Repo) -> OrderOut:
    return repo.add(data)


@router.get("", response_model=list[OrderOut])
def listar_ordenes(
    repo: Repo,
    estado: OrderStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[OrderOut]:
    return repo.list(estado)[offset : offset + limit]


@router.get("/{order_id}", response_model=OrderOut)
def obtener_orden(order_id: int, repo: Repo) -> OrderOut:
    order = repo.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order


@router.put("/{order_id}", response_model=OrderOut)
def actualizar_orden(order_id: int, data: OrderIn, repo: Repo) -> OrderOut:
    order = repo.update(order_id, data)
    if order is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order


@router.patch("/{order_id}/pagar", response_model=OrderOut)
def pagar_orden(order_id: int, repo: Repo) -> OrderOut:
    order = repo.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if order.status == OrderStatus.cancelada:
        raise HTTPException(status_code=409, detail="La orden está cancelada")
    return repo.set_status(order_id, OrderStatus.pagada)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_orden(order_id: int, repo: Repo) -> Response:
    if not repo.delete(order_id):
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
