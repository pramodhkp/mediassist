import json
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from agents.data_fetcher_agent import data_fetcher_agent_llm, DATA_FETCHER_AGENT_SYSTEM_PROMPT
from agents.insights_agent import insights_agent_llm, INSIGHTS_AGENT_SYSTEM_PROMPT
from tools.tools import tool_node

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def process_tool_output(tool_calls):
    tool_output = []
    response = tool_node.invoke({"messages": [tool_calls]})
    for message in response['messages']:
        tool_output.append(message.content)
    return json.dumps(tool_output)

def data_fetcher_agent(state: State):
    system_message = SystemMessage(content=DATA_FETCHER_AGENT_SYSTEM_PROMPT)
    tool_calls = data_fetcher_agent_llm.invoke([system_message] + state["messages"])
    tool_output = process_tool_output(tool_calls)
    data = AIMessage(content=tool_output)
    return {"messages": [data]}

def insights_agent(state: State):
    system_message = SystemMessage(content=INSIGHTS_AGENT_SYSTEM_PROMPT)
    insights_response = insights_agent_llm.invoke([system_message] + state["messages"])
    return {"messages": [insights_response]}

# Nodes in the graph
graph_builder.add_node("data_fetcher_agent", data_fetcher_agent)
graph_builder.add_node("insights_agent", insights_agent)


graph_builder.add_edge(START, "data_fetcher_agent")
graph_builder.add_edge("data_fetcher_agent", "insights_agent")
graph_builder.add_edge("insights_agent", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)


