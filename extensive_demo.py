import asyncio
import random
from typing import List
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pydantic import Field
import requests
from src.dillagent.dependencies.prompts import MultiAgentSupervisorSysPrompt
from src.dillagent.tools.Tool import tool
from src.dillagent.models.DescribedModel import DescribedModel
from src.dillagent.agents.agents import StarterAgent
from src.dillagent.llm import OpenAILLM, LLMConfig
from src.dillagent.dependencies.prompts import MultiInputToolsSysPrompt
from src.dillagent.dependencies.parsers.intermediate import JsonParser
from src.dillagent.workflows.graphs.graphs import BaseAgentGraph
from src.dillagent.workflows.graphs.executors import BaseAgentGraphExecutor
from googlesearch import search as google_search
import os

load_dotenv()

# Setup
llm = OpenAILLM(LLMConfig(
    model="gpt-4o-2024-08-06",
    api_key=os.environ['OPENAI_API_KEY'],
    path="https://api.openai.com/v1/"
))

class SearchSchema(DescribedModel):
    query: str = Field(...,
                       description="Query to be searched in the form of a string.")


class QuoteModel(DescribedModel):
    topic: str = Field(...,
                       description="Topic of motivational quote in the form of a string")


class VibeSchema(DescribedModel):
    vibe: str = Field(...,
                      description="The vibe of the music being made in the form of a String")
    length: str = Field(...,
                        description="The length of the song in seconds represented as an int")


class Route(DescribedModel):
    length: int = Field(...,
                        description="An int representing the route length")
    name: str = Field(..., description="The name of the route as a string")


class Map(DescribedModel):
    routes: List[Route] = Field(..., description="A list of route objects")


class Question(DescribedModel):
    question: str = Field(...,
                          description="An example SAT question in the form of a String")


@tool(name="Search", description="Useful for searching for information", schema=SearchSchema)
def search(query: str):
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
            return res
        else:
            return "Failed to retrieve page content"
    else:
        return "No search results found"


@tool(name="Quote Generator", description="Useful for generating motivational quotes", schema=QuoteModel)
def generate_quote(topic: str):
    arr = [
        "You will one day be as financially stable as Eric!",
        "You will one day be as smart as Kieran the great!",
        "One day, you will be a star!",
    ]
    random_element = random.choice(arr)
    return random_element


@tool(name="Make Music", description="Useful for making music", schema=VibeSchema)
def make_music(vibe: str, length: str):
    with open(vibe + '.txt', 'w') as file:
        file.write(vibe)
        file.write("Length: " + str(length))
    return "music file generated called example.txt"


@tool(name="Make Map", description="Useful for making maps", schema=Map)
def make_map(routes: List[Route]):
    print(routes)
    return "Map generated in file called map.txt"


@tool(name="Make Pracitce SAT Question", description="Useful for making practice SAT questions and outputting them in PDF format", schema=Question)
def make_sat(question: str):
    print(question)
    return "PDF Generated as sat.txt"

planner_sys_prompt = MultiAgentSupervisorSysPrompt("TO_DO - NEEDS TO SPECIFY WHAT AGENTS ARE AVAILABLE AS CHILDREN AND RETURN FORMAT TO EXECUTE")

#USE MULTIINPUTSYSPROMPTS FOR ALL AGENTS THAT REQUIRE TOOLS + APPROPRAITE PARSERS

#MAKE AGENTS

#MAKE GRAPH

#MAKE GRAPH EXECUTOR

parser = JsonParser(['action', 'action_input'])

# Agents
input_agent = StarterAgent(llm, [generate_quote], sys_prompt, parser, name="InputAgent")
music_agent = StarterAgent(llm, [make_music], sys_prompt, parser, name="MusicAgent")
quote_agent = StarterAgent(llm, [generate_quote], sys_prompt, parser, name="QuoteAgent")
summary_agent = StarterAgent(llm, [], sys_prompt, parser, name="SummaryAgent")

# Graph
graph = BaseAgentGraph()
graph.add_edge(input_agent, music_agent)
graph.add_edge(input_agent, quote_agent)
graph.add_edge(music_agent, summary_agent)
graph.add_edge(quote_agent, summary_agent)

# Executor
class SingleRunExecutor(BaseAgentGraphExecutor):
    async def run(self, input_data):
        return await self.run_iteration(input_data)

executor = SingleRunExecutor(graph)

# Run
async def main():
    user_prompt = input("What vibe of music and inspiration are you looking for?\n")
    input_data = {"InputAgent_input": user_prompt}
    result = await executor.run(input_data)
    print("\nFinal Summary Output:\n", result)

asyncio.run(main())
