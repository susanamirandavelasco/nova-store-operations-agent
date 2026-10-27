"""Optional LLM interpretation of product condition; policy remains deterministic."""
import json
import re

from nova.condition_extraction import ConditionExtraction, _normalize
from nova.product_condition import ProductCondition


class OpenAIConditionExtractor:
    """Structured-output adapter. No API call occurs at construction."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def extract(self, message: str) -> ConditionExtraction:
        if not message.strip():
            return ConditionExtraction(None, True)

        # Explicit hedging, contradiction or negation must not become certainty.
        text = _normalize(message)
        if re.search(
            r"\b(creo|quizas|quiza|tal vez|no se|no estoy seguro|no estoy segura|"
            r"parece|puede que|me parece|no recuerdo)\b", text
        ):
            return ConditionExtraction(None, True)

        try:
            from openai import OpenAI

            response = OpenAI().chat.completions.create(
                model=self.model,
                temperature=0,
                messages=[
                    {"role": "system", "content": (
                        "Interpreta SOLO la condición de un producto para un piloto ficticio. "
                        "Devuelve SEALED únicamente si hay evidencia explícita de empaque "
                        "sellado, intacto o sin abrir. 'Empaque original' por sí solo NO "
                        "demuestra que esté sellado. OPENED significa que se abrió la caja "
                        "o empaque; DAMAGED que el producto está roto o dañado. "
                        "UNKNOWN es una declaración explícita de desconocimiento. "
                        "Si hay duda, negación, contradicción, varias condiciones o "
                        "evidencia insuficiente, condition=null y needs_clarification=true. "
                        "Nunca evalúes elegibilidad ni autorices devoluciones."
                    )},
                    {"role": "user", "content": message},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "condition_extraction",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "condition": {
                                    "type": ["string", "null"],
                                    "enum": ["SEALED", "OPENED", "DAMAGED", "UNKNOWN", None],
                                },
                                "needs_clarification": {"type": "boolean"},
                            },
                            "required": ["condition", "needs_clarification"],
                            "additionalProperties": False,
                        },
                    },
                },
            )
            data = json.loads(response.choices[0].message.content or "")
            if not isinstance(data, dict) or set(data) != {"condition", "needs_clarification"}:
                raise ValueError("Unexpected response shape")
            if type(data["needs_clarification"]) is not bool:
                raise ValueError("Expected boolean")
            value = data["condition"]
            if value is not None and (not isinstance(value, str) or value not in ProductCondition.__members__):
                raise ValueError("Unknown condition")
            if data["needs_clarification"] or value is None:
                return ConditionExtraction(None, True)
            return ConditionExtraction(ProductCondition(value), False)
        except Exception:
            # API errors, refusals or malformed responses must not advance workflow.
            return ConditionExtraction(None, True)
