from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import tool

from agents.elements_agent import run_elements_agent
from agents.llm import _llm, _parse_python_tag_calls


@tool
def call_elements_agent_tool(task: str) -> str:
    """Delegate element-related tasks to the elements agent.

    Use this for: searching elements, creating elements, updating element titles.
    Args:
        task: Natural language description of the task
              (e.g. 'search for ideas in space:acme-projects').
    """
    return run_elements_agent(task)


_orchestrator_tools = [call_elements_agent_tool]
_orchestrator_llm_with_tools = _llm.bind_tools(_orchestrator_tools)
_orchestrator_tool_map = {t.name: t for t in _orchestrator_tools}

_SYSTEM = SystemMessage(content=(
    "For casual conversation or general questions, reply directly. "
    "For tasks involving elements (search, create, update), delegate to the els agent tool."
))


def run_orchestrator(user_message: str, history: list[BaseMessage]) -> str:
    messages: list = [_SYSTEM, *history, HumanMessage(content=user_message)]
    while True:
        try:
            response: AIMessage = _orchestrator_llm_with_tools.invoke(messages)
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
                result = _orchestrator_tool_map[name].invoke(tc["args"]) if name in _orchestrator_tool_map else f"Unknown tool: {name}"
            except Exception as e:
                result = f"Tool call failed — missing or invalid arguments: {e}. Please retry with all required parameters."
            results.append(str(result))
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
        # The els agent already returns a final answer.
        return "\n".join(results)
