"""Manual lexical-vs-semantic experiment. Uses the optional OpenAI embeddings API.

Run: python -m nova.compare_policy_retrieval
Do not use this as a production accuracy benchmark.
"""
from nova.policy_retrieval import PolicyRetriever
from nova.semantic_policy_retrieval import OpenAIEmbedder, SemanticPolicyRetriever, cosine_similarity

CASES = (
    ("¿Cuál es el plazo de devolución?", "POL-RET-001#plazo"),
    ("¿Puedo regresar algo que compré hace tres semanas?", "POL-RET-001#plazo"),
    ("¿Qué sucede si abrí la caja?", "POL-RET-001#estado"),
    ("¿A qué hora cierra la tienda?", None),
    ("¿Cuál es la política de horario de sucursal?", None),
)


def main() -> None:
    lexical = PolicyRetriever()
    # Two passages + five questions: seven short texts embedded once each.
    # This baseline uses an uncalibrated threshold and must be evaluated.
    semantic = SemanticPolicyRetriever(OpenAIEmbedder())
    lexical_correct = 0
    semantic_correct = 0
    # Embed all questions once to inspect raw scores without extra API calls per policy.\n    query_vectors = semantic.embedder.embed([question for question, _ in CASES])\n    for (question, expected), query_vector in zip(CASES, query_vectors):
        left = lexical.answer(question)
        right = semantic.answer(question)
        lexical_correct += left.source_id == expected
        semantic_correct += right.source_id == expected
        print(f"Pregunta: {question}")
        print(f"  Esperada: {expected or 'ABSTENCIÓN'}")
        print(f"  Léxica:   {left.source_id or 'ABSTENCIÓN/ACLARACIÓN'}")
        print(f"  Semántica:{right.source_id or 'ABSTENCIÓN/ACLARACIÓN'}")\n        scores = sorted(\n            ((cosine_similarity(query_vector, vector), passage.source_id)\n             for passage, vector in zip(semantic.passages, semantic.vectors)),\n            reverse=True,\n        )\n        print("  Scores:   " + ", ".join(f"{source}={score:.4f}" for score, source in scores))\n        if right.source_id is None:\n            print(f"  Motivo:   {right.text}")
        print()
    print(f"Coincidencias con etiquetas (léxica): {lexical_correct}/{len(CASES)}")
    print(f"Coincidencias con etiquetas (semántica): {semantic_correct}/{len(CASES)}")
    print("Advertencia: 5 casos son insuficientes para medir calidad real;")
    print("una abstención y una aclaración se agrupan en este resumen.")


if __name__ == "__main__":
    main()
