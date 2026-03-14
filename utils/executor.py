from utils.llm import get_llm


def safe_execute(code: str, local_vars: dict) -> dict:
    """Execute code safely with restricted builtins."""

    allowed_builtins = {
        "len": len, "range": range, "int": int, "float": float,
        "str": str, "list": list, "dict": dict, "tuple": tuple,
        "round": round, "sum": sum, "min": min, "max": max,
        "sorted": sorted, "enumerate": enumerate, "zip": zip,
        "abs": abs, "bool": bool, "print": print, "isinstance": isinstance,
        "type": type, "set": set, "True": True, "False": False, "None": None,
    }
    safe_globals = {"__builtins__": allowed_builtins}

    try:
        exec(code, safe_globals, local_vars)
        return {"success": True, "locals": local_vars, "error": ""}
    except Exception as e:
        return {"success": False, "locals": local_vars, "error": str(e)}


def self_healing_execute(code: str, local_vars: dict, api_key: str,
                         columns_info: str, query: str, max_retries: int = 3) -> dict:
    """Execute code with automatic self-healing on failure."""

    result = safe_execute(code, local_vars.copy())

    if result["success"]:
        return {"success": True, "locals": result["locals"],
                "code": code, "error": "", "retries": 0}

    # Self-healing loop
    current_code = code
    for attempt in range(max_retries):
        llm = get_llm(api_key)

        fix_prompt = f"""You are a Python expert. The following code failed with an error.

Original user question: {query}
Dataset columns: {columns_info}

Failed code:
{current_code}

Error message:
{result["error"]}

Fix the code so it works correctly.

Rules:
- The DataFrame is already loaded as `df`
- pd (pandas) is available
- Keep the same goal as the original code
- Respond with ONLY fixed Python code. No explanation, no markdown, no backticks."""

        response = llm.invoke(fix_prompt)
        fixed_code = response.content.strip()

        # Clean markdown backticks
        if fixed_code.startswith("```python"):
            fixed_code = fixed_code[9:]
        if fixed_code.startswith("```"):
            fixed_code = fixed_code[3:]
        if fixed_code.endswith("```"):
            fixed_code = fixed_code[:-3]
        fixed_code = fixed_code.strip()

        current_code = fixed_code
        result = safe_execute(current_code, local_vars.copy())

        if result["success"]:
            return {"success": True, "locals": result["locals"],
                    "code": current_code, "error": "", "retries": attempt + 1}

    # All retries failed
    return {"success": False, "locals": result["locals"],
            "code": current_code, "error": result["error"],
            "retries": max_retries}