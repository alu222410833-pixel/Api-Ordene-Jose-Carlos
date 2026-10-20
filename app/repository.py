"""Repositorio en memoria. En la sesión 6 se reemplaza por PostgreSQL."""

from datetime import datetime, timezone

from .schemas import OrderIn, OrderOut, OrderStatus


class OrderRepository:
    def __init__(self) -> None:
        self._items: dict[int, OrderOut] = {}
        self._next_id = 1

    def add(self, data: OrderIn) -> OrderOut:
        order = OrderOut(
            **data.model_dump(),
            id=self._next_id,
            total=round(data.cantidad * data.precio_unitario, 2),
            status=OrderStatus.pendiente,
            creada=datetime.now(timezone.utc),
        )
        self._items[order.id] = order
        self._next_id += 1
        return order

    def list(self, estado: OrderStatus | None = None) -> list[OrderOut]:
        orders = list(self._items.values())
        if estado is not None:
            orders = [o for o in orders if o.status == estado]
        return orders

    def get(self, order_id: int) -> OrderOut | None:
        return self._items.get(order_id)

    def update(self, order_id: int, data: OrderIn) -> OrderOut | None:
        current = self._items.get(order_id)
        if current is None:
            return None
        updated = current.model_copy(
            update={
                **data.model_dump(),
                "total": round(data.cantidad * data.precio_unitario, 2),
            }
        )
        self._items[order_id] = updated
        return updated

    def delete(self, order_id: int) -> bool:
        return self._items.pop(order_id, None) is not None

    def set_status(self, order_id: int, status: OrderStatus) -> OrderOut | None:
        current = self._items.get(order_id)
        if current is None:
            return None
        updated = current.model_copy(update={"status": status})
        self._items[order_id] = updated
        return updated


# Una sola instancia compartida por toda la app
repo = OrderRepository()


def get_repo() -> OrderRepository:
    """Dependencia de FastAPI. En las pruebas se reemplaza por un repo limpio."""
    return repo
