from src.graph.state import State
from langgraph.graph import StateGraph, START, END
from src.graph.nodes import router_node, fallback_node, memory_injection_node, create_task_node, get_current_issues, memory_update_node, get_user_issues_node
from src.graph.edges import select_route
import asyncio


def create_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node("memory_update_node", memory_update_node)
    graph_builder.add_node("memory_injection_node", memory_injection_node)
    graph_builder.add_node("router_node", router_node)
    graph_builder.add_node("fallback_node", fallback_node)
    graph_builder.add_node("create_task_node", create_task_node)
    graph_builder.add_node("get_current_issues_node", get_current_issues)
    graph_builder.add_node("get_user_issues_node", get_user_issues_node)


    graph_builder.add_edge(START, "memory_update_node")
    graph_builder.add_edge("memory_update_node", "memory_injection_node")
    graph_builder.add_edge("memory_injection_node", "router_node")

    valid_destinations = {
        "fallback_node": "fallback_node",
        "create_task_node": "create_task_node",
        "get_current_issues_node": "get_current_issues_node",
        "get_user_issues_node": "get_user_issues_node"
    }
    
    graph_builder.add_conditional_edges(
        "router_node",
        select_route,
        valid_destinations
    )
    
    conversation_nodes = ["fallback_node", "create_task_node", "get_current_issues_node", "get_user_issues_node"]

    for conversation_node in conversation_nodes:
        graph_builder.add_edge(conversation_node, END)

    return graph_builder

graph = create_graph().compile()
