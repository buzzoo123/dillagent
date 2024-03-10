import random
from agents.agents.AdvancedAgent import AdvancedAgent
from tools.Tool import tool
from models.DescribedModel import DescribedModel, Field
from LLM.OpenAILLM import OpenAILLM
from LLM.LLMConfig import LLMConfig
from agents.Executors.AgentExecutor import AgentExecutor
from agents.Executors.ConversationalExecutor import ConversationalExecutor
import requests
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from dotenv import load_dotenv
import os
from Dependencies.Prompts.MultiInputSysPrompt import MultiInputSysPrompt
from Dependencies.Parsers.Intermediate.JsonParser import JsonParser


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
        "You will one day be Eric",
        "You will one day be Kieran",
        "I eat hairy assholes",
    ]
    random_element = random.choice(arr)
    return random_element


@tool(name="Make Music", description="Useful for making music", schema=VibeSchema)
def make_music(vibe: str, length: str):
    with open('example.txt', 'w') as file:
        file.write(vibe)
        file.write("Length: ", length)
    return "music file generated called example.txt"


# initial_prompt = StructuredPrompt(header, loop_conditions)
llm = OpenAILLM(LLMConfig(
    model="gpt-3.5-turbo-0125", api_key=os.environ.get('API_KEY'), path="https://api.openai.com/v1/"),)
# model="gpt-4", api_key=os.environ.get('API_KEY'), path="https://api.openai.com/v1/"),)

sys_prompt = MultiInputSysPrompt("You are a helpful AI Assistant.")

agent = AdvancedAgent(llm, [search, make_music, generate_quote], sys_prompt)

print(agent.sys_prompt.prompt_str)

runner = ConversationalExecutor(agent, JsonParser(
    ['action', 'action_input'], 'action', 'action_input'))

while (True):
    print(runner.run(input("What can I help you with?\n")))
