"""The CLI demo is opt-in and composes the existing deterministic adapters."""
from nova.__main__ import build_service
from nova.workflow import Step


def test_default_cli_does_not_enable_order_lookup(tmp_path):
    service = build_service(db_path=str(tmp_path / "default.sqlite3"))
    assert service.order_repository is None
    assert service.return_evaluator is None


def test_demo_cli_enables_fictional_return_flow(tmp_path):
    service = build_service(demo=True, db_path=str(tmp_path / "demo.sqlite3"))
    conversation = "cli-test"
    service.handle_message(conversation, "Quiero devolver unos audífonos")
    service.handle_message(conversation, "83921")
    response, state = service.handle_message(conversation, "audífonos")
    assert "condición" in response
    assert state.next_step == Step.ASK_FOR_PRODUCT_CONDITION
    response, state = service.handle_message(conversation, "Está sellado")
    assert "Recomendación: Elegible" in response
    assert "no autoriza ni ejecuta" in response
    assert state.next_step == Step.GET_ORDER


def test_demo_cli_restores_state_from_sqlite(tmp_path):
    path = str(tmp_path / "resume.sqlite3")
    first = build_service(demo=True, db_path=path)
    first.handle_message("resume", "Quiero devolver unos audífonos")
    first.handle_message("resume", "83921")
    restarted = build_service(demo=True, db_path=path)
    response, state = restarted.handle_message("resume", "audífonos")
    assert state.next_step == Step.ASK_FOR_PRODUCT_CONDITION
    assert "condición" in response
