"""Run with python -m nova; opt into fictional return demo with --demo."""
import argparse

from nova.orders import FakeOrderRepository
from nova.repository import SQLiteStateRepository
from nova.return_evaluator import evaluate_return
from nova.service import WorkflowService


def build_service(*, demo: bool = False, db_path: str = "nova_state.sqlite3") -> WorkflowService:
    """Compose adapters at the application boundary; no external services."""
    repository = SQLiteStateRepository(db_path)
    if demo:
        return WorkflowService(
            repository,
            order_repository=FakeOrderRepository(),
            return_evaluator=evaluate_return,
        )
    return WorkflowService(repository)


def main() -> None:
    parser = argparse.ArgumentParser(description="Nova — Store Operations Agent")
    parser.add_argument(
        "--demo", action="store_true",
        help="Enable fictional order verification and return recommendations",
    )
    parser.add_argument(
        "--conversation", default=None,
        help="Conversation ID (reuse to resume persisted state)",
    )
    args = parser.parse_args()
    conversation_id = args.conversation or ("demo_returns_07" if args.demo else "demo_001")
    service = build_service(demo=args.demo)
    print("Nova prototype — SQLite persistence enabled; type 'salir' to exit")
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
