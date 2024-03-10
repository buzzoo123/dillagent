from Dependencies.Parsers.Intermediate.IntermediateParser import IntermediateParser
import json


class JsonParser(IntermediateParser):
    def __init__(self, keys, tool_indicator, input_indicator):
        super().__init__(keys, tool_indicator=tool_indicator, input_indicator=input_indicator)

    def parse_values(self, text):
        # Find the start and end positions of the JSON blob
        start_pos = text.find('{')
        end_pos = text.rfind('}') + 1
        if start_pos == -1 or end_pos == -1:
            # JSON blob not found
            raise KeyError("Can't parse keys because JSON blob not detected")

        # Extract the JSON blob from the text
        json_blob = text[start_pos:end_pos]

        # Parse the JSON blob
        try:
            data = json.loads(json_blob)
        except json.JSONDecodeError:
            raise KeyError('Error parsing json blob')  # JSON parsing failed

        # Extract values based on keys
        values = {}
        for key in self.keys:
            if key in data:
                values[key] = data[key]

        return values
