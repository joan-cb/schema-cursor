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
#     @patch('startup.input', side_effect=['1', ''])  # Select file 1, default output
#     def test_startup_sequence_integration(self, mock_input, example_json_file):
#         """Test the complete startup sequence with user choices."""
#         # Run startup sequence with mocked inputs
#         result = run_startup_sequence()
#
#         # Verify result contains expected values
#         assert result is not None
#         mode, input_file, output_file = result
#
#         assert mode == "tui"
#         assert "example.json" in input_file
#         assert output_file == "updated_schema.json"
#
#     def test_core_api_workflow_integration(self, example_json_file):
#         """Test complete workflow using core API (no CLI/TUI)."""
#         # Load schema directly
#         schema = handle_file(example_json_file)
#         paths = extract_schema_paths(schema)
#
#         # Verify expected paths
#         expected_paths = [
#             "name", "age", "city", "isStudent", "grades", "address",
#             "address.street", "address.zip", "phoneNumbers",
#             "phoneNumbers[*].type", "phoneNumbers[*].number"
#         ]
#
#         path_names = [p["path"] for p in paths]
#         for expected_path in expected_paths:
#             assert expected_path in path_names, f"Missing expected path: {expected_path}"
#
#         # Apply annotations directly
#         annotation_data = {
#             "path": "name",
#             "annotation": "description",
#             "value": "User's full name"
#         }
#
#         success, updated_schema, error_msg = apply_annotation(schema, annotation_data)
#         assert success is True, f"Annotation failed: {error_msg}"
#         assert updated_schema["properties"]["name"]["description"] == "User's full name"
#
#         # Test filtering directly
#         address_paths = filter_paths_by_prefix(paths, "address")
#         assert len(address_paths) < len(paths)
#         for path_info in address_paths:
#             assert path_info["path"].startswith("address")
#
#         # Test saving directly
#         output_file = "test_core_api_output.json"
#         success = export_schema(updated_schema, output_file)
#         assert success is True
#
#         # Verify saved content
#         assert Path(output_file).exists()
#         with open(output_file, 'r') as f:
#             saved_schema = json.load(f)
#         assert saved_schema["properties"]["name"]["description"] == "User's full name"
#
#         # Cleanup
#         Path(output_file).unlink()
#
#     def test_annotation_workflow_integration(self, example_json_file):
#         """Test complete annotation workflow."""
#         # Load schema
#         schema = handle_file(example_json_file)
#         paths = extract_schema_paths(schema)
#
#         # Test multiple annotations
#         annotations = [
#             {"path": "name", "annotation": "description", "value": "User's name"},
#             {"path": "age", "annotation": "example", "value": "25"},
#             {"path": "address.street", "annotation": "format", "value": "address"},
#         ]
#
#         current_schema = schema.copy()
#
#         for annotation_data in annotations:
#             success, updated_schema, error_msg = apply_annotation(current_schema, annotation_data)
#             assert success is True, f"Failed to apply annotation: {error_msg}"
#             current_schema = updated_schema
#
#         # Verify all annotations were applied
#         assert current_schema["properties"]["name"]["description"] == "User's name"
#         assert current_schema["properties"]["age"]["example"] == "25"
#         assert current_schema["properties"]["address"]["properties"]["street"]["format"] == "address"
#
#         # Test export
#         output_file = "test_annotated_schema.json"
#         success = export_schema(current_schema, output_file)
#         assert success is True
#
#         # Verify exported file
#         with open(output_file, 'r') as f:
#             exported_schema = json.load(f)
#
#         assert exported_schema["properties"]["name"]["description"] == "User's name"
#
#         # Cleanup
#         Path(output_file).unlink()
#
#     def test_filtering_workflow_integration(self, example_json_file):
#         """Test complete filtering workflow."""
#         schema = handle_file(example_json_file)
#         paths = extract_schema_paths(schema)
#
#         # Test level filtering
#         level_1_paths = filter_paths_by_level(paths, 1)
#         level_2_paths = filter_paths_by_level(paths, 2)
#
#         assert len(level_1_paths) < len(paths)
#         assert len(level_1_paths) <= len(level_2_paths)
#
#         # Verify level 1 contains only top-level properties
#         for path_info in level_1_paths:
#             assert "." not in path_info["path"] or path_info["path"].count(".") < 1
#
#         # Test prefix filtering
#         address_paths = filter_paths_by_prefix(paths, "address")
#         phone_paths = filter_paths_by_prefix(paths, "phoneNumbers")
#
#         for path_info in address_paths:
#             assert path_info["path"].startswith("address")
#
#         for path_info in phone_paths:
#             assert path_info["path"].startswith("phoneNumbers")
#
#         # Test combined filtering
#         address_level_1 = filter_paths_by_level(address_paths, 1)
#         assert len(address_level_1) <= len(address_paths)
#
#     @patch('tui_app.run_tui_app')
#     @patch('startup.input', side_effect=['1', ''])
#     def test_tui_mode_integration(self, mock_input, mock_tui_app, example_json_file):
#         """Test TUI mode selection and launch."""
#         # Mock TUI app to avoid actual UI launch
#         mock_tui_app.return_value = None
#
#         # Test startup sequence selects TUI
#         result = run_startup_sequence()
#         assert result is not None
#         mode, input_file, output_file = result
#         assert mode == "tui"
#
#         # Test main() would call TUI app
#         with patch('main.run_startup_sequence', return_value=result):
#             with patch('sys.exit'):
#                 try:
#                     main()
#                     # Should have called run_tui_app
#                     mock_tui_app.assert_called_once()
#                 except SystemExit:
#                     pass
#
#     def test_error_handling_integration(self):
#         """Test error handling for various scenarios."""
#         # Test invalid JSON file
#         schema = None
#         try:
#             schema = handle_file("nonexistent.json")
#         except FileNotFoundError:
#             pass  # Expected
#
#         assert schema is None, "Should not load non-existent file"
#
#         # Test export to invalid path
#         schema = {"type": "object", "properties": {"name": {"type": "string"}}}
#         success = export_schema(schema, "/invalid/path/schema.json")
#         assert success is False
#
#     def test_performance_integration(self, example_json_file):
#         """Test performance with larger schemas."""
#         # Create a larger test file
#         large_data = {"users": []}
#
#         # Add 100 users with nested data
#         for i in range(100):
#             large_data["users"].append({
#                 "id": i,
#                 "name": f"User {i}",
#                 "email": f"user{i}@example.com",
#                 "profile": {
#                     "bio": f"Bio for user {i}",
#                     "settings": {
#                         "theme": "dark",
#                         "notifications": True
#                     }
#                 },
#                 "tags": ["tag1", "tag2", "tag3"]
#             })
#
#         # Write to temporary file
#         with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
#             json.dump(large_data, f)
#             large_file = f.name
#
#         try:
#             # Test performance
#             import time
#             start_time = time.time()
#
#             schema = handle_file(large_file)
#             paths = extract_schema_paths(schema)
#
#             load_time = time.time() - start_time
#
#             # Should handle 100+ properties efficiently (< 2 seconds)
#             assert load_time < 2.0
#
#             # Should extract many paths
#             assert len(paths) > 500  # Each user has multiple nested properties
#
#         finally:
#             os.unlink(large_file)
#
#
# # Test for comprehensive coverage
# class TestTUIFeatureComplete:
#     """Test that all TUI features work properly."""
#
#     def test_tui_components_available(self):
#         """Verify TUI components are properly available."""
#         from tui_app import SchemaBuilderTUI, AnnotationModal, FilterModal
#
#         # Test that components can be instantiated
#         app = SchemaBuilderTUI("test.json")
#         assert app is not None
#         assert hasattr(app, 'BINDINGS')
#         assert hasattr(app, 'CSS')
#
#         modal = AnnotationModal([])
#         assert modal is not None
#         assert hasattr(modal, 'BINDINGS')
#
#         filter_modal = FilterModal()
#         assert filter_modal is not None
#         assert hasattr(filter_modal, 'BINDINGS')
#
#
# if __name__ == "__main__":
#     # Run integration tests
#     pytest.main([__file__, "-v"])
