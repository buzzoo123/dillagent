from ..models.DescribedModel import DescribedModel


class Tool:
    def __init__(self, name, description, schema: DescribedModel, func):
        self.name = name
        self.description = description
        self.schema = schema
        self.func = func

    # Need to potentially reformt as the name confuses llms.
    def describe_tool(self):
        name = f"{self.name}: "
        input_info = "\n\tThe input to this tool should be:\n"
        field_descriptions = self.schema.get_field_descriptions()
        for field, description in field_descriptions.items():
            # field_type = self.schema.__annotations__[field].__name__
            input_info += f"\t{field}: {description}\n"
        return name + self.description + input_info


def tool(name, description, schema):
    def decorator(func):
        return Tool(name, description, schema, func)
    return decorator
