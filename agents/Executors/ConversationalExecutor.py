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
        reponse = ""
        while True:
            if (count > 10):
                return response
            count += 1
            response = self.agent.run(prompt).choices[0].message.content
            print(response)
            try:
                parsed = self.im_parser.parse_values(response)
                to_call = parsed[self.im_parser.tool_indicator]
                to_input = parsed[self.im_parser.input_indicator]

                if to_call.upper() == "FINAL ANSWER":
                    #!Line below is for debugging
                    print(self.agent.llm.messages)
                    return to_input

                else:
                    prompt = self.use_tool(response, to_call, to_input)

            except KeyError:
                return response
            except Exception as e:
                print(e)
                return response

    def use_tool(self, response, to_call, to_input):
        observation = None
        # Eventually replace with something more modular.
        print(to_input, type(to_input))
        for tool in self.agent.tools:
            if to_call == tool.name:
                if isinstance(to_input, dict):
                    observation = tool.func(**to_input)
                    break
                elif isinstance(to_input, list):
                    print("wtf")
                else:
                    observation = tool.func(to_input)

        print("observation", observation)
        if (observation):
            self.agent.llm.add_messages(
                [{"role": "assistant", "content": response}])
            return f"Observation: {observation}"
        else:
            raise KeyError("No fucking idea why this doesn't work")
