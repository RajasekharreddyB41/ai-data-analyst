from langchain_groq import ChatGroq


def get_llm(api_key: str):
    """Create and return a Groq LLM instance."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0
    )
    return llm