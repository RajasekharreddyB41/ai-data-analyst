from graph.state import AgentState
from utils.llm import get_llm


def summarizer_node(state: AgentState) -> AgentState:
    """Turn raw analysis results into plain English insights."""

    # If there's an error and no output, skip summarization
    if state["error"] and not state["code_output"]:
        state["summary"] = "⚠️ Analysis failed. Please try rephrasing your question."
        return state

    llm = get_llm(state["api_key"])

    prompt = f"""You are a friendly data analyst explaining results to a business manager.

User question: {state["query"]}

Analysis result:
{state["code_output"]}

Rules:
- Explain the result in simple, clear language
- Highlight key numbers and what they mean
- If there are interesting patterns, mention them
- Keep it to 2-4 sentences
- Use bullet points only if there are multiple findings
- Do NOT mention code, pandas, or technical terms

Respond with ONLY the insight summary. No preamble."""

    response = llm.invoke(prompt)
    state["summary"] = response.content.strip()

    return state