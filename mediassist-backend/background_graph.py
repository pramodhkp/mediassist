from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from agents.insights_agent import insights_agent_llm, INSIGHTS_AGENT_SYSTEM_PROMPT
from tools.tools import tool_node

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def forward_or_respond(state):
    """Decides whether to forward the request to another agent or respond directly."""
    user_message = state["messages"][-1]
    if "nutrition_agent" in user_message.content:
        return "nutrition_agent"
    elif "medical_conditions_agent" in user_message.content:
        return "medical_conditions_agent"
    else:
        return "respond"

def insights_agent(state: State):
    system_message = SystemMessage(content=INSIGHTS_AGENT_SYSTEM_PROMPT)
    response = tool_node.invoke({"messages": [insights_agent_llm.invoke([system_message] + state["messages"])]})
    print(response)
    output = AIMessage(content=response["messages"][-1].content)
    return {"messages": [output]}


# Nodes in the graph
graph_builder.add_node("insights_agent", insights_agent)
graph_builder.add_edge(START, "insights_agent")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Chat part

config = {"configurable": {"thread_id": "1"}}
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config=config):
        for key, value in event.items():
            print(key, value["messages"][-1].content)

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    stream_graph_updates(user_input)
