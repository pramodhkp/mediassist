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
from agents.insights_agent import insights_agent_llm, INSIGHTS_AGENT_SYSTEM_PROMPT
from agents.intent_classifier_agent import intent_classifier_llm, INTENT_CLASSIFIER_SYSTEM_PROMPT
from storage.client import store_nutrition_data, store_medical_conditions_data, store_user_profile_data
from agents.medical_conditions_agent import medical_conditions_agent_llm, MEDICAL_CONDITIONS_AGENT_SYSTEM_PROMPT
from agents.user_profile_agent import user_profile_agent_llm, USER_PROFILE_AGENT_SYSTEM_PROMPT

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def forward_or_respond(state):
    """Decides whether to forward the request to another agent or respond directly using LLM-based intent classification."""
    user_message = state["messages"][-2]
    system_message = SystemMessage(content=INTENT_CLASSIFIER_SYSTEM_PROMPT)
    print(user_message)
    
    # Use the intent classifier to determine thpe user's intent
    classification = intent_classifier_llm.invoke([system_message, user_message])
    
    print(f"Intent classification: {classification.intent} (confidence: {classification.confidence})")
    print(f"Explanation: {classification.explanation}")
    
    # Route based on the classified intent
    if classification.intent == "user_profile":
        return "user_profile_agent"
    elif classification.intent == "nutrition":
        return "nutrition_agent"
    elif classification.intent == "medical_conditions":
        return "medical_conditions_agent"
    elif classification.intent == "data_fetcher":
        return "data_fetcher_agent"
    else:  # general or any other intent
        return "respond"

def input_agent(state: State):
    print("INPUT AGENT")
    system_message = SystemMessage(content=INPUT_AGENT_SYSTEM_PROMPT)
    return {"messages": [input_agent_llm.invoke([system_message] + state["messages"])]}

def output_agent(state: State):
    print("OUTPUT AGENT")
    print(state["messages"][-1])
    system_message = SystemMessage(content=OUTPUT_AGENT_SYSTEM_PROMPT)
    return {"messages": [output_agent_llm.invoke([system_message] + state["messages"])]}

def orchestrator_agent(state: State):
    print("ORCHESTRATOR AGENT")
    system_message = SystemMessage(content=ORCHESTRATOR_SYSTEM_PROMPT)
    return {"messages": [orchestrator_agent_llm.invoke([system_message] + state["messages"])]}

def nutrition_agent(state: State):
    print("NUTRITION AGENT")
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
    print("MEDICAL CONDITIONS AGENT")
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

def insights_agent(state: State):
    """
    Handles nutrition-related queries by analyzing nutrition data and providing actionable insights.
    """
    print("INSIGHTS AGENT")
    system_message = SystemMessage(content=INSIGHTS_AGENT_SYSTEM_PROMPT)
    
    # Get response from the insights agent
    response = insights_agent_llm.invoke([system_message] + state["messages"])
    
    return {"messages": state["messages"] + [AIMessage(content=response.content)]}

def user_profile_agent(state: State):
    print("USER PROFILE AGENT")
    system_message = SystemMessage(content=USER_PROFILE_AGENT_SYSTEM_PROMPT)
    llm_response = user_profile_agent_llm.invoke([system_message] + state["messages"])
    user_profile_data = llm_response.dict()
    
    try:
        # Store the profile data
        store_user_profile_data(user_profile_data)
        response = AIMessage(content="Thank you! I've updated your profile information.")
    except Exception as e:
        print(f"Error storing user profile data: {e}")
        response = AIMessage(content="I'm sorry, I couldn't save your profile information. Please try again.")
        return {"messages": [system_message] + state["messages"] + [response]}

    return {"messages": [system_message] + state["messages"] + [response]}

# Nodes in the graph
graph_builder.add_node("input_agent", input_agent)
graph_builder.add_node("orchestrator_agent", orchestrator_agent)
graph_builder.add_node("output_agent", output_agent)
graph_builder.add_node("nutrition_agent", nutrition_agent)
graph_builder.add_node("medical_conditions_agent", medical_conditions_agent)
graph_builder.add_node("user_profile_agent", user_profile_agent)
graph_builder.add_node("insights_agent", insights_agent)

# Edges in the graph
graph_builder.add_edge(START, "input_agent")
graph_builder.add_edge("input_agent", "orchestrator_agent")

graph_builder.add_conditional_edges("orchestrator_agent", forward_or_respond, {
    "nutrition_agent": "nutrition_agent",
    "medical_conditions_agent": "medical_conditions_agent",
    "user_profile_agent": "user_profile_agent",
    "insights_agent": "insights_agent",
    "respond": "output_agent",
})

graph_builder.add_edge("nutrition_agent", "output_agent")
graph_builder.add_edge("medical_conditions_agent", "output_agent")
graph_builder.add_edge("user_profile_agent", "output_agent")
graph_builder.add_edge("insights_agent", "output_agent")
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
