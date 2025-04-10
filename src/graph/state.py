from langgraph.graph import StateGraph
from langchain_core.messages import BaseMessage
from typing import List
from typing import TypedDict
from src.graph.utils.chains import RouterResponseLiteral

class State(TypedDict):
    messages: List[BaseMessage]
    summary: str
    next_node: RouterResponseLiteral | None
    memory_context: str
