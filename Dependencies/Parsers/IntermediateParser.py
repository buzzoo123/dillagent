class IntermediateParser():
    def __init__(self, key_words):
        self.keys = key_words

    def parse_values(self, text):
        parsed_values = {}
        for line in text.strip().split('\n'):  # Iterate over each line
            # Split the line by colon, maximum 1 split
            key, value = line.strip().split(':', 1)
            key = key.strip()  # Remove leading and trailing spaces from the key
            value = value.strip()  # Remove leading and trailing spaces from the value
            if key in self.keys:
                parsed_values[key] = value
        return parsed_values
