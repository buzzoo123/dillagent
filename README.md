# DillAgent

DillAgent is an AI agent library based on the principles of *ReAct: Synergizing Reasoning and Acting in Language Models*. While there are existing libraries such as Langchain, Langroid, and Llamaindex, DillAgent takes a different approach by prioritizing modularity and abstraction to provide developers with more control over their LLM-powered applications.

## Overview

DillAgent empowers developers by offering a high-level framework while allowing customization of prompts, formatting, and logic patterns - which is necessary when using a non-deterministic technology like an LLM. It provides a structured environment for creating production-ready LLM-powered applications. The key abstractions in DillAgent include:

1. **LLM**: A wrapper for any provided Language Model, accessible via API or executable path, serving as the engine for any AI Agent framework.
   
2. **Tool**: Contains an LLM-callable function with user-defined descriptions/instructions to provide to the LLM.
   
3. **Agent**: Comprised of an LLM, Tools that the LLM can use, and a System Prompt to set up the environment for an AI Agent loop regardless of specific logic implementation.
   
4. **Agent Executor**: Utilizes an Agent, intermediate parser, and output parser in a loop, allowing developers to implement their own logic to achieve various tasks using LLM reasoning.

## High Level Usage:

1. Define Tools and Schemas for the parameters of the tool fucntions using Described Models
2. Instantiate an LLM and SysPrompt (Abstraction for system prompt)
3. Instantiate an Agent using the LLM and SysPrompt
4. Create an Agent Executor to run the agent

It should be noted that AgentExecutors can be implemented into loops for continuous chats with conversational memory.

## Basic Example Usage

**Before running this example, make sure you have the `dillagent` package installed.** You can install it using pip:

```bash
pip install dillagent
```
Then using python...
```python
from dillagent.models import DescribedModel, Field
from dillagent.agents.executors import ConversationalExecutor
from dillagent.llm import OpenAILLM, LLMConfig
from dillagent.tools import tool
from dillagent.agents.agents import AdvancedAgent
from dotenv import load_dotenv

load_dotenv()

class SearchSchema(DescribedModel):
  query: str = Field(...,
            description="Query to be searched in the form of a string.")

@tool(name="Search", description="Useful for searching for information", schema=SearchSchema)
def search(query: str):
  # Return search results using query
  return "I searched the internet for your query!"

llm = OpenAILLM(LLMConfig(
  model="gpt-3.5-turbo-0125", api_key=os.environ.get('API_KEY'), path="[https://api.openai.com/v1/](https://api.openai.com/v1/)"),)

sys_prompt = MultiInputSysPrompt("You are a helpful AI Assistant.")

agent = AdvancedAgent(llm, [search], sys_prompt)

runner = ConversationalExecutor(agent, JsonParser(
  ['action', 'action_input'], 'action', 'action_input'))

prompt = input("What can I help you with?\n")

print(runner.run(prompt))
```

View the project documentation for further implementation details.

## Demo

This library is currently under development. However, you can use the provided `demo.py` file to demo the project with premade "dummy" tools. Follow these instructions:

1. Clone the repository.
2. Create and start a Python 3.10+ virtual environment.
3. Install the required packages: `pip install -r requirements.txt`.
4. Create a `.env` file and add your OpenAI API key: `OPENAI_API_KEY=<your_api_key>`.
5. Run the command `python demo.py` to execute the program.
6. Press `CTRL + C` to exit.

**WARNING:** This will consume API tokens (gpt-3.5-turbo-0125 by default), which may incur costs. Make sure to use it responsibly.
