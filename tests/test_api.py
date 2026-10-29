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


def test_chat_rejects_malformed_payloads_and_excessive_lengths():
    api = client()
    cases = [
        None,
        [],
        {"conversation_id": "c", "message": 123},
        {"conversation_id": "c", "message": "x" * 4001},
        {"conversation_id": "x" * 129, "message": "hola"},
        {"conversation_id": "c", "message": None},
    ]
    for payload in cases:
        response = api.post("/chat", json=payload)
        assert response.status_code == 422


def test_chat_rejects_wrong_http_method():
    assert client().get("/chat").status_code == 405


def test_api_response_exposes_only_public_contract_fields():
    response = client().post(
        "/chat", json={"conversation_id": "c", "message": "Quiero devolver unos audífonos"}
    )
    assert response.status_code == 200
    assert set(response.json()) == {"conversation_id", "reply", "next_step", "status"}


def test_web_chat_home_and_static_assets():
    api = client()
    home = api.get("/")
    assert home.status_code == 200
    assert "text/html" in home.headers["content-type"]
    assert 'id="chat-form"' in home.text
    assert 'id="messages"' in home.text
    script = api.get("/ui/app.js")
    assert script.status_code == 200
    assert 'fetch("/chat"' in script.text
    assert "textContent" in script.text
    stylesheet = api.get("/ui/style.css")
    assert stylesheet.status_code == 200
    assert ".bubble" in stylesheet.text
