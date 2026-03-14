from graph.state import AgentState
from utils.llm import get_llm


def router_node(state: AgentState) -> AgentState:
    """Decide which path the query should take."""

    llm = get_llm(state["api_key"])

    prompt = f"""You are a query router for a data analysis agent.

The user has a dataset with these columns: {state["columns_info"]}

User query: {state["query"]}

Classify this query into exactly ONE of these categories:
- "analyze" — if the user wants numbers, statistics, comparisons, or calculations
- "visualize" — if the user wants a chart, plot, graph, or trend
- "both" — if the user wants analysis AND a visualization

Respond with ONLY one word: analyze, visualize, or both. Nothing else."""

    response = llm.invoke(prompt)
    route = response.content.strip().lower()

    # Fallback if LLM gives unexpected response
    if route not in ["analyze", "visualize", "both"]:
        route = "analyze"

    state["route"] = route
    return state