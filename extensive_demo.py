import os
import asyncio
from termcolor import colored
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from googlesearch import search as google_search
import json
import sys
from src.dillagent.models import DescribedModel, Field
from src.dillagent.llm import OpenAILLM, LLMConfig
from src.dillagent.tools import tool
from src.dillagent.agents.agents import StarterAgent
from src.dillagent.dependencies.prompts import MultiInputSysPrompt
from src.dillagent.workflows.graphs import StarterAgentGraph
from src.dillagent.workflows.graphs import PlanningAgentGraphExecutor
from src.dillagent.dependencies.parsers.intermediate.BaseIntermediateParser import BaseIntermediateParser
from src.dillagent.dependencies.parsers.intermediate.PlanningJsonParser import PlanningJsonParser

# Load environment variables
load_dotenv()

# Schema definitions for our tools
class SearchSchema(DescribedModel):
    query: str = Field(...,
                       description="Query to be searched in the form of a string.")

# Tool definitions
@tool(name="Search", description="Useful for searching for information on the web", schema=SearchSchema)
def search(query: str):
    """Perform a web search and return the content of the top result."""
    res = ""
    search_results = list(google_search(query, num_results=1))
    if search_results:
        # Fetch the content of the first search result page
        page_url = search_results[0]
        response = requests.get(page_url)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract text from the HTML content
            for data in soup.find_all("p"):
                res += "\n" + data.get_text()
            # Return the plain text
            return f"Search results for '{query}':\n{res}"
        else:
            return f"Failed to retrieve page content for '{query}'"
    else:
        return f"No search results found for '{query}'"

# Configure the LLM
llm_config = LLMConfig(
    model="gpt-4-turbo-preview",  # You can change this to use a different model
    api_key=os.environ.get('API_KEY'), 
    path="https://api.openai.com/v1/"
)

# Modify StarterAgent to handle both prompt and inputs
class ResearchAgent(StarterAgent):
    async def run(self, *, prompt=None, inputs=None):
        """Run the agent with either prompt string or structured inputs."""
        if inputs:
            # Format inputs into a prompt string
            formatted_prompt = json.dumps(inputs)
            return self.llm.run(formatted_prompt)
        elif prompt:
            return self.llm.run(prompt)
        else:
            raise ValueError("Either prompt or inputs must be provided")

async def create_agent_network():
    print(colored("Creating a planning-based multi-agent research network...", "blue"))
    
    # Research Agent - Gathers information based on search queries
    research_agent_prompt = MultiInputSysPrompt(
        "You are a Research Assistant. You take search queries and use the Search tool to gather "
        "relevant information. For each query, return a summary of the key findings. "
        "Return a JSON object with the key 'research_results' containing your findings."
    )
    research_agent = ResearchAgent(
        OpenAILLM(llm_config),
        [search],
        research_agent_prompt,
        name="ResearchAgent"
    )
    
    # Analysis Agent - Analyzes information
    analysis_agent_prompt = MultiInputSysPrompt(
        "You are an Analysis Assistant. You review research findings and analyze them to identify "
        "key insights, patterns, and implications. Synthesize the most important information "
        "and highlight any contradictions or gaps. "
        "Return a JSON object with the key 'analysis' containing your analysis."
    )
    analysis_agent = ResearchAgent(
        OpenAILLM(llm_config),
        [search],
        analysis_agent_prompt,
        name="AnalysisAgent"
    )
    
    # Report Agent - Creates the final report
    report_agent_prompt = MultiInputSysPrompt(
        "You are a Report Generation Assistant. You take analyzed research and format it into "
        "a comprehensive, well-structured report for the user. Include an executive summary, "
        "key findings, and recommendations. Make the report clear, concise, and professional. "
        "Return a JSON object with the key 'final_report' containing the formatted report."
    )
    report_agent = ResearchAgent(
        OpenAILLM(llm_config),
        [search],
        report_agent_prompt,
        name="ReportAgent"
    )
    
    # Planning Agent - Controls the workflow
    planning_agent_prompt = MultiInputSysPrompt(
        "You are a Research Planning Agent that coordinates a team of specialized research agents. "
        "Your job is to examine the current state of a research task and determine which agents "
        "should be called next and with what inputs. You will also be provided with the user's initial request."
        "\n\n"
        "You have access to the following agents:\n"
        "- ResearchAgent: Performs searches and gathers information\n"
        "- AnalysisAgent: Analyzes and synthesizes research findings\n"
        "- ReportAgent: Creates a final report based on the analysis\n"
        "\n\n"
        "For each step, you must return a JSON object with the following structure:\n"
        "{\n"
        "  \"next_agents\": [\"AgentName1\", \"AgentName2\"],  // List of agents to call next\n"
        "  \"agent_inputs\": {  // Specific inputs for each agent\n"
        "    \"AgentName1\": { ... inputs for agent 1 ... },\n"
        "    \"AgentName2\": { ... inputs for agent 2 ... }\n"
        "  },\n"
        "  \"terminate\": false  // Set to true when the task is complete\n"
        "}\n\n"
        "When you determine the research is complete, set 'terminate' to true and include "
        "no agents in the 'next_agents' list."
    )
    planning_agent = ResearchAgent(
        OpenAILLM(llm_config),
        [search],
        planning_agent_prompt,
        name="PlanningAgent"
    )


    
    # Create the agent graph
    graph = StarterAgentGraph()
    
    # Set input and output agents
    graph.input_agent = planning_agent
    graph.output_agent = report_agent
    
    graph.add_edge(planning_agent, research_agent)
    graph.add_edge(planning_agent, analysis_agent)
    graph.add_edge(planning_agent, report_agent)
    
    # Create a custom JSON parser for planning
    parser = PlanningJsonParser()
    
    # Create the planning-based executor
    executor = PlanningAgentGraphExecutor(graph, parser)
    executor.set_planning_agent(planning_agent)
    
    return executor

async def run_research_workflow(query):
    """Run the multi-agent research workflow."""
    
    print(colored(f"Starting research on: {query}", "green"))
    
    # Create the agent network
    executor = await create_agent_network()
    
    # Run the workflow
    try:
        results = await executor.run({"user_query": query})
        
        if isinstance(results, dict) and 'final_report' in results:
            print(colored("\n=== FINAL REPORT ===\n", "yellow"))
            print(colored(results['final_report'], "cyan"))
        elif isinstance(results, dict) and 'raw_output' in results:
            print(colored("\n=== FINAL REPORT ===\n", "yellow"))
            print(colored(results['raw_output'], "cyan"))
        else:
            print(colored("\nHere's the output from the research system:", "yellow"))
            print(colored(json.dumps(results, indent=2), "cyan"))
            
    except Exception as e:
        print(colored(f"Error occurred: {str(e)}", "red"))
        import traceback
        traceback.print_exc()

# Main function
async def main():
    print(colored("Welcome to the Planning-based Multi-Agent Research System!", "blue"))
    print(colored("This system uses a planning agent to coordinate multiple specialized agents for research.", "blue"))
    
    while True:
        query = input(colored("\nWhat would you like to research? (or 'exit' to quit)\n> ", "green"))
        
        if query.lower() in ('exit', 'quit', 'q'):
            print(colored("Thank you for using the Multi-Agent Research System. Goodbye!", "blue"))
            break
            
        await run_research_workflow(query)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())