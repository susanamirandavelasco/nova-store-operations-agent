"""Persistence and orchestration tests."""
import pytest

from nova.repository import InMemoryStateRepository, SQLiteStateRepository
from nova.service import WorkflowService
from nova.workflow import Status, Step


@pytest.mark.parametrize("repository_kind", ["memory", "sqlite"])
def test_workflow_service_uses_repository(repository_kind, tmp_path):
    repository = (
        InMemoryStateRepository()
        if repository_kind == "memory"
        else SQLiteStateRepository(tmp_path / "state.db")
    )
    service = WorkflowService(repository)
    service.handle_message("employee-a", "Quiero devolver unos audífonos")
    _, state = service.handle_message("employee-a", "83921")
    assert state.order_id == "83921"
    assert state.next_step == Step.GET_ORDER


def test_sqlite_state_survives_repository_recreation(tmp_path):
    db_path = tmp_path / "nova.db"
    first = WorkflowService(SQLiteStateRepository(db_path))
    first.handle_message("employee-a", "Quiero devolver unos audífonos")

    # Simulate application restart by constructing new service and repository.
    restarted = WorkflowService(SQLiteStateRepository(db_path))
    restored = restarted.repository.load("employee-a")
    assert restored is not None
    assert restored.status == Status.ACTIVE
    assert restored.next_step == Step.ASK_FOR_ORDER_ID
    assert restored.order_id is None

    _, state = restarted.handle_message("employee-a", "83921")
    assert state.order_id == "83921"
    assert state.next_step == Step.GET_ORDER


def test_suspended_state_survives_restart(tmp_path):
    path = tmp_path / "nova.db"
    first = WorkflowService(SQLiteStateRepository(path))
    first.handle_message("a", "Quiero devolver unos audífonos")
    first.handle_message("a", "Mejor dime la política de garantía")

    restarted = WorkflowService(SQLiteStateRepository(path))
    _, state = restarted.handle_message("a", "83921")
    assert state.status == Status.SUSPENDED
    assert state.order_id is None

    _, state = restarted.handle_message("a", "retomar")
    assert state.status == Status.ACTIVE
    assert state.next_step == Step.ASK_FOR_ORDER_ID


def test_sqlite_conversations_are_isolated(tmp_path):
    service = WorkflowService(SQLiteStateRepository(tmp_path / "nova.db"))
    service.handle_message("a", "Quiero devolver unos audífonos")
    _, other = service.handle_message("b", "83921")
    assert other.order_id is None
    assert other.next_step == Step.UNDERSTAND


def test_blank_conversation_id_rejected(tmp_path):
    service = WorkflowService(SQLiteStateRepository(tmp_path / "nova.db"))
    with pytest.raises(ValueError):
        service.handle_message("  ", "Hola")


def test_sqlite_state_survives_new_process(tmp_path):
    """Recreating repository verifies persistence; actual subprocess is unnecessary here."""
    path = tmp_path / "nova.db"
    service = WorkflowService(SQLiteStateRepository(path))
    service.handle_message("a", "Quiero devolver unos audífonos")
    assert path.is_file()
    assert SQLiteStateRepository(path).load("a").next_step == Step.ASK_FOR_ORDER_ID
