from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes.router import router_node
from graph.nodes.analyzer import analyzer_node
from graph.nodes.visualizer import visualizer_node
from graph.nodes.summarizer import summarizer_node


def decide_next(state: AgentState) -> str:
    """After routing, decide which node to go to."""
    route = state["route"]
    if route == "analyze":
        return "analyze"
    elif route == "visualize":
        return "visualize"
    elif route == "both":
        return "analyze"
    return "analyze"


def after_analyze(state: AgentState) -> str:
    """After analysis, check if we also need a chart."""
    if state["route"] == "both":
        return "visualize"
    return "summarize"


def build_graph():
    """Build and compile the LangGraph agent."""

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("analyze", analyzer_node)
    graph.add_node("visualize", visualizer_node)
    graph.add_node("summarize", summarizer_node)

    # Set entry point
    graph.set_entry_point("router")

    # Router -> decide path
    graph.add_conditional_edges("router", decide_next, {
        "analyze": "analyze",
        "visualize": "visualize",
    })

    # Analyze -> summarize OR visualize
    graph.add_conditional_edges("analyze", after_analyze, {
        "visualize": "visualize",
        "summarize": "summarize",
    })

    # Visualize -> always summarize
    graph.add_edge("visualize", "summarize")

    # Summarize -> end
    graph.add_edge("summarize", END)

    return graph.compile()