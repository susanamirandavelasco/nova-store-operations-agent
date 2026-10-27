"""Application orchestration: load state, interpret message, route, persist."""
import re
from datetime import date
from collections.abc import Callable
from typing import Protocol

from nova.condition_extraction import ConditionExtractor, RuleBasedConditionExtractor
from nova.intent_classifier import IntentResult
from nova.order_details import ProductExtractor, RuleBasedProductExtractor
from nova.orders import OrderRepository, VerificationStatus, verify_order
from nova.repository import StateRepository
from nova.product_condition import ProductCondition
from nova.return_evaluator import evaluate_return
from nova.eligibility_engine import CombinedEligibilityResult
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
        product_extractor: ProductExtractor | None = None,
        return_evaluator: Callable[..., CombinedEligibilityResult] | None = None,
        evaluation_date: Callable[[], date] | None = None,
        condition_extractor: ConditionExtractor | None = None,
    ) -> None:
        self.repository = repository
        self.classifier = classifier
        self.order_repository = order_repository
        self.product_extractor = product_extractor or RuleBasedProductExtractor()
        self.return_evaluator = return_evaluator
        self.evaluation_date = evaluation_date or date.today
        self.condition_extractor = condition_extractor or RuleBasedConditionExtractor()

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

            if state.next_step == Step.ASK_FOR_PRODUCT_CONDITION and self.return_evaluator is not None:
                try:
                    extraction = self.condition_extractor.extract(message)
                except Exception:
                    return "No pude interpretar la condición. ¿Puedes aclararla?"
                if extraction.needs_clarification or extraction.condition is None:
                    return ("No pude confirmar una única condición del producto. "
                            "¿Está sellado, abierto o dañado? Si no lo sabes, responde UNKNOWN.")
                condition = extraction.condition
                order = self.order_repository.get(state.order_id) if state.order_id else None
                if order is None:
                    return "No encontré la orden corroborada. Solicita revisión humana."
                result = self.return_evaluator(
                    order, self.evaluation_date(), condition=condition,
                    category=order.category,
                )
                state.next_step = Step.GET_ORDER
                reasons = "; ".join(
                    f"{item.rule_name}: {item.result.reason}"
                    for item in result.evaluations
                )
                return (f"Recomendación: {result.status.value}. {reasons}. "
                        "No autoriza ni ejecuta la devolución.")

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
                try:
                    extraction = self.product_extractor.extract(detail)
                except Exception:
                    return "No pude interpretar el producto. ¿Puedes aclararlo?"
                if (extraction.needs_clarification
                        or not extraction.product
                        or extraction.product not in {"audífonos", "televisor"}):
                    return (
                        "No pude identificar un único producto con seguridad. "
                        "¿Puedes verificar cuál fue el producto comprado y confirmármelo?"
                    )
                result = verify_order(
                    self.order_repository, state.pending_order_id,
                    product=extraction.product,
                )
                if result.status == VerificationStatus.MATCH:
                    state.order_id = state.pending_order_id
                    state.pending_order_id = None
                    state.next_step = (Step.ASK_FOR_PRODUCT_CONDITION
                                       if self.return_evaluator is not None else Step.GET_ORDER)
                    if self.return_evaluator is not None:
                        return (f"Los datos coinciden con la orden {state.order_id}. "
                                "¿Cuál es la condición del producto? "
                                "Responde SEALED, OPENED, DAMAGED o UNKNOWN.")
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
