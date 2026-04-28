import json
import re
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from langchain_ollama import ChatOllama

__all__ = ["_llm", "_parse_python_tag_calls", "run_react_loop"]

_llm = ChatOllama(model="llama3.1", base_url="http://ollama:11434")


def run_react_loop(
    messages: list,
    llm_with_tools: Any,
    tool_map: dict[str, Any],
    stop_on: set[str] | None = None,
) -> str:
    """Generic ReAct loop shared by all agents.

    stop_on: tool names that trigger an immediate return.
             None means always return after the first tool batch (orchestrator).
    """
    while True:
        try:
            response: AIMessage = llm_with_tools.invoke(messages)
        except Exception as e:
            return f"The assistant is temporarily unavailable: {e}"
        messages.append(response)
        tool_calls = response.tool_calls or _parse_python_tag_calls(str(response.content))
        if not tool_calls:
            return str(response.content)
        results: list[str] = []
        for tc in tool_calls:
            name = tc["name"]
            try:
                result = tool_map[name].invoke(tc["args"]) if name in tool_map else f"Unknown tool: {name}"
            except Exception as e:
                result = f"Tool call failed — missing or invalid arguments: {e}. Please retry with all required parameters."
            results.append(str(result))
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
        if stop_on is None or any(tc["name"] in stop_on for tc in tool_calls):
            return "\n".join(results)


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
