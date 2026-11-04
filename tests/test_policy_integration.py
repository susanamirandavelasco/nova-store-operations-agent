"""Policy integration preserves the deterministic return workflow."""
from nova.orders import FakeOrderRepository
from nova.policy_retrieval import PolicyRetriever
from nova.repository import InMemoryStateRepository
from nova.return_evaluator import evaluate_return
from nova.service import WorkflowService
from nova.workflow import Status, Step


def service():
    return WorkflowService(
        InMemoryStateRepository(),
        order_repository=FakeOrderRepository(),
        return_evaluator=evaluate_return,
        policy_retriever=PolicyRetriever(),
    )


def test_policy_question_cites_source():
    response, state = service().handle_message("p1", "¿Cuál es el plazo de devolución?")
    assert "30 días" in response
    assert "Fuente:" in response
    assert "POL-RET-001#plazo" in response
    assert state.status == Status.ACTIVE


def test_policy_interruption_preserves_pending_order_and_resumes():
    nova = service()
    nova.handle_message("p2", "Quiero devolver unos audífonos")
    _, before = nova.handle_message("p2", "83921")
    assert before.next_step == Step.ASK_FOR_ORDER_DETAILS
    response, interrupted = nova.handle_message("p2", "¿Cuál es el plazo de devolución?")
    assert "POL-RET-001#plazo" in response
    assert interrupted.status == Status.SUSPENDED
    assert interrupted.pending_order_id == "83921"
    assert interrupted.next_step == Step.ASK_FOR_ORDER_DETAILS
    _, resumed = nova.handle_message("p2", "retomar")
    assert resumed.status == Status.ACTIVE
    assert resumed.pending_order_id == "83921"
    assert resumed.next_step == Step.ASK_FOR_ORDER_DETAILS


def test_condition_answer_does_not_trigger_policy_lookup():
    nova = service()
    for message in ("Quiero devolver unos audífonos", "83921", "audífonos"):
        nova.handle_message("p3", message)
    response, state = nova.handle_message("p3", "Está sellado")
    assert "Recomendación:" in response
    assert "Fuente:" not in response
    assert state.next_step == Step.GET_ORDER


def test_unsupported_policy_question_abstains_without_source():
    response, _ = service().handle_message("p4", "¿Cuál es la política de horario de sucursal?")
    assert "No encontré información suficiente" in response
    assert "Fuente:" not in response
