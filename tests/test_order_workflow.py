"""Stateful integration tests for provisional order verification."""
import sqlite3

from nova.orders import FakeOrderRepository
from nova.repository import InMemoryStateRepository, SQLiteStateRepository
from nova.service import WorkflowService
from nova.workflow import Step, Status


def service(repository=None):
    return WorkflowService(
        repository or InMemoryStateRepository(),
        order_repository=FakeOrderRepository(),
    )


def test_candidate_requires_corroborration():
    nova = service()
    nova.handle_message("a", "Quiero devolver unos audífonos")
    _, state = nova.handle_message("a", "Creo que era la 83921")
    assert state.pending_order_id == "83921"
    assert state.order_id is None
    assert state.next_step == Step.ASK_FOR_ORDER_DETAILS


def test_matching_details_confirm_order():
    nova = service()
    nova.handle_message("a", "Quiero devolver unos audífonos")
    nova.handle_message("a", "83921")
    response, state = nova.handle_message("a", "audífonos")
    assert state.order_id == "83921"
    assert state.pending_order_id is None
    assert state.next_step == Step.GET_ORDER
    assert "elegibilidad" in response


def test_mismatch_stays_provisional():
    nova = service()
    nova.handle_message("a", "Quiero devolver unos audífonos")
    nova.handle_message("a", "83921")
    response, state = nova.handle_message("a", "televisor")
    assert "no coinciden" in response
    assert state.order_id is None
    assert state.pending_order_id == "83921"
    assert state.next_step == Step.ASK_FOR_ORDER_DETAILS


def test_nonexistent_order_stays_provisional():
    nova = service()
    nova.handle_message("a", "Quiero devolver unos audífonos")
    nova.handle_message("a", "99999")
    _, state = nova.handle_message("a", "audífonos")
    assert state.order_id is None
    assert state.pending_order_id == "99999"


def test_cancel_clears_candidate():
    nova = service()
    nova.handle_message("a", "Quiero devolver unos audífonos")
    nova.handle_message("a", "83921")
    _, state = nova.handle_message("a", "cancelar")
    assert state.status == Status.CANCELLED
    assert state.pending_order_id is None
    assert state.order_id is None


def test_restart_preserves_candidate(tmp_path):
    path = tmp_path / "nova.db"
    first = service(SQLiteStateRepository(path))
    first.handle_message("a", "Quiero devolver unos audífonos")
    first.handle_message("a", "83921")
    restarted = service(SQLiteStateRepository(path))
    restored = restarted.repository.load("a")
    assert restored.pending_order_id == "83921"
    assert restored.order_id is None
    _, state = restarted.handle_message("a", "audífonos")
    assert state.order_id == "83921"
    assert state.pending_order_id is None


def test_sqlite_migrates_existing_schema(tmp_path):
    path = tmp_path / "legacy.db"
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE conversation_states ("
            "conversation_id TEXT PRIMARY KEY, intent TEXT NOT NULL, "
            "order_id TEXT, next_step TEXT NOT NULL, status TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO conversation_states VALUES (?, ?, ?, ?, ?)",
            ("a", "RETURN_REQUEST", None, "ASK_FOR_ORDER_ID", "ACTIVE"),
        )
    repository = SQLiteStateRepository(path)
    restored = repository.load("a")
    assert restored.next_step == Step.ASK_FOR_ORDER_ID
    assert restored.pending_order_id is None
    repository.save("a", restored)


def test_unrecognized_candidate_not_saved():
    nova = service()
    nova.handle_message("a", "Quiero devolver unos audífonos")
    _, state = nova.handle_message("a", "Tal vez ochenta y tres mil")
    assert state.pending_order_id is None
    assert state.next_step == Step.ASK_FOR_ORDER_ID
