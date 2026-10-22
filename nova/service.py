"""Application orchestration: load state, interpret message, route, persist."""
import re
from typing import Protocol

from nova.intent_classifier import IntentResult
from nova.order_details import extract_product
from nova.orders import OrderRepository, VerificationStatus, verify_order
from nova.repository import StateRepository
from nova.workflow import NovaState, Step, Status, extract_order_id, route


class IntentInterpreter(Protocol):
    def classify(self, message: str) -> IntentResult: ...


def candidate_order_id(message: str) -> str | None:
    """Only two narrowly defined formats in this increment; no guesswork."""
    exact = extract_order_id(message)
    if exact is not None:
        return exact
    match = re.fullmatch(
        r"\s*creo que (?:era |es )?(?:la |el )?(?:orden )?([0-9]+)\s*",
        message, re.IGNORECASE,
    )
    return match.group(1) if match else None


class WorkflowService:
    def __init__(
        self, repository: StateRepository,
        classifier: IntentInterpreter | None = None,
        order_repository: OrderRepository | None = None,
    ) -> None:
        self.repository = repository
        self.classifier = classifier
        self.order_repository = order_repository

    def handle_message(self, conversation_id: str, message: str) -> tuple[str, NovaState]:
        if not conversation_id.strip():
            raise ValueError("conversation_id cannot be blank")

        state = self.repository.load(conversation_id)
        if state is None:
            state = NovaState()

        if self.order_repository is not None:
            response = self._handle_with_orders(state, message)
        elif self.classifier is None:
            response = route(state, message)
        elif (state.status == Status.ACTIVE
              and state.next_step == Step.ASK_FOR_ORDER_ID
              and extract_order_id(message) is not None):
            response = route(state, message, resolved_intent="UNKNOWN")
        else:
            response = self._classify_and_route(state, message)

        self.repository.save(conversation_id, state)
        return response, state

    def _classify_and_route(self, state: NovaState, message: str) -> str:
        try:
            result = self.classifier.classify(message)
        except Exception:
            return (
                "No pude interpretar la solicitud en este momento. "
                "¿Puedes reformularla o intentarlo de nuevo?"
            )
        if result.needs_clarification:
            return result.clarification_question or "¿Puedes aclarar tu solicitud?"
        return route(state, message, resolved_intent=result.intent.value)

    def _handle_with_orders(self, state: NovaState, message: str) -> str:
        """Candidate -> corroboration -> confirmed order; never skip verification."""
        if state.status == Status.ACTIVE and state.intent == "RETURN_REQUEST":
            # Explicit commands are handled before consuming order data.
            # Other interruption phrasings require the optional classifier.
            if re.fullmatch(r"\s*(cancelar|cancela|mejor cancela)\s*", message, re.I):
                return route(state, message, resolved_intent="CANCEL")
            if re.fullmatch(r"\s*(retomar|continuar)\s*", message, re.I):
                return route(state, message, resolved_intent="RESUME")

            if state.next_step == Step.ASK_FOR_ORDER_ID:
                candidate = candidate_order_id(message)
                if candidate is not None:
                    state.pending_order_id = candidate
                    state.order_id = None
                    state.next_step = Step.ASK_FOR_ORDER_DETAILS
                    return (
                        f"Tengo {candidate} como referencia provisional. "
                        "¿Qué producto se compró? Lo corroboraré con el registro."
                    )

            if state.next_step == Step.ASK_FOR_ORDER_DETAILS:
                detail = message.strip()
                if not detail:
                    return "Indica el producto de la compra para corroborar la referencia."
                if self.classifier is not None:
                    # Preserve interruptions, even while awaiting details.
                    try:
                        classification = self.classifier.classify(message)
                    except Exception:
                        return "No pude interpretar la solicitud. Intenta de nuevo."
                    if classification.needs_clarification:
                        return classification.clarification_question or "¿Puedes aclarar tu solicitud?"
                    if classification.intent.value in {"CANCEL", "POLICY_QUESTION", "RESUME", "RETURN_REQUEST"}:
                        return route(state, message, resolved_intent=classification.intent.value)
                extraction = extract_product(detail)
                if extraction.needs_clarification:
                    return (
                        "No pude identificar un único producto con seguridad. "
                        "¿Fue un televisor o unos audífonos?"
                    )
                result = verify_order(
                    self.order_repository, state.pending_order_id,
                    product=extraction.product,
                )
                if result.status == VerificationStatus.MATCH:
                    state.order_id = state.pending_order_id
                    state.pending_order_id = None
                    state.next_step = Step.GET_ORDER
                    return (
                        f"Los datos coinciden con la orden {state.order_id}. "
                        "La elegibilidad para devolución aún no está evaluada."
                    )
                if result.status == VerificationStatus.NOT_FOUND:
                    return (
                        "No encontré esa referencia. Sigue provisional; "
                        "verifica el número de orden o cancela la consulta."
                    )
                return (
                    "Los datos no coinciden con el registro. La referencia sigue "
                    "provisional. Revisa el producto o cancela la consulta."
                )

        if self.classifier is not None:
            return self._classify_and_route(state, message)
        return route(state, message)
