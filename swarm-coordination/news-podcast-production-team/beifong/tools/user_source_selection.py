from agno.assistant import Assistant
from dotenv import load_dotenv
from typing import List

load_dotenv()

def user_source_selection_run(
    assistant: Assistant,
    selected_sources: List[int],
) -> str:
    """
    User Source Selection that takes the selected sources indices as input and updates the final confirmed sources.
    Args:
        assistant: The assistant instance
        selected_sources: The selected sources indices
    Returns:
        Response status
    """
    from services.internal_session_service import SessionService
    context_id = assistant.context_id
    session = SessionService.get_session(context_id)
    session_state = session["state"]
    for i, src in enumerate(session_state["search_results"]):
        if (i+1) in selected_sources:
            src["confirmed"] = True
        else:
            src["confirmed"] = False
    SessionService.save_session(context_id, session_state)
    return f"Updated selected sources to {selected_sources}."
