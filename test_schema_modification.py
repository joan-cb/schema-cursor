"""Unit tests for schema_modification module."""

import pytest
import json
import tempfile
import os
from copy import deepcopy

from schema_modification import (
    find_schema_property, update_schema_property, apply_annotation,
    validate_annotation, get_property_schema, update_paths_with_schema,
    export_schema
)


class TestFindSchemaProperty:
    """Test cases for find_schema_property function."""
    
    def setup_method(self):
        """Set up test schema."""
        self.schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "user": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "profile": {
                            "type": "object",
                            "properties": {
                                "bio": {"type": "string"}
                            }
                        }
                    }
                },
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
    
    def test_find_top_level_property(self):
        """Test finding top-level property."""
        parent, key = find_schema_property(self.schema, "name")
        
        assert parent is not None
        assert key == "name"
        assert parent[key]["type"] == "string"
    
    def test_find_nested_property(self):
        """Test finding nested property."""
        parent, key = find_schema_property(self.schema, "user.email")
        
        assert parent is not None
        assert key == "email"
        assert parent[key]["type"] == "string"
    
    def test_find_deeply_nested_property(self):
        """Test finding deeply nested property."""
        parent, key = find_schema_property(self.schema, "user.profile.bio")
        
        assert parent is not None
        assert key == "bio"
        assert parent[key]["type"] == "string"
    
    def test_find_array_item_property(self):
        """Test finding array item property."""
        parent, key = find_schema_property(self.schema, "items[*].id")
        
        assert parent is not None
        assert key == "id"
        assert parent[key]["type"] == "integer"
    
    def test_find_nonexistent_property(self):
        """Test finding non-existent property."""
        parent, key = find_schema_property(self.schema, "nonexistent")
        
        assert parent is None
        assert key is None
    
    def test_find_invalid_nested_property(self):
        """Test finding invalid nested property."""
        parent, key = find_schema_property(self.schema, "name.invalid")
        
        assert parent is None
        assert key is None
    
    def test_find_empty_path(self):
        """Test finding with empty path."""
        parent, key = find_schema_property(self.schema, "")
        
        assert parent is None
        assert key is None


class TestUpdateSchemaProperty:
    """Test cases for update_schema_property function."""
    
    def setup_method(self):
        """Set up test schema."""
        self.schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "user": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"}
                    }
                }
            }
        }
    
    def test_update_property_description(self):
        """Test updating property description."""
        success = update_schema_property(
            self.schema, "name", "description", "User's full name"
        )
        
        assert success is True
        assert self.schema["properties"]["name"]["description"] == "User's full name"
    
    def test_update_nested_property(self):
        """Test updating nested property."""
        success = update_schema_property(
            self.schema, "user.email", "format", "email"
        )
        
        assert success is True
        assert self.schema["properties"]["user"]["properties"]["email"]["format"] == "email"
    
    def test_update_nonexistent_property(self):
        """Test updating non-existent property."""
        success = update_schema_property(
            self.schema, "nonexistent", "description", "test"
        )
        
        assert success is False


class TestApplyAnnotation:
    """Test cases for apply_annotation function."""
    
    def setup_method(self):
        """Set up test schema."""
        self.schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
    
    def test_apply_valid_annotation(self):
        """Test applying valid annotation."""
        annotation = {
            "path": "name",
            "annotation": "description",
            "value": "User's name"
        }
        
        success, updated_schema, error = apply_annotation(self.schema, annotation)
        
        assert success is True
        assert updated_schema["properties"]["name"]["description"] == "User's name"
        assert error == ""
        # Original schema should be unchanged
        assert "description" not in self.schema["properties"]["name"]
    
    def test_apply_annotation_to_nonexistent_path(self):
        """Test applying annotation to non-existent path."""
        annotation = {
            "path": "nonexistent",
            "annotation": "description",
            "value": "test"
        }
        
        success, updated_schema, error = apply_annotation(self.schema, annotation)
        
        assert success is False
        assert updated_schema == self.schema
        assert "not found" in error
    
    def test_apply_annotation_missing_data(self):
        """Test applying annotation with missing data."""
        annotation = {"path": "name"}
        
        success, updated_schema, error = apply_annotation(self.schema, annotation)
        
        assert success is False
        assert "Missing required" in error
    
    def test_apply_annotation_none(self):
        """Test applying None annotation."""
        success, updated_schema, error = apply_annotation(self.schema, None)
        
        assert success is False
        assert "No annotation data" in error


class TestValidateAnnotation:
    """Test cases for validate_annotation function."""
    
    def setup_method(self):
        """Set up test paths."""
        self.paths = [
            {"path": "name", "type": "string"},
            {"path": "age", "type": "integer"},
            {"path": "user.email", "type": "string"}
        ]
    
    def test_validate_valid_annotation(self):
        """Test validating valid annotation."""
        annotation = {
            "path": "name",
            "annotation": "description",
            "value": "User's name"
        }
        
        is_valid, error = validate_annotation(annotation, self.paths)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_missing_path(self):
        """Test validating annotation with missing path."""
        annotation = {
            "annotation": "description",
            "value": "test"
        }
        
        is_valid, error = validate_annotation(annotation, self.paths)
        
        assert is_valid is False
        assert "Path is required" in error
    
    def test_validate_nonexistent_path(self):
        """Test validating annotation with non-existent path."""
        annotation = {
            "path": "nonexistent",
            "annotation": "description",
            "value": "test"
        }
        
        is_valid, error = validate_annotation(annotation, self.paths)
        
        assert is_valid is False
        assert "does not exist" in error
    
    def test_validate_invalid_annotation_type(self):
        """Test validating annotation with invalid type."""
        annotation = {
            "path": "name",
            "annotation": "invalid_type",
            "value": "test"
        }
        
        is_valid, error = validate_annotation(annotation, self.paths)
        
        assert is_valid is False
        assert "Invalid annotation type" in error
    
    def test_validate_invalid_numeric_constraint(self):
        """Test validating annotation with invalid numeric constraint."""
        annotation = {
            "path": "name",
            "annotation": "minItems",
            "value": "not a number"
        }
        
        is_valid, error = validate_annotation(annotation, self.paths)
        
        assert is_valid is False
        assert "must be an integer" in error
    
    def test_validate_invalid_enum(self):
        """Test validating annotation with invalid enum."""
        annotation = {
            "path": "name",
            "annotation": "enum",
            "value": "not a list"
        }
        
        is_valid, error = validate_annotation(annotation, self.paths)
        
        assert is_valid is False
        assert "must be a list" in error


class TestExportSchema:
    """Test cases for export_schema function."""
    
    def test_export_valid_schema(self):
        """Test exporting valid schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "User's name"}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            success = export_schema(schema, temp_path)
            
            assert success is True
            
            # Verify file content
            with open(temp_path, 'r') as f:
                loaded_schema = json.load(f)
            
            assert loaded_schema == schema
        finally:
            os.unlink(temp_path)
    
    def test_export_invalid_path(self):
        """Test exporting to invalid path."""
        schema = {"type": "object"}
        
        success = export_schema(schema, "/invalid/path/schema.json")
        
        assert success is False
