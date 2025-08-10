import json
from genson import SchemaBuilder
from pathlib import Path

def generate_schema(json_data):
    """Generate JSON schema from JSON data using genson."""
    builder = SchemaBuilder()
    builder.add_object(json_data)
    return builder.to_schema()

def extract_schema_paths(schema, current_path=""):
    """Extract all absolute paths from a JSON schema with their properties."""
    paths = []
    
    if not isinstance(schema, dict):
        return paths
    
    schema_type = schema.get("type")
    
    if schema_type == "object" and "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            prop_path = f"{current_path}.{prop_name}" if current_path else prop_name
            
            # Add the current property
            paths.append({
                "path": prop_path,
                "type": prop_schema.get("type", "unknown"),
                "required": prop_name in schema.get("required", []),
                "description": prop_schema.get("description", ""),
                "default": prop_schema.get("default", ""),
                "enum": prop_schema.get("enum", []),
                "format": prop_schema.get("format", ""),
                "example": prop_schema.get("example", ""),
                "minItems": prop_schema.get("minItems", ""),
                "maxItems": prop_schema.get("maxItems", ""),
                "schema": prop_schema
            })
            
            # Recursively extract paths from nested objects
            paths.extend(extract_schema_paths(prop_schema, prop_path))
    
    elif schema_type == "array" and "items" in schema:
        items_schema = schema["items"]
        if items_schema.get("type") == "object":
            # For array items, use [*] notation to indicate array elements
            array_path = f"{current_path}[*]" if current_path else "[*]"
            paths.extend(extract_schema_paths(items_schema, array_path))
    
    return paths

def handle_file(file_path):
    """Load JSON file and generate schema."""
    with open(file_path, "r") as f:
        data = json.load(f)
    schema = generate_schema(data)
    return schema