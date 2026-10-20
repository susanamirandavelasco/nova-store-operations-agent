import json
import pytest

from nova.intent_classifier import Intent, IntentClassifier, IntentResult


class FakeModel:
    def __init__(self, response: str):
        self.response = response
        self.calls = 0

    def classify_json(self, message: str) -> str:
        self.calls += 1
        return self.response


def test_return_request():
    model = FakeModel(json.dumps({
        "intent": "RETURN_REQUEST",
        "needs_clarification": False,
        "clarification_question": None,
    }))
    result = IntentClassifier(model).classify("Un cliente ya no quiere sus audífonos")
    assert result.intent == Intent.RETURN_REQUEST
    assert not result.needs_clarification


def test_ambiguous_message_asks_for_clarification():
    model = FakeModel(json.dumps({
        "intent": "UNKNOWN",
        "needs_clarification": True,
        "clarification_question": "¿Garantía o devolución?",
    }))
    result = IntentClassifier(model).classify("Tengo un problema con unos audífonos")
    assert result.needs_clarification
    assert result.clarification_question == "¿Garantía o devolución?"


@pytest.mark.parametrize("response", [
    "not json",
    '{"intent": "DO_SOMETHING_ELSE", "needs_clarification": false}',
    '{"intent": "UNKNOWN", "needs_clarification": false, "clarification_question": null}',
    '{"intent": "RETURN_REQUEST", "needs_clarification": "false", "clarification_question": null}',
])
def test_invalid_model_output_fails_safe(response):
    result = IntentClassifier(FakeModel(response)).classify("Hola")
    assert result.intent == Intent.UNKNOWN
    assert result.needs_clarification


def test_empty_message_does_not_call_model():
    model = FakeModel("ignored")
    result = IntentClassifier(model).classify("  ")
    assert result.needs_clarification
    assert model.calls == 0


def test_inconsistent_contract_rejected():
    with pytest.raises(ValueError):
        IntentResult(Intent.UNKNOWN, True, None)
