from typing import TypedDict, Optional
import pandas as pd


class AgentState(TypedDict):
    """State that flows between all nodes in the graph."""
    query: str
    api_key: str
    df: Optional[pd.DataFrame]
    columns_info: str
    sample_data: str
    route: str
    generated_code: str
    code_output: str
    error: str
    retry_count: int
    chart: Optional[object]
    summary: str
    chat_history: list