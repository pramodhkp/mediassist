from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from agents.user_profile_agent import user_profile_agent_llm, USER_PROFILE_AGENT_SYSTEM_PROMPT
from storage.client import store_user_profile_data

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def user_profile_agent(state: State):
    system_message = SystemMessage(content=USER_PROFILE_AGENT_SYSTEM_PROMPT)
    llm_response = user_profile_agent_llm.invoke([system_message] + state["messages"])
    user_profile_data = llm_response.dict()
    try:
        store_user_profile_data(user_profile_data)
        response = AIMessage(content=f"Thank you! I've updated your profile with the following information: Age: {user_profile_data.get('age', 'Not provided')}, Gender: {user_profile_data.get('gender', 'Not provided')}, Height: {user_profile_data.get('height', 'Not provided')} cm, Weight: {user_profile_data.get('weight', 'Not provided')} kg")
    except Exception as e:
        print(f"Error storing user profile data: {e}")
        response = AIMessage(content="I'm sorry, I couldn't save your profile information. Please try again.")
        return {"messages": [system_message] + state["messages"] + [response]}

    return {"messages": [system_message] + state["messages"] + [response]}

# Nodes in the graph
graph_builder.add_node("user_profile_agent", user_profile_agent)

# Edges in the graph
graph_builder.add_edge(START, "user_profile_agent")
graph_builder.add_edge("user_profile_agent", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)