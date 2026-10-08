"""Run with: python -m nova"""

from nova.workflow import InMemoryConversationStore


def main() -> None:
    store = InMemoryConversationStore()
    print("Nova prototype — type 'salir' to exit")
    while True:
        try:
            message = input("\nEmpleado: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if message.strip().casefold() == "salir":
            break
        response, state = store.handle_message("demo_001", message)
        print(f"Nova: {response}")
        print(f"STATE: {state}")


if __name__ == "__main__":
    main()
