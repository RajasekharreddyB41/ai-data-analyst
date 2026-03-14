from graph.state import AgentState
from utils.llm import get_llm
from utils.executor import self_healing_execute


def visualizer_node(state: AgentState) -> AgentState:
    """Generate and execute Plotly chart code from the user's question."""

    llm = get_llm(state["api_key"])

    # Include analysis result if available
    context = ""
    if state["code_output"]:
        context = f"\nAnalysis result from previous step:\n{state['code_output']}"

    prompt = f"""You are a data visualization expert. Write Python code to create a Plotly chart.

Dataset columns: {state["columns_info"]}
Sample data:
{state["sample_data"]}
{context}

Chat history:
{state["chat_history"]}

User question: {state["query"]}

Rules:
- The DataFrame is already loaded as `df`
- Use plotly.express as px (already imported)
- Use plotly.graph_objects as go (already imported)
- Store the figure in a variable called `fig`
- Make the chart clean and professional
- Add a clear title
- If the question references something from chat history, use that context
- Do NOT call fig.show()

Respond with ONLY Python code. No explanation, no markdown, no backticks."""

    response = llm.invoke(prompt)
    code = response.content.strip()

    # Clean up markdown backticks
    if code.startswith("```python"):
        code = code[9:]
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    code = code.strip()

    # Execute with self-healing
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd

    local_vars = {
        "df": state["df"],
        "pd": pd,
        "px": px,
        "go": go,
    }

    result = self_healing_execute(
        code=code,
        local_vars=local_vars,
        api_key=state["api_key"],
        columns_info=state["columns_info"],
        query=state["query"],
    )

    state["generated_code"] = result["code"]
    state["retry_count"] = result["retries"]

    if result["success"] and "fig" in result["locals"]:
        state["chart"] = result["locals"]["fig"]
        state["error"] = ""
    else:
        state["chart"] = None
        state["error"] = result.get("error", "")

    return state