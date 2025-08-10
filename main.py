#!/usr/bin/env python3
"""
Main orchestrator for the JSON Schema Builder and Annotation Tool.
"""

import json
import sys
from pathlib import Path

from cli import parse_arguments, display_banner, handle_cli_error, display_completion_message, confirm_overwrite
from schema_builder import handle_file, extract_schema_paths
from table_display import display_schema_table, render_schema_table
from user_interaction import (
    display_menu, get_user_choice, prompt_user_for_annotation,
    display_annotation_result, prompt_for_level, prompt_for_prefix,
    confirm_save, prompt_for_output_file, display_navigation_help,
    display_filter_help
)
from schema_modification import (
    apply_annotation, validate_annotation, update_paths_with_schema,
    export_schema
)
from navigation import (
    filter_paths_by_level, filter_paths_by_prefix,
    display_navigation_summary
)

# Import TUI app (only when needed to avoid import errors if textual not available)
try:
    from tui_app import run_tui_app
    TUI_AVAILABLE = True
except ImportError:
    TUI_AVAILABLE = False


class SchemaAnnotationTool:
    """Main application class for the JSON Schema Annotation Tool."""
    
    def __init__(self, input_file, output_file="updated_schema.json"):
        self.input_file = input_file
        self.output_file = output_file
        self.original_schema = None
        self.current_schema = None
        self.paths = []
        self.current_paths = []
        self.current_filter = None
    
    def load_data(self):
        """Load and process the input JSON file."""
        try:
            self.original_schema = handle_file(self.input_file)
            self.current_schema = self.original_schema.copy()
            self.paths = extract_schema_paths(self.original_schema)
            self.current_paths = self.paths.copy()
            return True
        except FileNotFoundError:
            handle_cli_error(f"File not found: {self.input_file}")
        except json.JSONDecodeError as e:
            handle_cli_error(f"Invalid JSON in file {self.input_file}: {e}")
        except Exception as e:
            handle_cli_error(f"Error processing file {self.input_file}: {e}")
        
        return False
    
    def apply_initial_filters(self, level=0, prefix=None):
        """Apply initial filters based on command-line arguments."""
        self.current_paths = self.paths.copy()
        
        if level > 0:
            self.current_paths = filter_paths_by_level(self.current_paths, level)
            self.current_filter = f"Level <= {level}"
        
        if prefix:
            self.current_paths = filter_paths_by_prefix(self.current_paths, prefix)
            if self.current_filter:
                self.current_filter += f", Prefix: {prefix}"
            else:
                self.current_filter = f"Prefix: {prefix}"
    
    def run_interactive_mode(self):
        """Run the interactive annotation mode."""
        print("\nEntering interactive mode...")
        
        while True:
            display_menu()
            choice = get_user_choice()
            
            if choice == 1:  # View schema table
                display_schema_table(self.current_paths)
                display_navigation_summary(self.current_paths, self.current_filter)
                input("Press Enter to continue...")
            
            elif choice == 2:  # Add annotation
                annotation_data = prompt_user_for_annotation()
                if annotation_data:
                    self._handle_annotation(annotation_data)
            
            elif choice == 3:  # Navigate to level
                display_navigation_help()
                level = prompt_for_level()
                self._apply_level_filter(level)
            
            elif choice == 4:  # Filter by prefix
                display_filter_help()
                prefix = prompt_for_prefix()
                self._apply_prefix_filter(prefix)
            
            elif choice == 5:  # Save schema
                if confirm_save():
                    output_file = prompt_for_output_file()
                    self._save_schema(output_file)
            
            elif choice == 6:  # Exit
                if confirm_save():
                    output_file = prompt_for_output_file()
                    self._save_schema(output_file)
                print("\nGoodbye!")
                break
    
    def _handle_annotation(self, annotation_data):
        """Handle adding an annotation to the schema."""
        # Validate annotation
        is_valid, error_msg = validate_annotation(annotation_data, self.paths)
        if not is_valid:
            display_annotation_result(False, error_msg)
            return
        
        # Apply annotation
        success, updated_schema, error_msg = apply_annotation(
            self.current_schema, annotation_data
        )
        
        if success:
            self.current_schema = updated_schema
            # Update paths with new schema values
            self.paths = update_paths_with_schema(self.paths, updated_schema)
            # Reapply current filters
            self._reapply_filters()
            display_annotation_result(True)
        else:
            display_annotation_result(False, error_msg)
    
    def _apply_level_filter(self, level):
        """Apply level filter to current paths."""
        self.current_paths = filter_paths_by_level(self.paths, level)
        if level > 0:
            self.current_filter = f"Level <= {level}"
        else:
            self.current_filter = None
        
        print(f"\nFiltered to show level <= {level} ({len(self.current_paths)} properties)")
    
    def _apply_prefix_filter(self, prefix):
        """Apply prefix filter to current paths."""
        if prefix:
            self.current_paths = filter_paths_by_prefix(self.paths, prefix)
            self.current_filter = f"Prefix: {prefix}"
            print(f"\nFiltered to show paths starting with '{prefix}' ({len(self.current_paths)} properties)")
        else:
            self.current_paths = self.paths.copy()
            self.current_filter = None
            print(f"\nShowing all paths ({len(self.current_paths)} properties)")
    
    def _reapply_filters(self):
        """Reapply current filters after schema update."""
        if not self.current_filter:
            self.current_paths = self.paths.copy()
        elif "Level" in self.current_filter and "Prefix" in self.current_filter:
            # Both filters applied
            level = int(self.current_filter.split("Level <= ")[1].split(",")[0])
            prefix = self.current_filter.split("Prefix: ")[1]
            self.current_paths = filter_paths_by_level(self.paths, level)
            self.current_paths = filter_paths_by_prefix(self.current_paths, prefix)
        elif "Level" in self.current_filter:
            level = int(self.current_filter.split("Level <= ")[1])
            self.current_paths = filter_paths_by_level(self.paths, level)
        elif "Prefix" in self.current_filter:
            prefix = self.current_filter.split("Prefix: ")[1]
            self.current_paths = filter_paths_by_prefix(self.paths, prefix)
    
    def _save_schema(self, output_file):
        """Save the current schema to file."""
        if export_schema(self.current_schema, output_file):
            print(f"\n✅ Schema saved successfully to: {output_file}")
        else:
            print(f"\n❌ Failed to save schema to: {output_file}")
    
    def run_non_interactive_mode(self, format_type="table"):
        """Run in non-interactive mode (just display and save)."""
        if format_type == "table":
            display_schema_table(self.current_paths)
        else:
            print(json.dumps(self.current_schema, indent=2))
        
        # Save schema
        if confirm_overwrite(self.output_file):
            self._save_schema(self.output_file)


def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Display banner in interactive mode
    if args.interactive and not args.quiet:
        display_banner()
    
    # Create and configure the tool
    tool = SchemaAnnotationTool(args.input_file, args.output)
    
    # Load and process data
    if not tool.load_data():
        return 1
    
    # Apply initial filters
    tool.apply_initial_filters(args.level, args.prefix)
    
    # Run in appropriate mode
    try:
        if args.tui:
            # Run Textual TUI mode
            if not TUI_AVAILABLE:
                handle_cli_error("Textual library not available. Install with: pip install textual")
                return 1
            
            if not args.quiet:
                print("Starting Textual TUI...")
            
            run_tui_app(args.input_file, args.output)
            
        elif args.interactive:
            # Run classic interactive mode
            tool.run_interactive_mode()
        else:
            # Run non-interactive mode
            tool.run_non_interactive_mode(args.format)
        
        if not args.quiet and not args.tui:
            display_completion_message(args.output, args.interactive)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 1
    except Exception as e:
        handle_cli_error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
