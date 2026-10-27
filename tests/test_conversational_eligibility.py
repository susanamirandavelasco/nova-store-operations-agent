"""End-to-end tests for opt-in conversational eligibility."""
from datetime import date

from nova.repository import InMemoryStateRepository, SQLiteStateRepository
from nova.orders import FakeOrderRepository
from nova.return_evaluator import evaluate_return
from nova.service import WorkflowService
from nova.workflow import Step


def make_service(repository=None):
    return WorkflowService(
        repository or InMemoryStateRepository(),
        order_repository=FakeOrderRepository(),
        return_evaluator=evaluate_return,
        evaluation_date=lambda: date(2026, 10, 26),
    )


def verified(service):
    service.handle_message("session", "Quiero devolver unos audífonos")
    service.handle_message("session", "83921")
    return service.handle_message("session", "audífonos")


def test_verified_order_requests_condition():
    nova = make_service()
    response, state = verified(nova)
    assert state.next_step == Step.ASK_FOR_PRODUCT_CONDITION
    assert state.order_id == "83921"
    assert "condición" in response


def test_sealed_electronics_recommended_eligible():
    nova = make_service()
    verified(nova)
    response, state = nova.handle_message("session", "SEALED")
    assert "Recomendación: ELIGIBLE" in response
    assert "plazo:" in response
    assert "condición:" in response
    assert "categoría:" in response
    assert "No autoriza ni ejecuta" in response
    assert state.next_step == Step.GET_ORDER


def test_unknown_condition_needs_review():
    nova = make_service()
    verified(nova)
    response, _ = nova.handle_message("session", "UNKNOWN")
    assert "Recomendación: NEEDS_REVIEW" in response


def test_invalid_condition_keeps_prompt():
    nova = make_service()
    verified(nova)
    response, state = nova.handle_message("session", "Creo que bien")
    assert "No pude confirmar una única condición" in response
    assert "¿Está sellado, abierto o dañado?" in response
    assert state.next_step == Step.ASK_FOR_PRODUCT_CONDITION


def test_condition_step_survives_sqlite_restart(tmp_path):
    path = tmp_path / "nova.db"
    first = make_service(SQLiteStateRepository(path))
    verified(first)
    restarted = make_service(SQLiteStateRepository(path))
    response, state = restarted.handle_message("session", "SEALED")
    assert "Recomendación: ELIGIBLE" in response
    assert state.order_id == "83921"


def test_cancel_during_condition_clears_order():
    nova = make_service()
    verified(nova)
    _, state = nova.handle_message("session", "cancelar")
    assert state.order_id is None
    assert state.next_step == Step.NONE
