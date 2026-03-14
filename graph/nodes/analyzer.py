from graph.state import AgentState
from utils.llm import get_llm
from utils.executor import self_healing_execute


def analyzer_node(state: AgentState) -> AgentState:
    """Generate and execute pandas code to answer the user's question."""

    llm = get_llm(state["api_key"])

    prompt = f"""You are a Python data analyst. Write pandas code to answer the user's question.

Dataset columns: {state["columns_info"]}
Sample data:
{state["sample_data"]}

Chat history:
{state["chat_history"]}

User question: {state["query"]}

Rules:
- The DataFrame is already loaded as `df`
- Store your final answer in a variable called `result`
- Only use pandas and basic Python — no imports needed
- Keep the code simple and short
- If the question references something from chat history, use that context

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
    import pandas as pd
    local_vars = {
        "df": state["df"],
        "pd": pd,
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

    if result["success"] and "result" in result["locals"]:
        state["code_output"] = str(result["locals"]["result"])
        state["error"] = ""
    elif result["success"]:
        state["code_output"] = "Code ran but no 'result' variable was found."
        state["error"] = ""
    else:
        state["code_output"] = ""
        state["error"] = result["error"]

    return state