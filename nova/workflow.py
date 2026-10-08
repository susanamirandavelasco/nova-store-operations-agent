"""Deterministic workflow prototype. No LLM or external services yet."""

from dataclasses import dataclass
from enum import Enum
import re


class Status(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"


class Step(str, Enum):
    UNDERSTAND = "UNDERSTAND"
    ASK_FOR_ORDER_ID = "ASK_FOR_ORDER_ID"
    GET_ORDER = "GET_ORDER"
    NONE = "NONE"


@dataclass
class NovaState:
    intent: str = "UNKNOWN"
    order_id: str | None = None
    next_step: Step = Step.UNDERSTAND
    status: Status = Status.ACTIVE


def classify_message(message: str) -> str:
    """Deliberately simple classifier for learning state transitions."""
    text = message.casefold()
    if re.search(r"\b(cancelar|cancela|cancelo)\b", text):
        return "CANCEL"
    if re.search(r"\b(continuar|retomar|retomemos)\b", text):
        return "RESUME"
    if re.search(r"\b(garantía|garantías|garantia|garantias)\b", text):
        return "POLICY_QUESTION"
    if re.search(r"\b(devolver|devolución|devolucion)\b", text):
        return "RETURN_REQUEST"
    return "UNKNOWN"


def extract_order_id(message: str) -> str | None:
    value = message.strip()
    return value if re.fullmatch(r"[0-9]+", value) else None


def route(state: NovaState, message: str) -> str:
    """Mutate one conversation's state and return a simulated reply."""
    intent = classify_message(message)

    if intent == "CANCEL":
        if state.status == Status.CANCELLED:
            return "No hay una devolución pendiente."
        state.status = Status.CANCELLED
        state.next_step = Step.NONE
        state.order_id = None
        state.intent = "UNKNOWN"
        return "Cancelé la consulta de devolución pendiente."

    if intent == "RESUME" and state.status == Status.SUSPENDED:
        state.status = Status.ACTIVE
        return "Retomamos la devolución. ¿Cuál es el número de orden?"

    if intent == "POLICY_QUESTION":
        if state.status == Status.ACTIVE and state.intent == "RETURN_REQUEST":
            state.status = Status.SUSPENDED
        return (
            "La consulta de garantías todavía no está implementada. "
            "Si había una devolución activa, quedó suspendida."
        )

    if intent == "RETURN_REQUEST":
        state.intent = intent
        state.order_id = None
        state.status = Status.ACTIVE
        state.next_step = Step.ASK_FOR_ORDER_ID
        return "¿Cuál es el número de orden?"

    if state.status == Status.ACTIVE and state.next_step == Step.ASK_FOR_ORDER_ID:
        order_id = extract_order_id(message)
        if order_id is None:
            return "Necesito un número de orden válido (solo dígitos)."
        state.order_id = order_id
        state.next_step = Step.GET_ORDER
        return f"El siguiente paso será consultar la orden {order_id} (simulado)."

    if state.status == Status.SUSPENDED:
        return "La devolución está suspendida. Di 'retomar' para continuar."

    if state.next_step == Step.GET_ORDER and state.status == Status.ACTIVE:
        return "La consulta de órdenes todavía no está implementada."

    return "¿Quieres consultar una política o evaluar una devolución?"


class InMemoryConversationStore:
    """Temporary storage; resets when the process stops."""

    def __init__(self) -> None:
        self.sessions: dict[str, NovaState] = {}

    def handle_message(self, conversation_id: str, message: str) -> tuple[str, NovaState]:
        if not conversation_id.strip():
            raise ValueError("conversation_id cannot be blank")
        state = self.sessions.setdefault(conversation_id, NovaState())
        return route(state, message), state
