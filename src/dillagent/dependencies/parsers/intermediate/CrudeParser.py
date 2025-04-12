from .BaseIntermediateParser import BaseIntermediateParser


class CrudeParser(BaseIntermediateParser):
    def __init__(self, keys):
        super().__init__(keys)

    def parse_values(self, text):
        parsed_values = {}
        for line in text.strip().split('\n'):  # Iterate over each line
            # Split the line by colon, maximum 1 split
            if (':' in line):
                key, value = line.strip().split(':', 1)
                key = key.strip()  # Remove leading and trailing spaces from the key
                value = value.strip()  # Remove leading and trailing spaces from the value
                if key in self.action_keys:
                    parsed_values[key] = value

        # Needs at least 1 action and 1 action input
        if (len(parsed_values) < 2):
            raise KeyError("Couldn't parse Keys in LLM response")

        return parsed_values
