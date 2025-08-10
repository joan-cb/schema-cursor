# """
# Integration tests covering BDD scenarios from feature.feature - TUI Only
# """
# import pytest
# import tempfile
# import json
# import os
# from pathlib import Path
# from unittest.mock import Mock, patch, MagicMock
#
# from main import main
# from startup import run_startup_sequence
# from schema_builder import handle_file, extract_schema_paths
# from schema_modification import apply_annotation, export_schema
# from navigation import filter_paths_by_prefix, filter_paths_by_level
#
#
# class TestTUIIntegration:
#     """Integration tests for TUI mode only."""
#
#     @pytest.fixture
#     def example_json_file(self):
#         """Create the example.json file for testing."""
#         sample_data = {
#             "name": "John",
#             "age": 30,
#             "city": "New York",
#             "isStudent": True,
#             "grades": [85, 90, 95],
#             "address": {
#                 "street": "123 Main St",
#                 "zip": "10001"
#             },
#             "phoneNumbers": [
#                 {"type": "home", "number": "123-456-7890"},
#                 {"type": "work", "number": "098-765-4321"}
#             ]
#         }
#
#         # Create in json directory
#         json_dir = Path("json")
#         json_dir.mkdir(exist_ok=True)
#
#         json_file = json_dir / "example.json"
#         with open(json_file, 'w') as f:
#             json.dump(sample_data, f, indent=2)
#
#         yield str(json_file)
#
#         # Cleanup
#         if json_file.exists():
#             json_file.unlink()
#
