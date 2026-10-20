"""Integration tests: the interpreter proposes, the workflow decides."""
from nova.intent_classifier import Intent, IntentResult
from nova.repository import InMemoryStateRepository
from nova.service import WorkflowService
from nova.workflow import Step, Status


class StubClassifier:
    def __init__(self, *results):
        self.results = list(results)
        self.messages = []

    def classify(self, message):
        self.messages.append(message)
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def resolved(intent):
    return IntentResult(intent, False, None)


def ambiguous(question="¿Garantía o devolución?"):
    return IntentResult(Intent.UNKNOWN, True, question)


def test_natural_language_starts_return_request():
    classifier = StubClassifier(resolved(Intent.RETURN_REQUEST))
    service = WorkflowService(InMemoryStateRepository(), classifier)
    reply, state = service.handle_message("a", "El cliente ya no quiere sus audífonos")
    assert state.next_step == Step.ASK_FOR_ORDER_ID
    assert "número de orden" in reply


def test_ambiguous_message_does_not_advance():
    classifier = StubClassifier(ambiguous())
    service = WorkflowService(InMemoryStateRepository(), classifier)
    reply, state = service.handle_message("a", "Tengo un problema")
    assert reply == "¿Garantía o devolución?"
    assert state.next_step == Step.UNDERSTAND
    assert state.order_id is None


def test_numeric_order_id_bypasses_llm():
    classifier = StubClassifier(resolved(Intent.RETURN_REQUEST))
    service = WorkflowService(InMemoryStateRepository(), classifier)
    service.handle_message("a", "Quiero devolver un producto")
    reply, state = service.handle_message("a", "83921")
    assert state.order_id == "83921"
    assert state.next_step == Step.GET_ORDER
    assert len(classifier.messages) == 1


def test_uncertain_order_number_does_not_advance():
    classifier = StubClassifier(resolved(Intent.RETURN_REQUEST), ambiguous("¿Puedes confirmar el número?"))
    service = WorkflowService(InMemoryStateRepository(), classifier)
    service.handle_message("a", "Quiero devolver un producto")
    reply, state = service.handle_message("a", "Creo que era 83921")
    assert reply == "¿Puedes confirmar el número?"
    assert state.order_id is None
    assert state.next_step == Step.ASK_FOR_ORDER_ID


def test_cancel_interrupts_order_entry():
    classifier = StubClassifier(resolved(Intent.RETURN_REQUEST), resolved(Intent.CANCEL))
    service = WorkflowService(InMemoryStateRepository(), classifier)
    service.handle_message("a", "Quiero devolver un producto")
    _, state = service.handle_message("a", "Mejor cancela")
    assert state.status == Status.CANCELLED
    assert state.next_step == Step.NONE


def test_model_failure_keeps_state():
    classifier = StubClassifier(resolved(Intent.RETURN_REQUEST), RuntimeError("offline"))
    service = WorkflowService(InMemoryStateRepository(), classifier)
    service.handle_message("a", "Quiero devolver un producto")
    reply, state = service.handle_message("a", "Creo que era 83921")
    assert "No pude interpretar" in reply
    assert state.order_id is None
    assert state.next_step == Step.ASK_FOR_ORDER_ID
