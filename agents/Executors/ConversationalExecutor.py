from agents.agents.BaseAgent import BaseAgent
from agents.Executors.BaseAgentExecutor import BaseAgentExecutor
from Dependencies.Parsers.Intermediate.IntermediateParser import IntermediateParser


class ConversationalExecutor(BaseAgentExecutor):
    def __init__(self, agent, intermediate_parser: IntermediateParser):
        super().__init__(agent, intermediate_parser)

    def run(self, prompt):
        #!Line below is for debugging
        # print("\n\n\n", self.agent.llm.messages)
        count = 0
        while True:
            if (count > 10):
                exit("SHIT IS TAKING TOO LONG!")
            count += 1
            response = self.agent.run(prompt).choices[0].message.content
            try:
                parsed = self.im_parser.parse_values(response)
                to_call = parsed[self.im_parser.tool_indicator]
                to_input = parsed[self.im_parser.input_indicator]
                observation = None
                # Eventually replace with something more modular.
                if to_call.upper() == "FINAL ANSWER":
                    #!Line below is for debugging
                    print(self.agent.llm.messages)
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
            except KeyError:
                return response
            except Exception:
                return "Something went wrong... please try again."
