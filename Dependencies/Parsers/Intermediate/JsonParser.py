import json

from Dependencies.Parsers.Intermediate.IntermediateParser import IntermediateParser


class JsonParser(IntermediateParser):
    def __init__(self, keys, tool_indicator, input_indicator):
        super().__init__(keys, tool_indicator, input_indicator)

    def parse_values(self, text):
        # Find the start and end positions of the JSON blob
        start_pos = text.find('{')
        end_pos = text.rfind('}') + 1
        if start_pos == -1 or end_pos == -1:
            raise ValueError("JSON blob not found in the provided text.")

        # Extract the JSON blob from the text
        json_blob = text[start_pos:end_pos]

        # Parse the JSON blob
        try:
            data = json.loads(json_blob)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON blob.")

        # Extract values based on keys
        values = {}
        for key in self.keys:
            if key in data:
                value = data[key]
                if isinstance(value, dict):
                    # Convert dictionaries to lists
                    values[key] = value
                elif isinstance(value, list):
                    values[key] = value
                else:
                    # Case 1 & 3: action_input has no key name or a singular key name inside
                    values[key] = value
        print(values)

        return values
