"""Conservative, source-attributed retrieval over fictional NovaRetail policies.

This is a lexical baseline, NOT semantic search or a complete RAG pipeline.
"""
from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class PolicyPassage:
    source_id: str
    title: str
    text: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class PolicyAnswer:
    text: str
    source_id: str | None = None
    title: str | None = None


POLICIES = (
    PolicyPassage(
        source_id="POL-RET-001#plazo",
        title="Política ficticia de devoluciones — plazo",
        text="Las devoluciones ordinarias se solicitan dentro de los 30 días naturales posteriores a la compra.",
        keywords=("plazo", "dias", "tiempo", "cuanto", "devolver", "devolucion", "devoluciones"),
    ),
    PolicyPassage(
        source_id="POL-RET-001#estado",
        title="Política ficticia de devoluciones — estado del producto",
        text="El estado del producto debe verificarse. Un artículo abierto puede requerir revisión humana; no se garantiza su aceptación.",
        keywords=("abierto", "abrir", "estado", "empaque", "caja", "sellado", "producto"),
    ),
)


def _tokens(value: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    plain = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return set(re.findall(r"[a-z0-9]+", plain))


class PolicyRetriever:
    """Keyword baseline with an explicit abstention when evidence is weak."""

    def __init__(self, passages: tuple[PolicyPassage, ...] = POLICIES) -> None:
        self.passages = passages

    def answer(self, question: str) -> PolicyAnswer:
        words = _tokens(question)
        if not words:
            return PolicyAnswer("No encontré información suficiente en las políticas disponibles.")
        matches = []
        for passage in self.passages:
            hits = words.intersection(passage.keywords)
            if hits:
                matches.append((len(hits), passage))
        if not matches:
            return PolicyAnswer("No encontré información suficiente en las políticas disponibles.")
        matches.sort(key=lambda item: item[0], reverse=True)
        if len(matches) > 1 and matches[0][0] == matches[1][0]:
            return PolicyAnswer("La pregunta puede referirse a varias políticas. ¿Puedes precisar si consultas el plazo o el estado del producto?")
        selected = matches[0][1]
        return PolicyAnswer(selected.text, selected.source_id, selected.title)
