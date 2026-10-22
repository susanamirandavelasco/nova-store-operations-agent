"""Conservative extraction of a product mentioned by a store employee.

Optional LLM adapter; no catalog lookup. Unknown/ambiguous inputs stay unresolved.
"""
from dataclasses import dataclass
import json
import re
from typing import Protocol


@dataclass(frozen=True)
class ProductExtraction:
    product: str | None
    needs_clarification: bool


class ProductExtractor(Protocol):
    """Contract for deterministic or future LLM-backed implementations."""

    def extract(self, message: str) -> ProductExtraction: ...


class RuleBasedProductExtractor:
    def extract(self, message: str) -> ProductExtraction:
        return extract_product(message)


# Deliberately small vocabulary for the fictional pilot. Do not infer products
# from order data: that would make verification circular.
PRODUCT_ALIASES = {
    "audífonos": ("audífonos", "audifonos"),
    "televisor": ("televisor", "televisión", "television"),
}


def extract_product(message: str) -> ProductExtraction:
    text = message.casefold()
    if not text.strip():
        return ProductExtraction(None, True)

    matches = {
        canonical
        for canonical, aliases in PRODUCT_ALIASES.items()
        if any(
            alias.strip() and re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", text)
            for alias in aliases
        )
    }
    # Explicit uncertainty blocks confirmation even if one product is recognized.
    uncertain = any(phrase in text for phrase in (
        "creo que", "me parece que", "no estoy seguro", "no estoy segura",
        "no recuerdo", "tal vez", "quizá", "quizas", "puede que",
    ))
    # Negation, uncertainty and multiple products require clarification; never guess.
    if len(matches) != 1 or uncertain or re.search(r"\b(no|ni|tampoco)\b", text):
        return ProductExtraction(None, True)
    return ProductExtraction(next(iter(matches)), False)


class OpenAIProductExtractor:
    """Optional structured-output adapter. No API call occurs at construction."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def extract(self, message: str) -> ProductExtraction:
        if not message.strip():
            return ProductExtraction(None, True)
        try:
            from openai import OpenAI

            response = OpenAI().chat.completions.create(
                model=self.model,
                temperature=0,
                messages=[
                    {"role": "system", "content": (
                        "Extrae el producto mencionado por un empleado de tienda. "
                        "Solo puedes usar los productos canónicos audífonos y televisor. "
                        "Auriculares corresponde a audífonos; televisión corresponde a televisor. "
                        "Si hay negación, duda, múltiples productos o información insuficiente, "
                        "needs_clarification debe ser true. "
                        "Nunca deduzcas el producto a partir del número de orden. "
                        "No confirmes órdenes ni determines elegibilidad."
                    )},
                    {"role": "user", "content": message},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "product_extraction",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "product": {
                                    "type": ["string", "null"],
                                    "enum": ["audífonos", "televisor", None],
                                },
                                "needs_clarification": {"type": "boolean"},
                            },
                            "required": ["product", "needs_clarification"],
                            "additionalProperties": False,
                        },
                    },
                },
            )
            data = json.loads(response.choices[0].message.content or "")
            if not isinstance(data, dict):
                raise ValueError("Expected object")
            if set(data) != {"product", "needs_clarification"}:
                raise ValueError("Unexpected fields")
            if type(data["needs_clarification"]) is not bool:
                raise ValueError("Expected boolean")
            if data["product"] not in (None, "audífonos", "televisor"):
                raise ValueError("Unknown product")
            if data["product"] is None and not data["needs_clarification"]:
                raise ValueError("Missing product requires clarification")
            # Additional deterministic guard: obvious uncertainty must not be
            # overridden by a model claiming high confidence.
            if extract_product(message).needs_clarification and any(
                phrase in message.casefold()
                for phrase in (
                    "creo que", "me parece que", "no estoy seguro",
                    "no estoy segura", "no recuerdo", "tal vez",
                    "quizá", "quizas", "puede que",
                )
            ):
                return ProductExtraction(None, True)
            return ProductExtraction(data["product"], data["needs_clarification"])
        except Exception:
            # Invalid JSON, missing package, model refusal, API failure:
            # never allow a provisional order to advance.
            return ProductExtraction(None, True)
