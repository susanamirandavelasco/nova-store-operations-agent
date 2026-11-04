"""Small, manually labeled policy-retrieval evaluation.

Run: python -m nova.evaluate_policy_retrieval
Requires OPENAI_API_KEY and the optional openai package.
This is a development dataset, not a held-out production benchmark.
"""
from dataclasses import dataclass

from nova.policy_retrieval import POLICIES, PolicyRetriever
from nova.semantic_policy_retrieval import OpenAIEmbedder, cosine_similarity

PLAZO = "POL-RET-001#plazo"
ESTADO = "POL-RET-001#estado"


@dataclass(frozen=True)
class Case:
    question: str
    expected: str | None


CASES = (
    Case("¿Cuál es el plazo de devolución?", PLAZO),
    Case("¿Cuántos días tengo para devolver un artículo?", PLAZO),
    Case("¿Puedo regresar algo que compré hace tres semanas?", PLAZO),
    Case("Compré algo hace 20 días, ¿todavía puedo regresarlo?", PLAZO),
    Case("¿Hay un límite de tiempo para hacer una devolución?", PLAZO),
    Case("¿El periodo para devolver es de un mes?", PLAZO),
    Case("¿Cuánto tiempo después de comprar puedo solicitar una devolución?", PLAZO),
    Case("¿Qué pasa si quiero devolver un artículo después de 40 días?", PLAZO),
    Case("¿El conteo de días es natural o hábil?", PLAZO),
    Case("¿Cuándo vence el periodo de devolución?", PLAZO),
    Case("¿Qué sucede si abrí la caja?", ESTADO),
    Case("¿Se puede devolver un producto abierto?", ESTADO),
    Case("Quité el empaque original, ¿qué procede?", ESTADO),
    Case("¿Un artículo usado necesita revisión?", ESTADO),
    Case("¿Es seguro que aceptarán algo que ya destapé?", ESTADO),
    Case("¿Qué se revisa sobre el estado del producto?", ESTADO),
    Case("¿Quién verifica si el artículo fue abierto?", ESTADO),
    Case("Si rompí el sello, ¿la devolución está garantizada?", ESTADO),
    Case("¿A qué hora cierra la tienda?", None),
    Case("¿Cuál es el horario de atención de la sucursal?", None),
    Case("¿Cuánto cuesta el envío?", None),
    Case("¿Puedo pagar a meses sin intereses?", None),
    Case("¿Dónde está mi pedido?", None),
    Case("¿Cómo cambio mi contraseña?", None),
    Case("¿Cuánto tarda un reembolso en llegar a mi tarjeta?", None),
)

THRESHOLDS = (0.30, 0.33, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.75)
MARGIN = 0.03


def choose(scores: list[float], threshold: float, margin: float = MARGIN) -> str | None:
    """Mirror SemanticPolicyRetriever's abstention/tie rules."""
    if not scores:
        return None
    ordered = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    best = ordered[0]
    if scores[best] < threshold:
        return None
    if len(ordered) > 1 and scores[best] - scores[ordered[1]] < margin:
        return None
    return POLICIES[best].source_id


def metrics(predictions: list[str | None]) -> dict[str, int]:
    """Separate unsafe wrong-source answers from conservative abstentions."""
    result = {"correct": 0, "wrong_source": 0, "missed": 0, "false_positive": 0, "correct_abstain": 0}
    for case, predicted in zip(CASES, predictions):
        if case.expected is None:
            result["correct_abstain" if predicted is None else "false_positive"] += 1
        elif predicted == case.expected:
            result["correct"] += 1
        elif predicted is None:
            result["missed"] += 1
        else:
            result["wrong_source"] += 1
    return result


def main() -> None:
    lexical = PolicyRetriever()
    lexical_predictions = [lexical.answer(case.question).source_id for case in CASES]
    print(f"Casos: {len(CASES)} (18 con fuente, 7 fuera de alcance)")
    print("Léxico:", metrics(lexical_predictions))
    embedder = OpenAIEmbedder()
    # Exactly one batched API request for the passages, one for the questions.
    passage_vectors = embedder.embed([p.text for p in POLICIES])
    question_vectors = embedder.embed([c.question for c in CASES])
    score_rows = [
        [cosine_similarity(query, passage) for passage in passage_vectors]
        for query in question_vectors
    ]
    print("\nUmbral | Correctas | Fuente errónea | Sin respuesta | Falsos positivos | Abstenciones correctas")
    for threshold in THRESHOLDS:
        result = metrics([choose(scores, threshold) for scores in score_rows])
        print(
            f"{threshold:>6.2f} | {result['correct']:>9} | {result['wrong_source']:>13} |"
            f" {result['missed']:>13} | {result['false_positive']:>15} |"
            f" {result['correct_abstain']:>20}"
        )
    print("\nDetalle (mejor candidato y score, sin aplicar umbral):")
    for case, scores in zip(CASES, score_rows):
        best = max(range(len(scores)), key=lambda i: scores[i])
        print(
            f"{POLICIES[best].source_id:>18} {scores[best]:.4f} "
            f"esperada={case.expected or 'NINGUNA'} | {case.question}"
        )
    print("\nNOTA: el empate se agrupa como abstención; revisar manualmente errores.")
    print("No seleccionar un umbral final usando únicamente estos mismos 25 casos.")


if __name__ == "__main__":
    main()
