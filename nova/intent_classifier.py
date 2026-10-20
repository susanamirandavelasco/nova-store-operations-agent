"""Structured intent classification; the workflow remains the decision-maker."""
from dataclasses import dataclass
from enum import Enum
import json
from typing import Protocol


class Intent(str, Enum):
    RETURN_REQUEST = "RETURN_REQUEST"
    POLICY_QUESTION = "POLICY_QUESTION"
    CANCEL = "CANCEL"
    RESUME = "RESUME"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class IntentResult:
    intent: Intent
    needs_clarification: bool
    clarification_question: str | None = None

    def __post_init__(self) -> None:
        if self.needs_clarification and not self.clarification_question:
            raise ValueError("A clarification question is required")
        if not self.needs_clarification and self.clarification_question is not None:
            raise ValueError("Do not ask a clarification question for a resolved intent")


class StructuredIntentModel(Protocol):
    def classify_json(self, message: str) -> str:
        """Return a JSON string matching the intent classification contract."""


class IntentClassifier:
    def __init__(self, model: StructuredIntentModel) -> None:
        self.model = model

    def classify(self, message: str) -> IntentResult:
        if not message.strip():
            return IntentResult(Intent.UNKNOWN, True, "¿En qué puedo ayudarte?")
        try:
            data = json.loads(self.model.classify_json(message))
            if not isinstance(data, dict):
                raise ValueError("Expected JSON object")
            result = IntentResult(
                intent=Intent(data["intent"]),
                needs_clarification=data["needs_clarification"],
                clarification_question=data.get("clarification_question"),
            )
            if type(result.needs_clarification) is not bool:
                raise ValueError("needs_clarification must be boolean")
            if result.intent == Intent.UNKNOWN and not result.needs_clarification:
                raise ValueError("Unknown intent must request clarification")
            return result
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            return IntentResult(
                Intent.UNKNOWN, True,
                "No pude identificar con claridad tu solicitud. ¿Quieres consultar una política o evaluar una devolución?",
            )


class OpenAIIntentModel:
    """Real LLM adapter. Requires 'openai' package and OPENAI_API_KEY."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def classify_json(self, message: str) -> str:
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": (
                    "Clasifica la intención de un empleado de tienda. "
                    "Intenciones: RETURN_REQUEST, POLICY_QUESTION, CANCEL, RESUME, UNKNOWN. "
                    "Si hay ambigüedad, responde UNKNOWN, needs_clarification=true "
                    "y formula una pregunta breve en español. "
                    "No inventes datos ni confirmes números de orden. "
                    "No confundas menciones negadas ('no quiero cancelar') con CANCEL. "
                    "Solo clasifica: nunca ejecutes acciones."
                )},
                {"role": "user", "content": message},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "intent_classification",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "intent": {"type": "string", "enum": [i.value for i in Intent]},
                            "needs_clarification": {"type": "boolean"},
                            "clarification_question": {"type": ["string", "null"]},
                        },
                        "required": ["intent", "needs_clarification", "clarification_question"],
                        "additionalProperties": False,
                    },
                },
            },
        )
        return response.choices[0].message.content or ""
