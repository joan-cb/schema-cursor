"""Unit tests for table_display module."""

import pytest
from table_display import (
    format_table_data, render_schema_table, filter_paths_by_level,
    get_top_level_paths, get_paths_by_prefix
)


class TestFormatTableData:
    """Test cases for format_table_data function."""
    
    def test_format_simple_paths(self):
        """Test formatting simple path data."""
        paths = [
            {
                "path": "name",
                "type": "string",
                "description": "User name",
                "default": "",
                "required": True,
                "example": "John",
                "enum": [],
                "format": "",
                "minItems": "",
                "maxItems": ""
            },
            {
                "path": "age",
                "type": "integer", 
                "description": "",
                "default": 0,
                "required": False,
                "example": "",
                "enum": [],
                "format": "",
                "minItems": "",
                "maxItems": ""
            }
        ]
        
        table_data = format_table_data(paths)
        
        assert len(table_data) == 2
        assert table_data[0][0] == "name"  # path
        assert table_data[0][1] == "string"  # type
        assert table_data[0][2] == "User name"  # description
        assert table_data[0][4] == "Yes"  # required
        assert table_data[1][4] == "No"  # required
    
    def test_format_paths_with_enum(self):
        """Test formatting paths with enum values."""
        paths = [
            {
                "path": "status",
                "type": "string",
                "description": "",
                "default": "",
                "required": True,
                "example": "",
                "enum": ["active", "inactive"],
                "format": "",
                "minItems": "",
                "maxItems": ""
            }
        ]
        
        table_data = format_table_data(paths)
        
        assert "['active', 'inactive']" in table_data[0][6]  # enum column
    
    def test_format_empty_paths(self):
        """Test formatting empty paths list."""
        table_data = format_table_data([])
        
        assert table_data == []


class TestRenderSchemaTable:
    """Test cases for render_schema_table function."""
    
    def test_render_table_with_data(self):
        """Test rendering table with path data."""
        paths = [
            {
                "path": "name",
                "type": "string",
                "description": "User name",
                "default": "",
                "required": True,
                "example": "John",
                "enum": [],
                "format": "",
                "minItems": "",
                "maxItems": ""
            }
        ]
        
        table = render_schema_table(paths)
        
        assert isinstance(table, str)
        assert "AbsolutePath" in table
        assert "Type" in table
        assert "name" in table
        assert "string" in table
    
    def test_render_empty_table(self):
        """Test rendering table with no data."""
        table = render_schema_table([])
        
        assert isinstance(table, str)
        assert "AbsolutePath" in table  # Headers should still be present


class TestFilterPathsByLevel:
    """Test cases for filter_paths_by_level function."""
    
    def setup_method(self):
        """Set up test paths."""
        self.paths = [
            {"path": "name", "type": "string"},
            {"path": "user", "type": "object"},
            {"path": "user.email", "type": "string"},
            {"path": "user.profile", "type": "object"},
            {"path": "user.profile.bio", "type": "string"},
            {"path": "items", "type": "array"},
            {"path": "items[*].id", "type": "integer"},
            {"path": "items[*].data", "type": "object"},
            {"path": "items[*].data.value", "type": "string"}
        ]
    
    def test_filter_level_zero(self):
        """Test filtering with level 0 (all paths)."""
        filtered = filter_paths_by_level(self.paths, 0)
        
        assert len(filtered) == len(self.paths)
    
    def test_filter_level_one(self):
        """Test filtering with level 1 (up to 1 level of nesting)."""
        filtered = filter_paths_by_level(self.paths, 1)
        
        filtered_path_names = [p["path"] for p in filtered]
        
        # Should include level 0 and level 1 paths
        assert "name" in filtered_path_names  # level 0
        assert "user" in filtered_path_names  # level 0
        assert "user.email" in filtered_path_names  # level 1 (1 dot)
        assert "user.profile" in filtered_path_names  # level 1 (1 dot)
        assert "items" in filtered_path_names  # level 0
        
        # Should not include level 2+ paths
        assert "user.profile.bio" not in filtered_path_names  # level 2 (2 dots)
        assert "items[*].id" not in filtered_path_names  # level 2 (1 array + 1 dot)
        assert "items[*].data.value" not in filtered_path_names  # level 3
    
    def test_filter_level_two(self):
        """Test filtering with level 2 (up to 2 levels of nesting)."""
        filtered = filter_paths_by_level(self.paths, 2)
        
        filtered_path_names = [p["path"] for p in filtered]
        
        # Should include up to level 2 paths
        assert "name" in filtered_path_names  # level 0
        assert "user" in filtered_path_names  # level 0
        assert "user.email" in filtered_path_names  # level 1 (1 dot)
        assert "user.profile" in filtered_path_names  # level 1 (1 dot)
        assert "user.profile.bio" in filtered_path_names  # level 2 (2 dots)
        assert "items" in filtered_path_names  # level 0
        assert "items[*].id" in filtered_path_names  # level 2 (1 array + 1 dot)
        assert "items[*].data" in filtered_path_names  # level 2 (1 array + 1 dot)
        
        # Should not include level 3+ paths
        assert "items[*].data.value" not in filtered_path_names  # level 3 (1 array + 2 dots)


class TestGetTopLevelPaths:
    """Test cases for get_top_level_paths function."""
    
    def test_get_top_level_paths(self):
        """Test getting top-level paths only."""
        paths = [
            {"path": "name", "type": "string"},
            {"path": "user", "type": "object"},
            {"path": "user.email", "type": "string"},
            {"path": "items[*].id", "type": "integer"}
        ]
        
        top_level = get_top_level_paths(paths)
        
        path_names = [p["path"] for p in top_level]
        assert "name" in path_names
        assert "user" in path_names
        assert "user.email" not in path_names
        assert "items[*].id" not in path_names


class TestGetPathsByPrefix:
    """Test cases for get_paths_by_prefix function."""
    
    def setup_method(self):
        """Set up test paths."""
        self.paths = [
            {"path": "name", "type": "string"},
            {"path": "user", "type": "object"},
            {"path": "user.email", "type": "string"},
            {"path": "user.profile", "type": "object"},
            {"path": "user.profile.bio", "type": "string"},
            {"path": "address", "type": "object"},
            {"path": "address.street", "type": "string"},
            {"path": "address.city", "type": "string"}
        ]
    
    def test_filter_by_prefix_user(self):
        """Test filtering by 'user' prefix."""
        filtered = get_paths_by_prefix(self.paths, "user")
        
        filtered_path_names = [p["path"] for p in filtered]
        
        assert "user" in filtered_path_names
        assert "user.email" in filtered_path_names
        assert "user.profile" in filtered_path_names
        assert "user.profile.bio" in filtered_path_names
        assert "name" not in filtered_path_names
        assert "address" not in filtered_path_names
    
    def test_filter_by_prefix_address(self):
        """Test filtering by 'address' prefix."""
        filtered = get_paths_by_prefix(self.paths, "address")
        
        filtered_path_names = [p["path"] for p in filtered]
        
        assert "address" in filtered_path_names
        assert "address.street" in filtered_path_names
        assert "address.city" in filtered_path_names
        assert "user" not in filtered_path_names
    
    def test_filter_by_empty_prefix(self):
        """Test filtering by empty prefix (should return all)."""
        filtered = get_paths_by_prefix(self.paths, "")
        
        assert len(filtered) == len(self.paths)
    
    def test_filter_by_nonexistent_prefix(self):
        """Test filtering by non-existent prefix."""
        filtered = get_paths_by_prefix(self.paths, "nonexistent")
        
        assert len(filtered) == 0
