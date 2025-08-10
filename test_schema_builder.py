"""Unit tests for schema_builder module."""

import pytest
import json
import tempfile
import os
from pathlib import Path

from schema_builder import generate_schema, extract_schema_paths, handle_file


class TestGenerateSchema:
    """Test cases for generate_schema function."""
    
    def test_generate_schema_simple_object(self):
        """Test schema generation for simple JSON object."""
        data = {
            "name": "John",
            "age": 30,
            "active": True
        }
        
        schema = generate_schema(data)
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "age" in schema["properties"]
        assert "active" in schema["properties"]
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["age"]["type"] == "integer"
        assert schema["properties"]["active"]["type"] == "boolean"
    
    def test_generate_schema_nested_object(self):
        """Test schema generation for nested JSON object."""
        data = {
            "user": {
                "name": "John",
                "address": {
                    "street": "123 Main St",
                    "city": "New York"
                }
            }
        }
        
        schema = generate_schema(data)
        
        assert schema["type"] == "object"
        assert "user" in schema["properties"]
        assert schema["properties"]["user"]["type"] == "object"
        assert "address" in schema["properties"]["user"]["properties"]
        assert schema["properties"]["user"]["properties"]["address"]["type"] == "object"
    
    def test_generate_schema_with_array(self):
        """Test schema generation for JSON with arrays."""
        data = {
            "numbers": [1, 2, 3],
            "items": [
                {"id": 1, "name": "item1"},
                {"id": 2, "name": "item2"}
            ]
        }
        
        schema = generate_schema(data)
        
        assert schema["properties"]["numbers"]["type"] == "array"
        assert schema["properties"]["numbers"]["items"]["type"] == "integer"
        assert schema["properties"]["items"]["type"] == "array"
        assert schema["properties"]["items"]["items"]["type"] == "object"
    
    def test_generate_schema_empty_object(self):
        """Test schema generation for empty JSON object."""
        data = {}
        
        schema = generate_schema(data)
        
        assert schema["type"] == "object"
        # Empty object might not have properties field in genson
        if "properties" in schema:
            assert len(schema["properties"]) == 0


class TestExtractSchemaPaths:
    """Test cases for extract_schema_paths function."""
    
    def test_extract_paths_simple_schema(self):
        """Test path extraction for simple schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        
        paths = extract_schema_paths(schema)
        
        assert len(paths) == 2
        path_names = [p["path"] for p in paths]
        assert "name" in path_names
        assert "age" in path_names
        
        name_path = next(p for p in paths if p["path"] == "name")
        assert name_path["type"] == "string"
        assert name_path["required"] is True
        
        age_path = next(p for p in paths if p["path"] == "age")
        assert age_path["type"] == "integer"
        assert age_path["required"] is False
    
    def test_extract_paths_nested_schema(self):
        """Test path extraction for nested schema."""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"}
                    },
                    "required": ["name"]
                }
            }
        }
        
        paths = extract_schema_paths(schema)
        
        path_names = [p["path"] for p in paths]
        assert "user" in path_names
        assert "user.name" in path_names
        assert "user.email" in path_names
    
    def test_extract_paths_array_schema(self):
        """Test path extraction for schema with arrays."""
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        paths = extract_schema_paths(schema)
        
        path_names = [p["path"] for p in paths]
        assert "items" in path_names
        assert "items[*].id" in path_names
        assert "items[*].name" in path_names
    
    def test_extract_paths_empty_schema(self):
        """Test path extraction for empty schema."""
        schema = {
            "type": "object",
            "properties": {}
        }
        
        paths = extract_schema_paths(schema)
        
        assert len(paths) == 0
    
    def test_extract_paths_invalid_schema(self):
        """Test path extraction with invalid schema input."""
        paths = extract_schema_paths("not a dict")
        assert len(paths) == 0
        
        paths = extract_schema_paths(None)
        assert len(paths) == 0


class TestHandleFile:
    """Test cases for handle_file function."""
    
    def test_handle_file_valid_json(self):
        """Test file handling with valid JSON file."""
        test_data = {
            "name": "test",
            "value": 42
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            schema = handle_file(temp_path)
            
            assert schema["type"] == "object"
            assert "properties" in schema
            assert "name" in schema["properties"]
            assert "value" in schema["properties"]
        finally:
            os.unlink(temp_path)
    
    def test_handle_file_nonexistent(self):
        """Test file handling with non-existent file."""
        with pytest.raises(FileNotFoundError):
            handle_file("nonexistent_file.json")
    
    def test_handle_file_invalid_json(self):
        """Test file handling with invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                handle_file(temp_path)
        finally:
            os.unlink(temp_path)


class TestIntegration:
    """Integration tests for schema_builder module."""
    
    def test_full_workflow_with_example_json(self):
        """Test the complete workflow with example.json."""
        # This test requires example.json to exist
        example_path = Path("json/example.json")  # Fixed path
        if not example_path.exists():
            pytest.skip("example.json not found")
        
        schema = handle_file("json/example.json")  # Fixed path
        paths = extract_schema_paths(schema)
        
        # Verify we got expected paths from example.json
        path_names = [p["path"] for p in paths]
        expected_paths = [
            "name", "age", "city", "isStudent", "grades", "address",
            "address.street", "address.zip", "phoneNumbers",
            "phoneNumbers[*].type", "phoneNumbers[*].number"
        ]
        
        for expected_path in expected_paths:
            assert expected_path in path_names, f"Missing expected path: {expected_path}"
