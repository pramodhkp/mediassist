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
from storage.client import store_nutrition_data, store_medical_conditions_data
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
    response = nutrition_agent_llm.invoke([system_message] + state["messages"])
    nutrition_data = response.dict()
    try:
        store_nutrition_data(nutrition_data)
        response = AIMessage(content="Nutrition data stored successfully.")
    except Exception as e:
        print(f"Error storing nutrition data: {e}")
        response = AIMessage(content="Failed to store nutrition data.")
        return {"messages": [system_message] + state["messages"] + [response]}

    response = AIMessage(content="Nutrition data stored successfully.")
    return {"messages": [system_message] + state["messages"] + [response]}

def medical_conditions_agent(state: State):
    system_message = SystemMessage(content=MEDICAL_CONDITIONS_AGENT_SYSTEM_PROMPT)
    llm_response = medical_conditions_agent_llm.invoke([system_message] + state["messages"])
    medical_conditions_data = llm_response.dict()
    try:
        store_medical_conditions_data(medical_conditions_data)
        response = AIMessage(content="Medical conditions data stored successfully.") 
    except Exception as e:
        print(f"Error storing medical conditions data: {e}")
        response = AIMessage(content="Failed to store medical conditions data.")
        return {"messages": [system_message] + state["messages"] + [response]}

    return {"messages": [system_message] + state["messages"] + [response]}

# Nodes in the graph
graph_builder.add_node("input_agent", input_agent)
graph_builder.add_node("orchestrator_agent", orchestrator_agent)
graph_builder.add_node("output_agent", output_agent)
graph_builder.add_node("nutrition_agent", nutrition_agent)
graph_builder.add_node("medical_conditions_agent", medical_conditions_agent)

# Edges in the graph
graph_builder.add_edge(START, "input_agent")
graph_builder.add_edge("input_agent", "orchestrator_agent")

graph_builder.add_conditional_edges("orchestrator_agent", forward_or_respond, {
    "nutrition_agent": "nutrition_agent",
    "medical_conditions_agent": "medical_conditions_agent",
    "respond": "output_agent",
})

graph_builder.add_edge("nutrition_agent", "output_agent")
graph_builder.add_edge("medical_conditions_agent", "output_agent")

graph_builder.add_edge("output_agent", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Chat part

# config = {"configurable": {"thread_id": "1"}}
# def stream_graph_updates(user_input: str):
#     for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config=config):
#         for key, value in event.items():
#             print(key, value["messages"][-1].content)

# while True:
#     user_input = input("User: ")
#     if user_input.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")
#         break
#     stream_graph_updates(user_input)
