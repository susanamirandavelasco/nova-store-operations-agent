"""Run with python -m nova; opt into fictional return demo with --demo."""
import argparse

from nova.orders import FakeOrderRepository
from nova.repository import SQLiteStateRepository
from nova.return_evaluator import evaluate_return
from nova.service import WorkflowService


def build_service(*, demo: bool = False, llm_condition: bool = False, db_path: str = "nova_state.sqlite3") -> WorkflowService:
    """Compose adapters at the application boundary; no external services."""
    if llm_condition and not demo:
        raise ValueError("--llm-condition requires --demo")
    repository = SQLiteStateRepository(db_path)
    if demo:
        from nova.openai_condition_extractor import OpenAIConditionExtractor
        return WorkflowService(
            repository,
            order_repository=FakeOrderRepository(),
            return_evaluator=evaluate_return,
            condition_extractor=OpenAIConditionExtractor() if llm_condition else None,
        )
    return WorkflowService(repository)


def main() -> None:
    parser = argparse.ArgumentParser(description="Nova — Store Operations Agent")
    parser.add_argument(
        "--demo", action="store_true",
        help="Enable fictional order verification and return recommendations",
    )
    parser.add_argument(
        "--llm-condition", action="store_true",
        help="Use OpenAI to interpret product condition (requires --demo and OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--conversation", default=None,
        help="Conversation ID (reuse to resume persisted state)",
    )
    args = parser.parse_args()
    if args.llm_condition and not args.demo:
        parser.error("--llm-condition requires --demo")
    conversation_id = args.conversation or ("demo_returns_07" if args.demo else "demo_001")
    service = build_service(demo=args.demo, llm_condition=args.llm_condition)
    print("Nova prototype — SQLite persistence enabled; type 'salir' to exit")
    if args.llm_condition:
        print("Condition interpretation: OpenAI (API usage may incur charges)")
    if args.demo:
        print("Fictional return demo — no real orders, authorization, or execution")
        print("Example: order 83921 (audífonos) or 65042 (televisor)")
    print(f"Conversation: {conversation_id}")
    while True:
        try:
            message = input("\nEmpleado: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if message.strip().casefold() == "salir":
            break
        response, state = service.handle_message(conversation_id, message)
        print(f"Nova: {response}")
        print(f"STATE: {state.next_step.value}")


if __name__ == "__main__":
    main()
