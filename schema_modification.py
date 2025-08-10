"""Schema modification functionality for updating JSON schemas based on user input."""

import copy


def find_schema_property(schema, path):
    """
    Find a property in the schema by its absolute path.
    Returns (parent_schema, property_key) or (None, None) if not found.
    """
    if not path:
        return None, None
    
    parts = path.split(".")
    current_schema = schema
    
    # Navigate through the path
    for i, part in enumerate(parts):
        # Handle array notation [*]
        if "[*]" in part:
            prop_name = part.replace("[*]", "")
            if prop_name and "properties" in current_schema and prop_name in current_schema["properties"]:
                current_schema = current_schema["properties"][prop_name]
            
            # Navigate to array items
            if "items" in current_schema:
                current_schema = current_schema["items"]
            else:
                return None, None
        else:
            # Regular property navigation
            if "properties" in current_schema and part in current_schema["properties"]:
                if i == len(parts) - 1:
                    # Last part - return parent and property key
                    return current_schema["properties"], part
                else:
                    # Navigate deeper
                    current_schema = current_schema["properties"][part]
            else:
                return None, None
    
    return None, None


def update_schema_property(schema, path, annotation_type, value):
    """
    Update a schema property with the given annotation.
    Returns True if successful, False otherwise.
    """
    parent_schema, property_key = find_schema_property(schema, path)
    
    if parent_schema is None or property_key is None:
        return False
    
    # Map lowercase annotation types back to proper JSON Schema property names
    annotation_mapping = {
        "description": "description",
        "default": "default", 
        "example": "example",
        "enum": "enum",
        "format": "format",
        "minitems": "minItems",
        "maxitems": "maxItems"
    }
    
    # Normalize the annotation type and map it back
    normalized_type = str(annotation_type).strip().lower()
    actual_property_name = annotation_mapping.get(normalized_type, annotation_type)
    
    # Update the property with the annotation
    parent_schema[property_key][actual_property_name] = value
    return True


def apply_annotation(schema, annotation_data):
    """
    Apply an annotation to the schema.
    annotation_data should have keys: path, annotation, value
    Returns (success, updated_schema, error_message)
    """
    if not annotation_data:
        return False, schema, "No annotation data provided"
    
    path = annotation_data.get("path")
    annotation_type = annotation_data.get("annotation")
    value = annotation_data.get("value")
    
    if not all([path, annotation_type]):
        return False, schema, "Missing required annotation fields"
    
    # Create a deep copy of the schema to avoid modifying the original
    updated_schema = copy.deepcopy(schema)
    
    # Apply the annotation
    success = update_schema_property(updated_schema, path, annotation_type, value)
    
    if success:
        return True, updated_schema, ""
    else:
        return False, schema, f"Property '{path}' not found in schema"


def validate_annotation(annotation_data, available_paths):
    """
    Validate annotation data before applying it.
    Returns (is_valid, error_message)
    """
    if not annotation_data:
        return False, "No annotation data provided"
    
    path = annotation_data.get("path")
    annotation_type = annotation_data.get("annotation")
    value = annotation_data.get("value")
    
    # Check required fields
    if not path:
        return False, "Path is required"
    
    if not annotation_type:
        return False, "Annotation type is required"
    
    # Normalize annotation_type to lowercase and strip whitespace
    annotation_type = str(annotation_type).strip().lower()
    
    # Check if path exists in available paths
    path_exists = any(p["path"] == path for p in available_paths)
    if not path_exists:
        return False, f"Path '{path}' does not exist in the schema"
    
    # Validate annotation type
    valid_annotations = [
        "description", "default", "example", "enum",
        "format", "minitems", "maxitems"
    ]
    if annotation_type not in valid_annotations:
        return False, f"Invalid annotation type: '{annotation_type}'. Valid types: {valid_annotations}"
    
    # Type-specific validations
    if annotation_type in ["minitems", "maxitems"]:
        if value != "" and not isinstance(value, int):
            return False, f"{annotation_type} must be an integer"
    
    if annotation_type == "enum" and not isinstance(value, list):
        return False, "Enum must be a list of values"
    
    return True, ""


def get_property_schema(schema, path):
    """
    Get the schema definition for a specific property.
    Returns the property schema or None if not found.
    """
    parent_schema, property_key = find_schema_property(schema, path)
    
    if parent_schema and property_key:
        return parent_schema[property_key]
    
    return None


def update_paths_with_schema(paths, updated_schema):
    """
    Update the paths list with values from the updated schema.
    Returns updated paths list.
    """
    updated_paths = []
    
    for path_info in paths:
        path = path_info["path"]
        property_schema = get_property_schema(updated_schema, path)
        
        if property_schema:
            # Update the path info with values from the schema
            updated_path_info = copy.deepcopy(path_info)
            updated_path_info.update({
                "description": property_schema.get("description", ""),
                "default": property_schema.get("default", ""),
                "enum": property_schema.get("enum", []),
                "format": property_schema.get("format", ""),
                "example": property_schema.get("example", ""),
                "minItems": property_schema.get("minItems", ""),
                "maxItems": property_schema.get("maxItems", ""),
                "schema": property_schema
            })
            updated_paths.append(updated_path_info)
        else:
            # Keep original if property not found
            updated_paths.append(path_info)
    
    return updated_paths


def export_schema(schema, filename):
    """
    Export the schema to a JSON file.
    Returns True if successful, False otherwise.
    """
    try:
        import json
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving schema: {e}")
        return False
