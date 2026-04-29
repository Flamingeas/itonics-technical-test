from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from langchain_core.tools import tool

from agents.elements_agent import run_elements_agent
from agents.llm import _llm, run_react_loop


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
    "Reply directly to casual questions. "
    "For element tasks (search/create/update), use call_elements_agent_tool."
))


_ELEMENT_KEYWORDS = {"create", "search", "find", "update", "rename", "element", "idea", "task", "project", "read", "admin", "write", "delete"}


def _is_element_task(message: str) -> bool:
    words = set(message.lower().split())
    return bool(words & _ELEMENT_KEYWORDS)


def run_orchestrator(user_message: str, history: list[BaseMessage]) -> str:
    if _is_element_task(user_message):
        return run_elements_agent(user_message)
    messages: list = [_SYSTEM, *history, HumanMessage(content=user_message)]
    return run_react_loop(messages, _orchestrator_llm_with_tools, _orchestrator_tool_map)
