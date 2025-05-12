import asyncio
from typing import Any, Dict
from .ToolResult import ToolResult
from ..models.DescribedModel import DescribedModel


class Tool:
    def __init__(self, name, description, schema: DescribedModel, func):
        self.name = name
        self.description = description
        self.schema = schema
        self.func = func

    # Need to potentially reformt as the name confuses llms.
    def describe_tool(self):
        """
        The `describe_tool` function generates a description of a tool including its name, description, and
        input information based on field descriptions.
        
        @return The `describe_tool` method returns a string that includes the name of the tool, its
        description, and information about the input fields required by the tool.
        """
        name = f"{self.name}: "
        input_info = "\n\tThe input to this tool should be:\n"
        field_descriptions = self.schema.get_field_descriptions()
        for field, description in field_descriptions.items():
            # field_type = self.schema.__annotations__[field].__name__
            input_info += f"\t{field}: {description}\n"
        return name + self.description + input_info
    
    def schema(self) -> Dict[str, Any]:
        """
        The `schema` function generates a JSON schema based on Pydantic model field definitions.
        
        @return A dictionary representing a JSON schema for the fields in a Pydantic model. The dictionary
        includes the type "object", properties with type and description for each field, and a list of
        required fields.
        """
        properties = {}
        required = []
        field_definitions = self._schema.model_fields  # Access Pydantic's field definitions

        for field_name, field_info in field_definitions.items():
            json_schema = field_info.json_schema()
            properties[field_name] = {
                "type": json_schema.get("type"),
                "description": field_info.description,
            }
            if field_info.is_required():
                required.append(field_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        # create an empty ToolResult, capturing name & args and start_time
        result = ToolResult(tool_name=self.name, arguments=arguments)
        try:
            if asyncio.iscoroutinefunction(self.func):
                output = await self.func(**arguments)
            else:
                output = self.func(**arguments)
            result.mark_complete(output)
        except Exception as e:
            result.mark_failed(e)
        return result

def tool(name, description, schema):
    """
    The function `tool` is a decorator factory that takes in parameters `name`, `description`, and
    `schema` to create a decorator for a function.
    
    @param name The `name` parameter is a string that represents the name of the tool or function being
    decorated.
    @param description The `description` parameter in the `tool` function is a string that describes the
    purpose or functionality of the tool being defined. It provides information about what the tool does
    or how it can be used.
    @param schema The `schema` parameter in the `tool` function is likely used to define the structure
    or format of the data that the decorated function is expected to receive or return. It could specify
    the expected input parameters, return values, or data types. The schema helps in validating the data
    and ensuring that the
    
    @return A decorator function is being returned.
    """
    def decorator(func):
        return Tool(name, description, schema, func)
    return decorator
