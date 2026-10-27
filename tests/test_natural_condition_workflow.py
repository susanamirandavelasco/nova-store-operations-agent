"""Integration tests: natural condition extraction precedes deterministic policy evaluation."""
from datetime import date

from nova.orders import FakeOrderRepository
from nova.repository import InMemoryStateRepository
from nova.return_evaluator import evaluate_return
from nova.service import WorkflowService
from nova.workflow import Step


def start():
    service = WorkflowService(
        InMemoryStateRepository(),
        order_repository=FakeOrderRepository(),
        return_evaluator=evaluate_return,
        evaluation_date=lambda: date(2026, 10, 26),
    )
    service.handle_message("a", "Quiero devolver unos audífonos")
    service.handle_message("a", "83921")
    service.handle_message("a", "audífonos")
    return service


def test_natural_sealed_condition_is_eligible():
    nova = start()
    response, state = nova.handle_message("a", "Está sellado")
    assert "Recomendación: Elegible para devolución" in response
    assert state.next_step == Step.GET_ORDER


def test_natural_opened_condition_requires_review():
    nova = start()
    response, state = nova.handle_message("a", "Ya lo abrí")
    assert "Recomendación: Se requiere revisión" in response
    assert state.next_step == Step.GET_ORDER


def test_ambiguous_condition_keeps_pending_step():
    nova = start()
    response, state = nova.handle_message("a", "Creo que está sellado")
    assert "¿Está sellado" in response
    assert state.next_step == Step.ASK_FOR_PRODUCT_CONDITION


def test_contradictory_condition_keeps_pending_step():
    nova = start()
    response, state = nova.handle_message("a", "Está sellado y dañado")
    assert "única condición" in response
    assert state.next_step == Step.ASK_FOR_PRODUCT_CONDITION


def test_clarification_then_evaluation():
    nova = start()
    nova.handle_message("a", "No sé")
    response, state = nova.handle_message("a", "Está sin abrir")
    assert "Recomendación: Elegible para devolución" in response
    assert state.next_step == Step.GET_ORDER
