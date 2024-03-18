from dependencies.prompts.Prompt import Prompt

# Needs rework


class StructuredPrompt(Prompt):

    def __init__(self, header, loop_conditions, tool_section=None, footer=None):
        self.header = header
        self.tool_section = tool_section
        self.loop_condition = loop_conditions
        self.footer = footer
