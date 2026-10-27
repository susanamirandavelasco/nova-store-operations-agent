"""HTTP boundary tests do not need a real server, SQLite or OpenAI."""
from fastapi.testclient import TestClient

from nova.api import create_app
from nova.orders import FakeOrderRepository
from nova.repository import InMemoryStateRepository
from nova.return_evaluator import evaluate_return
from nova.service import WorkflowService


def client():
    service = WorkflowService(
        InMemoryStateRepository(),
        order_repository=FakeOrderRepository(),
        return_evaluator=evaluate_return,
    )
    return TestClient(create_app(service))


def test_health():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_preserves_conversation_across_requests():
    api = client()
    cid = "http-flow"
    def send(message):
        response = api.post("/chat", json={"conversation_id": cid, "message": message})
        assert response.status_code == 200
        return response.json()

    first = send("Quiero devolver unos audífonos")
    assert first["next_step"] == "ASK_FOR_ORDER_ID"
    assert first["status"] == "ACTIVE"
    assert first["conversation_id"] == cid
    assert send("83921")["next_step"] == "ASK_FOR_ORDER_DETAILS"
    assert send("audífonos")["next_step"] == "ASK_FOR_PRODUCT_CONDITION"
    final = send("Está sellado")
    assert "Recomendación: Elegible" in final["reply"]
    assert final["next_step"] == "GET_ORDER"


def test_chat_rejects_blank_or_missing_fields():
    api = client()
    for payload in [
        {"conversation_id": "", "message": "hola"},
        {"conversation_id": "   ", "message": "hola"},
        {"conversation_id": "c", "message": "  "},
        {"conversation_id": "c"},
        {"conversation_id": "c", "message": ""},
    ]:
        assert api.post("/chat", json=payload).status_code == 422


def test_chat_isolates_conversations():
    api = client()
    api.post("/chat", json={"conversation_id": "one", "message": "Quiero devolver audífonos"})
    other = api.post("/chat", json={"conversation_id": "two", "message": "83921"})
    assert other.json()["next_step"] == "UNDERSTAND"
