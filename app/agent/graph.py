from datetime import date
from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.prompt import SYSTEM_PROMPT
from app.agent.state import AgentState
from app.agent.tools import get_total_spent
from app.config import get_settings

TOOLS = [get_total_spent]


@lru_cache
def build_llm():
    """Chat model with the tools bound, created once and reused."""
    settings = get_settings()
    llm = init_chat_model(
        model=settings.llm_model,
        model_provider="openai",  # OpenRouter speaks the OpenAI API
        base_url=settings.llm_base_url,
        api_key=settings.openrouter_api_key.get_secret_value(),
        temperature=settings.llm_temperature,
        timeout=30,
        max_retries=2,
    )
    return llm.bind_tools(TOOLS)  # the model now knows which tools it can ask for


# System prompt + the conversation from the state. The system prompt is never stored in the state.
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("messages"),
])


def call_model(state: AgentState) -> dict:
    """Ask the model what to do next: call a tool or answer the user."""
    chain = prompt | build_llm()
    response = chain.invoke({"messages": state["messages"], "today": date.today().isoformat()})
    return {"messages": [response]}  # appended to the state by the add_messages reducer


def route_after_model(state: AgentState) -> str:
    """Go to the tools if the model asked for any, otherwise stop."""
    last_msg = state["messages"][-1]
    if last_msg.tool_calls:
        return "use_tools"
    return "done"


def build_graph():
    """ReAct loop: model -> tools -> model ... until the model answers with text."""
    graph = StateGraph(AgentState)

    graph.add_node("call_model", call_model)
    graph.add_node("tools", ToolNode(TOOLS))  # runs the requested tools and passes them the config

    graph.add_edge(START, "call_model")
    graph.add_conditional_edges(
        "call_model",
        route_after_model,
        {"use_tools": "tools", "done": END},
    )
    graph.add_edge("tools", "call_model")  # after a tool, the model reads the result

    # The checkpointer stores each conversation by the thread_id in the config
    return graph.compile(checkpointer=InMemorySaver())