from graphene import Scalar
from graphql.language import ast
import json
from graphene.types.generic import GenericScalar

class JSONScalar(Scalar):
    @staticmethod
    def serialize(value):
        return value  # Return as-is (dict/list)

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return json.loads(node.value)
        return None

    @staticmethod
    def parse_value(value):
        return value
    
JSON = GenericScalar