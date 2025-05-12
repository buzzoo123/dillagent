import asyncio
import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from pydantic import Field
from src.dillagent.models import DescribedModel
from src.dillagent.tools import tool
from src.dillagent.llm import OpenAILLM, LLMConfig
from src.dillagent.agents.agents import StarterAgent
from src.dillagent.agents.executors import BaseAgentExecutor
from src.dillagent.dependencies.parsers.intermediate import JsonParser
from src.dillagent.dependencies.prompts.MultiAgentSupervisorSysPrompt import MultiAgentSupervisorSysPrompt
from src.dillagent.dependencies.prompts.MultiInputToolsSysPrompt import MultiInputToolsSysPrompt
from src.dillagent.workflows.signalFlows.signalFlows import BaseSignal, BaseSignalBinding
from src.dillagent.workflows.signalFlows.executors import BaseSignalFlowExecutor

# Load environment variables
load_dotenv()

# Setup OpenAI API
llm_config = LLMConfig(
    model="gpt-4o-2024-08-06",
    api_key=os.environ.get('OPENAI_API_KEY'),
    path="https://api.openai.com/v1/"
)

# Define schemas for our tools
class SearchSchema(DescribedModel):
    query: str = Field(..., description="The search query in the form of a string.")

class WeatherSchema(DescribedModel):
    location: str = Field(..., description="The location to get weather for (city name or coordinates).")

class SummarySchema(DescribedModel):
    content: str = Field(..., description="Content to be output for the final response.")

# Define tools
@tool(name="Search Tool", description="Search the internet for information on a topic.", schema=SearchSchema)
def search(query: str):
    """Simulated internet search."""
    try:
        # For demo purposes, we'll use a simple simulation
        if "weather" in query.lower():
            return "Weather information should be obtained using the Weather tool."
        elif "news" in query.lower():
            return "Latest news: AI is actually apporaching the singularity according to researchers."
        elif "recipe" in query.lower():
            return "Found several recipes that match your query. Top result: Classic pasta carbonara with eggs, cheese, and bacon."
        else:
            return f"Search results for '{query}': Found information related to your query. This is simulated search data."
    except Exception as e:
        return f"Error performing search: {str(e)}"

@tool(name="Weather", description="Get current weather information for a single location.", schema=WeatherSchema)
def get_weather(location: str):
    """Simulated weather API call."""
    # For demo purposes, we'll return mock data
    mock_weather = {
        "location": location,
        "temperature": 72,
        "condition": "Partly Cloudy",
        "humidity": 65,
        "wind_speed": 8
    }
    return json.dumps(mock_weather)

@tool(name="Respond To User", description="Respond to the user with a final output string", schema=SummarySchema)
def respond_to_user(content: str):
    """Tool for the output agent to organize its thinking."""
    # This tool doesn't do anything external
    print(content)

async def main():
    # Setup parsers for JSON output from LLMs
    parser = JsonParser(['action', 'action_input'])
    
    # Create prompt templates for agents with tools
    weather_prompt = MultiInputToolsSysPrompt(
        "You are a Weather Agent. Your job is to get accurate weather information for a location. "
        "Always extract the location from the query before using your tool."
    )
    
    search_prompt = MultiInputToolsSysPrompt(
        "You are a Search Agent. Your job is to search for information on the internet. "
        "Format search queries to be clear and concise."
    )
    
    output_prompt = MultiInputToolsSysPrompt(
        "You are an Output Agent. Your job is to take information from the Weather Agent and/or Search Agent "
        "and present it in a helpful, well-formatted way to the user. Always include all relevant information."
        "You must adhere to the JSON response format detailed below."
    )
    
    # Create planner prompt (using MultiAgentSupervisorSysPrompt)
    planner_prompt = MultiAgentSupervisorSysPrompt(
        "You are a Planning Agent. Your job is to determine which specialized agents to use. You will be given the current state of execution and available agents to choose from next."
        "For each query, select which agent(s) should process it by returning their names in the 'next_executors' list, "
        "and provide specific inputs for each selected agent by returning their inputs in the <Agentname_input> field."
        "If the query is complete, set 'terminate' to true.\n\n"
        "You must respond in the following format exactly:\n"
        "{\n"
        "  \"next_executors\": [\"WeatherAgent\", \"SearchAgent\"],\n"
        "  \"WeatherAgent_input\": \"What's the weather in New York?\",\n"
        "  \"SearchAgent_input\": \"Latest news about technology\",\n"
        "  \"terminate\": false\n"
        "}\n\n"
        "Only return the agents needed for the specific query. If none match, next_executors "
        "can be left empty to skip to the next execution layer. "
        "Make sure to include appropriate input "
        "fields for each agent (e.g., 'WeatherAgent_input' for WeatherAgent). "
        "If all required information has been gathered and the OutputAgent has been used to respond to the user, set 'terminate' to true."
        "Ensure you adhere to the output format. Begin!"
)
    
    # Create LLM instances for each agent
    planner_llm = OpenAILLM(llm_config)
    weather_llm = OpenAILLM(llm_config)
    search_llm = OpenAILLM(llm_config)
    output_llm = OpenAILLM(llm_config)
    
    # Create agents
    planner_agent = StarterAgent(planner_llm, [], parser, planner_prompt, "", name="PlannerAgent")
    weather_agent = StarterAgent(weather_llm, [get_weather], parser, weather_prompt, "Takes a weather related query in words", name="WeatherAgent")
    search_agent = StarterAgent(search_llm, [search], parser, search_prompt, "Takes an internet search related query in words", name="SearchAgent")
    output_agent = StarterAgent(output_llm, [respond_to_user], parser, output_prompt, "Takes a string of all relevant information needed for a final answer", name="OutputAgent", logging_enabled=True)
    
    # Create agent executors
    planner_executor = BaseAgentExecutor(planner_agent)
    weather_executor = BaseAgentExecutor(weather_agent, tool_indicator_key="action_input", tool_output_key="tool_result")
    search_executor = BaseAgentExecutor(search_agent, tool_indicator_key="action_input", tool_output_key="tool_result")
    output_executor = BaseAgentExecutor(output_agent, tool_indicator_key="action_input", tool_output_key="tool_result", logging_enabled=True)