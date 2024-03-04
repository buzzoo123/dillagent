from pydantic import BaseModel, Field
from typing import Dict, Type


class DescribedModel(BaseModel):
    """
    A wrapper class for Pydantic models that includes descriptions for each field.
    """

    @classmethod
    def _describe_fields(cls) -> Dict[str, str]:
        """
        Describe fields of the model.
        """
        descriptions = {}
        for field_name, field in cls.model_fields.items():
            descriptions[field_name] = field.description
        return descriptions

    @classmethod
    def get_field_descriptions(cls) -> Dict[str, str]:
        """
        Get descriptions for each field of the model.
        """
        return cls._describe_fields()

    @classmethod
    def generate_pydantic_model(cls) -> Type[BaseModel]:
        """
        Generate Pydantic model dynamically with descriptions.
        """
        descriptions = cls._describe_fields()
        return_type = type(cls.__name__, (BaseModel,), descriptions)

    @classmethod
    def create(cls, **kwargs):
        """
        Create an instance of the model with the provided data.
        """
        pydantic_model = cls.generate_pydantic_model()
        return pydantic_model(**kwargs)


# Example usage:
#! class UserSchema(DescribedModel):
#!     name: str = Field(..., description="The name of the user")
#!     age: int = Field(..., description="The age of the user")

#! user_data = {
#!     "name": "Alice",
#!     "age": 30
#! }

#! user_model = UserSchema.create(**user_data)
#! print(user_model)

# Accessing descriptions
#! print(UserSchema.get_field_descriptions())
