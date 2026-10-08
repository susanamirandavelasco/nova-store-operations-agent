"""Run with: python -m nova. Conversation state persists in local SQLite."""
from nova.repository import SQLiteStateRepository
from nova.service import WorkflowService


def main() -> None:
    service = WorkflowService(SQLiteStateRepository())
    print("Nova prototype — SQLite persistence enabled; type 'salir' to exit")
    print("Conversation: demo_001")
    while True:
        try:
            message = input("\nEmpleado: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if message.strip().casefold() == "salir":
            break
        response, state = service.handle_message("demo_001", message)
        print(f"Nova: {response}")
        print(f"STATE: {state}")


if __name__ == "__main__":
    main()
