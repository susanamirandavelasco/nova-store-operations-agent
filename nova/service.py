"""Application orchestration: load state, route message, persist state."""
from nova.repository import StateRepository
from nova.workflow import NovaState, route


class WorkflowService:
    def __init__(self, repository: StateRepository) -> None:
        self.repository = repository

    def handle_message(self, conversation_id: str, message: str) -> tuple[str, NovaState]:
        if not conversation_id.strip():
            raise ValueError("conversation_id cannot be blank")
        state = self.repository.load(conversation_id)
        if state is None:
            state = NovaState()
        response = route(state, message)
        self.repository.save(conversation_id, state)
        return response, state
