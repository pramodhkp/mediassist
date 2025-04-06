from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from agents.deep_research_agent import deep_research_agent_llm, DEEP_RESEARCH_AGENT_SYSTEM_PROMPT
from agents.anonymizer_agent import anonymize_text
from storage.client import get_user_profile_data, get_medical_conditions_data, get_nutrition_data_for_period
from datetime import datetime, timedelta

class State(TypedDict):
    messages: Annotated[list, add_messages]
    report_content: str
    file_ids: list
    filenames: list

graph_builder = StateGraph(State)

def anonymize_content(state: State):
    """
    Anonymizes the report content before further processing.
    """
    print("ANONYMIZING CONTENT")
    
    # Get the report content from the state
    report_content = state['report_content']
    
    # Anonymize the content
    anonymized_content = anonymize_text(report_content)
    
    # Update the state with anonymized content
    return {"report_content": anonymized_content}

def prepare_context(state: State):
    """
    Prepares the context for the deep research agent by gathering user profile, medical conditions,
    and nutrition data. Uses the anonymized report content.
    """
    print("PREPARING CONTEXT FOR DEEP ANALYSIS")
    
    # Get user profile data
    user_profile = get_user_profile_data()
    
    # Get medical conditions data
    medical_conditions = get_medical_conditions_data()
    
    # Get nutrition data for the last 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    nutrition_data = get_nutrition_data_for_period(start_date, end_date)
    
    # Format the context message
    context_message = f"""
    I need to analyze a medical report with the following user context:
    
    MEDICAL REPORT:
    Filenames: {', '.join(state['filenames'])}
    Content: {state['report_content']}
    
    USER PROFILE:
    """
    
    if user_profile:
        context_message += f"""
        Age: {user_profile.get('age', 'Not provided')}
        Gender: {user_profile.get('gender', 'Not provided')}
        Height: {user_profile.get('height', 'Not provided')} cm
        Weight: {user_profile.get('weight', 'Not provided')} kg
        """
    else:
        context_message += "No user profile data available.\n"
    
    context_message += "\nMEDICAL CONDITIONS:\n"
    if medical_conditions:
        for condition in medical_conditions:
            context_message += f"""
            Condition: {condition.get('condition_name', 'Not provided')}
            Symptoms: {condition.get('symptoms', 'Not provided')}
            Treatment: {condition.get('treatment', 'Not provided')}
            Prevention: {condition.get('prevention', 'Not provided')}
            """
    else:
        context_message += "No medical conditions data available.\n"
    
    context_message += "\nNUTRITION DATA (Last 30 days):\n"
    if nutrition_data:
        # Summarize nutrition data
        total_entries = len(nutrition_data)
        avg_calories = sum(entry.get('calories', 0) for entry in nutrition_data) / total_entries if total_entries > 0 else 0
        avg_protein = sum(entry.get('protein', 0) for entry in nutrition_data) / total_entries if total_entries > 0 else 0
        avg_carbs = sum(entry.get('carbohydrates', 0) for entry in nutrition_data) / total_entries if total_entries > 0 else 0
        avg_fats = sum(entry.get('fats', 0) for entry in nutrition_data) / total_entries if total_entries > 0 else 0
        
        context_message += f"""
        Average daily calories: {avg_calories:.2f}
        Average daily protein: {avg_protein:.2f}g
        Average daily carbohydrates: {avg_carbs:.2f}g
        Average daily fats: {avg_fats:.2f}g
        Number of entries: {total_entries}
        """
        
        # Add some recent food items
        recent_foods = [entry.get('food_name', 'Unknown food') for entry in nutrition_data[:5]]
        context_message += f"Recent food items: {', '.join(recent_foods)}\n"
    else:
        context_message += "No nutrition data available.\n"
    
    # Create a human message with the context
    human_message = HumanMessage(content=context_message)
    
    return {"messages": [human_message]}

def deep_research_agent(state: State):
    """
    Analyzes the medical report using the deep research agent.
    """
    print("DEEP RESEARCH AGENT")
    system_message = SystemMessage(content=DEEP_RESEARCH_AGENT_SYSTEM_PROMPT)
    
    # Get response from the deep research agent
    response = deep_research_agent_llm.invoke([system_message] + state["messages"])
    
    return {"messages": state["messages"] + [AIMessage(content=response.content)]}

# Nodes in the graph
graph_builder.add_node("anonymize_content", anonymize_content)
graph_builder.add_node("prepare_context", prepare_context)
graph_builder.add_node("deep_research_agent", deep_research_agent)

# Edges in the graph
graph_builder.add_edge(START, "anonymize_content")
graph_builder.add_edge("anonymize_content", "prepare_context")
graph_builder.add_edge("prepare_context", "deep_research_agent")
graph_builder.add_edge("deep_research_agent", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)