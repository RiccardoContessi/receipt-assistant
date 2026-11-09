from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State shared by the graph nodes: the conversation so far."""
    messages: Annotated[list[AnyMessage], add_messages]