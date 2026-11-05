"""Session 13: persistence and workflow continuity regression."""
from fastapi.testclient import TestClient

from nova.api import create_app
from nova.__main__ import build_service


def test_return_flow_continues_after_api_recreation(tmp_path):
    db_path = str(tmp_path / "nova.sqlite3")
    conversation_id = "session13-persisted-return"

    first = TestClient(create_app(
        build_service(demo=True, db_path=db_path)
    ))

    def send(client, message):
        response = client.post(
            "/chat",
            json={
                "conversation_id": conversation_id,
                "message": message,
            },
        )
        assert response.status_code == 200
        return response.json()

    assert send(first, "Quiero devolver unos audífonos")["next_step"] == "ASK_FOR_ORDER_ID"

    provisional = send(first, "83921")
    assert provisional["next_step"] == "ASK_FOR_ORDER_DETAILS"
    assert "referencia provisional" in provisional["reply"]

    # Recreate the API/service using the same SQLite database.
    second = TestClient(create_app(
        build_service(demo=True, db_path=db_path)
    ))

    verified = send(second, "Audífonos")
    assert verified["next_step"] == "ASK_FOR_PRODUCT_CONDITION"
    assert verified["status"] == "ACTIVE"
    assert "Los datos coinciden con la orden 83921" in verified["reply"]

    final = send(second, "Está sellado")
    assert "Recomendación: Elegible" in final["reply"]
    assert final["next_step"] == "GET_ORDER"