from pydantic import Field
from src.dillagent.models.DescribedModel import DescribedModel
from src.dillagent.llm.LLMConfig import LLMConfig
from src.dillagent.llm.OpenAILLM import OpenAILLM
from src.dillagent.tools.Tool import tool
import os

llm_config = LLMConfig(
    model="gpt-4o-2024-08-06",
    api_key=os.environ.get('OPENAI_API_KEY'),
    path="https://api.openai.com/v1/"
)

class SearchSchema(DescribedModel):
    query: str = Field(..., description="The search query in the form of a string.")

@tool(name="Search Tool", description="Search the internet for information on a topic.", schema=SearchSchema)
def search(query: str):
    """Simulated internet search."""
    try:
        # For demo purposes, we'll use a simple simulation
        if "weather" in query.lower():
            return "It is currently 100 degrees Celcius"
        elif "news" in query.lower():
            return "Latest news: AI is actually apporaching the singularity according to researchers."
        elif "recipe" in query.lower():
            return "Found several recipes that match your query. Top result: Classic pasta carbonara with eggs, cheese, and bacon."
        else:
            return f"Search results for '{query}': Found information related to your query. This is simulated search data."
    except Exception as e:
        return f"Error performing search: {str(e)}"


tools1 = [search]



openai = OpenAILLM(llm_config, tools=tools1)

res = await openai.run("What is the weather?")

print(res)
