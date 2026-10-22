"""Conservative extraction of a product mentioned by a store employee.

No LLM and no product catalog lookup. Unknown/ambiguous inputs stay unresolved.
"""
from dataclasses import dataclass
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
