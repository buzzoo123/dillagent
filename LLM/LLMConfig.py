class LLMConfig:
    VALID_TYPES = {'API', 'SCRIPT'}

    def __init__(self, model="local model", api_key="not-needed", config_type='API', path="http://localhost:1234/v1", temperature=0, max_tokens=-1):
        if config_type not in self.VALID_TYPES:
            raise ValueError(
                "Invalid config type. It should be 'api' or 'script'.")
        self.type = config_type
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.path = path
        self.api_key = api_key
        self.model = model
