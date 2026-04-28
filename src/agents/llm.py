import json
import re
from typing import Any

from langchain_ollama import ChatOllama

__all__ = ["_llm", "_parse_python_tag_calls"]

_llm = ChatOllama(model="llama3.1", base_url="http://ollama:11434")


def _parse_python_tag_calls(content: str) -> list[dict[str, Any]]:
    """Parse llama3.1's native tool calls.
    The model uses 'parameters' as the key; we normalise to 'args' for consistency.
    """
    calls: list[dict[str, Any]] = []
    for match in re.finditer(r"<\|python_tag\|>(\{.*?\})\s*(?=<\|python_tag\|>|$)", content, re.DOTALL):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        name = data.get("name")
        if not name:
            continue
        args = data.get("parameters", data.get("arguments", data.get("args", {})))
        calls.append({"name": name, "args": args, "id": f"ptag_{len(calls)}"})
    return calls
