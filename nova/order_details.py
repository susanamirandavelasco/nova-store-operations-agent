"""Conservative extraction of a product mentioned by a store employee.

No LLM and no product catalog lookup. Unknown/ambiguous inputs stay unresolved.
"""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ProductExtraction:
    product: str | None
    needs_clarification: bool


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
    # Negation and multiple products require clarification; never guess.
    if len(matches) != 1 or re.search(r"\b(no|ni|tampoco)\b", text):
        return ProductExtraction(None, True)
    return ProductExtraction(next(iter(matches)), False)
