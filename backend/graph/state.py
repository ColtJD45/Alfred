# alfred/backend/graph/state.py

from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    user_id: str
    session_id: str