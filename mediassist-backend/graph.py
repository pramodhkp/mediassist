from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from agents.input_agent import input_agent_llm, INPUT_AGENT_SYSTEM_PROMPT
from agents.output_agent import output_agent_llm, OUTPUT_AGENT_SYSTEM_PROMPT
from agents.orchestrator_agent import orchestrator_agent_llm, ORCHESTRATOR_SYSTEM_PROMPT
from agents.nutrition_agent import nutrition_agent_llm, NUTRITION_AGENT_SYSTEM_PROMPT
from agents.medical_conditions_agent import medical_conditions_agent_llm, MEDICAL_CONDITIONS_AGENT_SYSTEM_PROMPT

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

def query_or_input(state):
    """Decides whether the user is asking a question or providing input."""
    user_message = state["messages"][-1]
    if "USER_INTENT: \"question\"" in user_message.content:
        return "question"
    elif "USER_INTENT: \"input\"" in user_message.content:
        return "input"
    else:
        return "input"  # Default to unknown if not clear

def input_agent(state: State):
    system_message = SystemMessage(content=INPUT_AGENT_SYSTEM_PROMPT)
    return {"messages": [input_agent_llm.invoke([system_message] + state["messages"])]}

def output_agent(state: State):
    system_message = SystemMessage(content=OUTPUT_AGENT_SYSTEM_PROMPT)
    return {"messages": [output_agent_llm.invoke([system_message] + state["messages"])]}

def orchestrator_agent(state: State):
    system_message = SystemMessage(content=ORCHESTRATOR_SYSTEM_PROMPT)
    return {"messages": [orchestrator_agent_llm.invoke([system_message] + state["messages"])]}

def nutrition_agent(state: State):
    system_message = SystemMessage(content=NUTRITION_AGENT_SYSTEM_PROMPT)
    return {"messages": [nutrition_agent_llm.invoke([system_message] + state["messages"])]}

def medical_conditions_agent(state: State):
    system_message = SystemMessage(content=MEDICAL_CONDITIONS_AGENT_SYSTEM_PROMPT)
    return {"messages": [medical_conditions_agent_llm.invoke([system_message] + state["messages"])]}

graph_builder.add_node("input_agent", input_agent)
graph_builder.add_node("orchestrator_agent", orchestrator_agent)
graph_builder.add_node("output_agent", output_agent)
graph_builder.add_node("nutrition_agent", nutrition_agent)
graph_builder.add_node("medical_conditions_agent", medical_conditions_agent)

graph_builder.add_edge(START, "input_agent")
graph_builder.add_conditional_edges("input_agent", query_or_input, {
    "question": "output_agent",
    "input": "orchestrator_agent",
})

graph_builder.add_edge("input_agent", "orchestrator_agent")
graph_builder.add_conditional_edges("orchestrator_agent", forward_or_respond, {
    "nutrition_agent": "nutrition_agent",
    "medical_conditions_agent": "medical_conditions_agent",
    "respond": "output_agent",
})

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Chat part

config = {"configurable": {"thread_id": "1"}}
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config=config):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break