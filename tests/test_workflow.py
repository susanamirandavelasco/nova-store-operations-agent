"""State transitions are deterministic and testable."""

from nova.workflow import InMemoryConversationStore, Status, Step


def test_missing_order_id_then_valid_reply():
    store = InMemoryConversationStore()
    _, state = store.handle_message("a", "Quiero devolver unos audífonos")
    assert state.next_step == Step.ASK_FOR_ORDER_ID
    assert state.order_id is None

    _, state = store.handle_message("a", "83921")
    assert state.order_id == "83921"
    assert state.next_step == Step.GET_ORDER


def test_invalid_order_id_does_not_advance():
    store = InMemoryConversationStore()
    store.handle_message("a", "Quiero devolver unos audífonos")
    _, state = store.handle_message("a", "abc")
    assert state.next_step == Step.ASK_FOR_ORDER_ID
    assert state.order_id is None


def test_suspend_resume_preserves_step():
    store = InMemoryConversationStore()
    store.handle_message("a", "Quiero devolver unos audífonos")
    _, state = store.handle_message("a", "Mejor dime la política de garantía")
    assert state.status == Status.SUSPENDED
    assert state.next_step == Step.ASK_FOR_ORDER_ID

    _, state = store.handle_message("a", "retomar")
    assert state.status == Status.ACTIVE
    assert state.next_step == Step.ASK_FOR_ORDER_ID


def test_suspended_order_id_does_not_advance():
    store = InMemoryConversationStore()
    store.handle_message("a", "Quiero devolver unos audífonos")
    store.handle_message("a", "Mejor dime la política de garantía")
    _, state = store.handle_message("a", "83921")
    assert state.status == Status.SUSPENDED
    assert state.order_id is None


def test_cancelled_workflow_cannot_be_resumed():
    store = InMemoryConversationStore()
    store.handle_message("a", "Quiero devolver unos audífonos")
    _, state = store.handle_message("a", "cancelar")
    assert state.status == Status.CANCELLED
    assert state.next_step == Step.NONE

    _, state = store.handle_message("a", "retomar")
    assert state.status == Status.CANCELLED
    assert state.next_step == Step.NONE


def test_new_request_after_cancellation():
    store = InMemoryConversationStore()
    store.handle_message("a", "Quiero devolver unos audífonos")
    store.handle_message("a", "cancelar")
    _, state = store.handle_message("a", "Quiero devolver otra compra")
    assert state.status == Status.ACTIVE
    assert state.next_step == Step.ASK_FOR_ORDER_ID


def test_conversations_are_isolated():
    store = InMemoryConversationStore()
    store.handle_message("a", "Quiero devolver unos audífonos")
    _, other = store.handle_message("b", "83921")
    assert other.order_id is None
    assert other.next_step == Step.UNDERSTAND
