from typing import List
from .BaseSysPrompt import BaseSysPrompt
from ...tools.Tool import Tool


class MultiInputToolsSysPrompt(BaseSysPrompt):
    def __init__(self, header):
        self.header = header
        self.prompt_str = None

    def get_tool_names(self, tools):
        res = ""
        for i in range(len(tools)):
            if i != len(tools)-1:
                res += f"'{tools[i].name}, '"
            else:
                res += f"'{tools[i].name}'"

    def generate_prompt(self, tools: List[Tool]):
        if (len(tools) < 1):
            raise ValueError(
                "Must provide at least 1 valid tool for this type of prompt")
        prompt = f'''{self.header}
        
You have access to the following tools:
        
'''
        for tool in tools:
            prompt += tool.describe_tool() + "\n"

        prompt += f'''Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: {self.get_tool_names(tools)}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Begin! ALWAYS respond with a valid json blob of a single action.

Use tools if necessary. Format is Action:```$JSON_BLOB```then Observation'''

        self.prompt_str = prompt
        return prompt
