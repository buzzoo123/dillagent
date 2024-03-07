from agents.BaseAgent import BaseAgent
from Dependencies.Parsers.IntermediateParser import IntermediateParser


class AgentExecutor:
    def __init__(self, agent):
        self.agent = agent
        # Eventually get parser keywords from PromptTemplate
        self.im_parser = IntermediateParser(['Action', 'Action Input'])

    def run(self, prompt):
        # print("\n\n\n", self.agent.llm.messages)
        count = 0
        while True:
            if (count > 10):
                exit("SHIT IS TAKING TOO LONG!")
            count += 1
            response = self.agent.run(prompt).choices[0].message.content
            print(response)
            parsed = self.im_parser.parse_values(response)
            to_call = parsed['Action']
            to_input = parsed['Action Input']
            observation = None
            if to_call.upper() == "RESPONSE TO HUMAN":
                return to_input

            for tool in self.agent.tools:
                if to_call == tool.name:
                    observation = tool.func(to_input)
                    break

            if (observation):
                self.agent.llm.add_messages(
                    [{"role": "assistant", "content": response}])
                prompt = f"Observation: {observation}"
            else:
                exit()
