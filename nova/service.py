"""Application orchestration: load state, interpret message, route, persist."""
from typing import Protocol

from nova.intent_classifier import IntentResult
from nova.repository import StateRepository
from nova.workflow import NovaState, Step, Status, extract_order_id, route


class IntentInterpreter(Protocol):
    def classify(self, message: str) -> IntentResult:
        ...


class WorkflowService:
    def __init__(
        self, repository: StateRepository,
        classifier: IntentInterpreter | None = None,
    ) -> None:
        self.repository = repository
        self.classifier = classifier

    def handle_message(self, conversation_id: str, message: str) -> tuple[str, NovaState]:
        if not conversation_id.strip():
            raise ValueError("conversation_id cannot be blank")

        state = self.repository.load(conversation_id)
        if state is None:
            state = NovaState()

        if self.classifier is None:
            response = route(state, message)
        elif (state.status == Status.ACTIVE
              and state.next_step == Step.ASK_FOR_ORDER_ID
              and extract_order_id(message) is not None):
            # An exact numeric reply is deterministic; no LLM needed.
            response = route(state, message, resolved_intent="UNKNOWN")
        else:
            # Classify first: this also recognizes interruptions such as
            # cancellation while the workflow awaits an order number.
            try:
                result = self.classifier.classify(message)
            except Exception:
                # External model/network errors must not advance state.
                response = (
                    "No pude interpretar la solicitud en este momento. "
                    "¿Puedes reformularla o intentarlo de nuevo?"
                )
            else:
                if result.needs_clarification:
                    response = result.clarification_question or "¿Puedes aclarar tu solicitud?"
                else:
                    response = route(state, message, resolved_intent=result.intent.value)

        self.repository.save(conversation_id, state)
        return response, state
