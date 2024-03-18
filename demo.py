import random
import os
from agents.agents import AdvancedAgent
from tools import tool
from typing import List
from models import DescribedModel, Field
from llm import OpenAILLM, LLMConfig
from agents.executors import ConversationalExecutor
import requests
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from dotenv import load_dotenv
from dependencies.prompts import MultiInputSysPrompt
from dependencies.parsers.intermediate import JsonParser
from termcolor import colored

load_dotenv()


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


llm = OpenAILLM(LLMConfig(
    # model="gpt-3.5-turbo-0125", api_key=os.environ.get('API_KEY'), path="https://api.openai.com/v1/"),)
    model="gpt-4", api_key=os.environ.get('API_KEY'), path="https://api.openai.com/v1/"),)

sys_prompt = MultiInputSysPrompt("You are a helpful AI Assistant.")

agent = AdvancedAgent(
    llm, [search, make_music, generate_quote, make_map, make_sat], sys_prompt)

print(agent.sys_prompt.prompt_str)

runner = ConversationalExecutor(agent, JsonParser(
    ['action', 'action_input'], 'action', 'action_input'))

prompt = input(colored("What can I help you with?\n", "green"))
while (True):
    print(colored(runner.run(prompt), "green"))
    prompt = input("")
