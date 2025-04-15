import json
from .BaseIntermediateParser import BaseIntermediateParser

class JsonParser(BaseIntermediateParser):
    def __init__(self, state_keys=None):
        super().__init__(state_keys)

    def parse_values(self, text: str) -> dict:
        # Attempt to extract JSON from within potentially noisy LLM output
        start_pos = text.find('{')
        end_pos = text.rfind('}') + 1
        if start_pos == -1 or end_pos == -1:
            print(f'PARSING ERROR - RAW OUTPUT: {text}')
            raise KeyError("No JSON object found in LLM output.")

        json_blob = text[start_pos:end_pos]

        try:
            parsed = json.loads(json_blob)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON from LLM output.")

        result = parsed

        return result
