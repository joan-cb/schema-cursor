"""
Textual TUI application for JSON Schema Builder & Annotator.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button, DataTable, Footer, Header, Input, Label, 
    Select, Static
)

from schema_builder import handle_file, extract_schema_paths
from schema_modification import (
    apply_annotation, validate_annotation, update_paths_with_schema,
    export_schema
)
from navigation import filter_paths_by_level, filter_paths_by_prefix


class AnnotationModal(ModalScreen[Optional[Dict[str, Any]]]):
    """Modal for adding annotations to schema properties."""
    
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, available_paths: List[Dict[str, Any]]) -> None:
        super().__init__()
        self.available_paths = available_paths
        self.path_options = [(path["path"], path["path"]) for path in available_paths]
    
    def compose(self) -> ComposeResult:
        """Compose the annotation modal."""
        annotation_types = [
            ("description", "Description"),
            ("default", "Default Value"), 
            ("example", "Example"),
            ("enum", "Enum (comma-separated)"),
            ("format", "Format"),
            ("minItems", "Min Items"),
            ("maxItems", "Max Items")
        ]
        
        with Container(id="annotation-modal"):
            yield Label("Add Schema Annotation", classes="modal-title")
            
            with Vertical(classes="form-fields"):
                yield Label("Property Path:")
                yield Select(self.path_options, id="path-select", value=Select.BLANK)
                
                yield Label("Annotation Type:")
                yield Select(annotation_types, id="annotation-select", value=Select.BLANK)
                
                yield Label("Value:")
                yield Input(placeholder="Enter annotation value...", id="value-input")
            
            with Horizontal(classes="modal-buttons"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Add Annotation", variant="primary", id="submit")
    
    @on(Button.Pressed, "#cancel")
    def cancel_annotation(self) -> None:
        """Cancel annotation."""
        self.dismiss(None)
    
    @on(Button.Pressed, "#submit")
    def submit_annotation(self) -> None:
        """Submit annotation."""
        path_select = self.query_one("#path-select", Select)
        annotation_select = self.query_one("#annotation-select", Select)
        value_input = self.query_one("#value-input", Input)
        
        if path_select.value == Select.BLANK:
            self.notify("Please select a property path", severity="error")
            return
            
        if annotation_select.value == Select.BLANK:
            self.notify("Please select an annotation type", severity="error")
            return
            
        if not value_input.value.strip():
            self.notify("Please enter a value", severity="error")
            return
        
        # Process value based on annotation type
        value = value_input.value.strip()
        annotation_type = annotation_select.value
        
        if annotation_type == "enum":
            value = [v.strip() for v in value.split(",") if v.strip()]
        elif annotation_type in ["minItems", "maxItems"]:
            try:
                value = int(value)
            except ValueError:
                self.notify("Min/Max items must be a number", severity="error")
                return
        elif annotation_type == "default":
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass  # Keep as string if not valid JSON
        
        result = {
            "path": path_select.value,
            "annotation": annotation_type,
            "value": value
        }
        
        self.dismiss(result)
    
    def action_cancel(self) -> None:
        """Cancel annotation via escape key."""
        self.dismiss(None)


class FilterModal(ModalScreen[Optional[Dict[str, Any]]]):
    """Modal for setting filters."""
    
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, current_level: int = 0, current_prefix: str = "") -> None:
        super().__init__()
        self.current_level = current_level
        self.current_prefix = current_prefix
    
    def compose(self) -> ComposeResult:
        """Compose the filter modal."""
        with Container(id="filter-modal"):
            yield Label("Filter Schema Properties", classes="modal-title")
            
            with Vertical(classes="form-fields"):
                yield Label("Maximum Nesting Level (0 = all levels):")
                yield Input(
                    placeholder="Enter level (0-10)...", 
                    id="level-input",
                    value=str(self.current_level)
                )
                
                yield Label("Path Prefix Filter:")
                yield Input(
                    placeholder="e.g., 'address' or 'user.profile'...", 
                    id="prefix-input",
                    value=self.current_prefix
                )
            
            with Horizontal(classes="modal-buttons"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Apply Filter", variant="primary", id="submit")
    
    @on(Button.Pressed, "#cancel")
    def cancel_filter(self) -> None:
        """Cancel filter."""
        self.dismiss(None)
    
    @on(Button.Pressed, "#submit")
    def submit_filter(self) -> None:
        """Submit filter."""
        level_input = self.query_one("#level-input", Input)
        prefix_input = self.query_one("#prefix-input", Input)
        
        try:
            level = int(level_input.value.strip()) if level_input.value.strip() else 0
        except ValueError:
            self.notify("Level must be a number", severity="error")
            return
        
        if level < 0:
            self.notify("Level must be 0 or greater", severity="error") 
            return
        
        result = {
            "level": level,
            "prefix": prefix_input.value.strip()
        }
        
        self.dismiss(result)
    
    def action_cancel(self) -> None:
        """Cancel filter via escape key."""
        self.dismiss(None)


class SchemaBuilderTUI(App):
    """Main Textual TUI application for JSON Schema Builder."""
    
    CSS = """
    #main-container {
        layout: vertical;
        height: 100%;
    }
    
    #toolbar {
        layout: horizontal;
        height: 3;
        background: $surface;
        border-bottom: solid $primary;
    }
    
    #toolbar Button {
        margin: 0 1;
    }
    
    #content {
        layout: horizontal;
        height: 1fr;
    }
    
    #table-container {
        width: 1fr;
        height: 100%;
        border: solid $primary;
    }
    
    #info-panel {
        width: 30;
        height: 100%;
        background: $surface;
        border-left: solid $primary;
    }
    
    #status-bar {
        height: 1;
        background: $primary;
        color: $text;
        content-align: center middle;
    }
    
    .modal-title {
        text-align: center;
        text-style: bold;
        padding: 1;
        background: $primary;
    }
    
    .form-fields {
        padding: 1;
        height: auto;
    }
    
    .form-fields Label {
        margin: 1 0 0 0;
    }
    
    .form-fields Input, .form-fields Select {
        margin: 0 0 1 0;
    }
    
    .modal-buttons {
        height: auto;
        align: center;
        padding: 1;
    }
    
    .modal-buttons Button {
        margin: 0 1;
    }
    
    #annotation-modal, #filter-modal {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
    }
    """
    
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+s", "save_schema", "Save Schema"),
        ("ctrl+a", "add_annotation", "Add Annotation"), 
        ("ctrl+f", "filter_properties", "Filter"),
        ("ctrl+r", "refresh", "Refresh"),
        ("f1", "help", "Help"),
    ]
    
    TITLE = "JSON Schema Builder & Annotator"
    
    # Reactive variables
    current_schema: reactive[Optional[Dict[str, Any]]] = reactive(None)
    current_paths: reactive[List[Dict[str, Any]]] = reactive([])
    current_filter_level: reactive[int] = reactive(0)
    current_filter_prefix: reactive[str] = reactive("")
    
    def __init__(self, input_file: str, output_file: str = "updated_schema.json"):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.original_schema = None
        self.all_paths = []
    
    def compose(self) -> ComposeResult:
        """Compose the main TUI layout."""
        yield Header()
        
        with Container(id="main-container"):
            with Horizontal(id="toolbar"):
                yield Button("Add Annotation", id="add-annotation", variant="primary")
                yield Button("Filter", id="filter", variant="default")
                yield Button("Clear Filters", id="clear-filters", variant="default")
                yield Button("Save Schema", id="save", variant="success")
                yield Button("Export JSON", id="export", variant="default")
            
            with Horizontal(id="content"):
                with Container(id="table-container"):
                    yield DataTable(id="schema-table", zebra_stripes=True)
                
                with VerticalScroll(id="info-panel"):
                    yield Label("Schema Information", classes="panel-title")
                    yield Static("", id="schema-stats")
                    yield Label("Current Filters", classes="panel-title")  
                    yield Static("None", id="filter-info")
                    yield Label("Instructions", classes="panel-title")
                    yield Static(
                        "• Use toolbar buttons or keyboard shortcuts\n"
                        "• Double-click table rows to edit\n"
                        "• Ctrl+A: Add annotation\n"
                        "• Ctrl+F: Filter properties\n"
                        "• Ctrl+S: Save schema",
                        id="instructions"
                    )
            
            yield Static("Ready", id="status-bar")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Load data when app starts."""
        await self.load_schema_data()
    
    @work
    async def load_schema_data(self) -> None:
        """Load and process the JSON schema data."""
        try:
            self.original_schema = handle_file(self.input_file)
            self.current_schema = self.original_schema.copy()
            self.all_paths = extract_schema_paths(self.original_schema)
            self.current_paths = self.all_paths.copy()
            
            await self.update_table()
            await self.update_info_panel()
            
            self.query_one("#status-bar", Static).update(
                f"Loaded {len(self.all_paths)} properties from {Path(self.input_file).name}"
            )
            
        except Exception as e:
            self.notify(f"Error loading file: {e}", severity="error")
            self.query_one("#status-bar", Static).update("Error loading file")
    
    async def update_table(self) -> None:
        """Update the DataTable with current schema paths."""
        table = self.query_one("#schema-table", DataTable)
        table.clear()
        
        # Add columns
        table.add_columns(
            "Path", "Type", "Required", "Description", "Default", 
            "Example", "Enum", "Format", "MinItems", "MaxItems"
        )
        
        # Add rows
        for path_info in self.current_paths:
            table.add_row(
                path_info["path"],
                path_info["type"], 
                "Yes" if path_info["required"] else "No",
                str(path_info["description"]) if path_info["description"] else "",
                str(path_info["default"]) if path_info["default"] else "",
                str(path_info["example"]) if path_info["example"] else "",
                str(path_info["enum"]) if path_info["enum"] else "",
                str(path_info["format"]) if path_info["format"] else "",
                str(path_info["minItems"]) if path_info["minItems"] else "",
                str(path_info["maxItems"]) if path_info["maxItems"] else "",
                key=path_info["path"]
            )
    
    async def update_info_panel(self) -> None:
        """Update the information panel."""
        stats = self.query_one("#schema-stats", Static)
        filter_info = self.query_one("#filter-info", Static)
        
        # Update stats
        total_props = len(self.all_paths)
        shown_props = len(self.current_paths)
        required_props = sum(1 for p in self.current_paths if p["required"])
        
        stats.update(
            f"Total Properties: {total_props}\n"
            f"Shown: {shown_props}\n"
            f"Required: {required_props}\n"
            f"Optional: {shown_props - required_props}"
        )
        
        # Update filter info
        filters = []
        if self.current_filter_level > 0:
            filters.append(f"Level ≤ {self.current_filter_level}")
        if self.current_filter_prefix:
            filters.append(f"Prefix: {self.current_filter_prefix}")
        
        filter_text = ", ".join(filters) if filters else "None"
        filter_info.update(filter_text)
    
    @on(Button.Pressed, "#add-annotation")
    async def action_add_annotation(self) -> None:
        """Show annotation modal."""
        if not self.current_paths:
            self.notify("No properties available", severity="warning")
            return
        
        result = await self.push_screen_wait(AnnotationModal(self.current_paths))
        if result:
            await self.apply_annotation_to_schema(result)
    
    @on(Button.Pressed, "#filter")
    async def action_filter_properties(self) -> None:
        """Show filter modal."""
        result = await self.push_screen_wait(
            FilterModal(self.current_filter_level, self.current_filter_prefix)
        )
        if result:
            await self.apply_filters(result["level"], result["prefix"])
    
    @on(Button.Pressed, "#clear-filters")
    async def clear_filters(self) -> None:
        """Clear all filters."""
        await self.apply_filters(0, "")
        self.notify("Filters cleared", severity="info")
    
    @on(Button.Pressed, "#save")
    async def action_save_schema(self) -> None:
        """Save the current schema."""
        await self.save_schema_file()
    
    @on(Button.Pressed, "#export")
    async def export_json(self) -> None:
        """Export schema as JSON."""
        # This could open a modal to choose filename or format
        await self.save_schema_file()
        self.notify("Schema exported", severity="success")
    
    async def apply_annotation_to_schema(self, annotation_data: Dict[str, Any]) -> None:
        """Apply annotation to the schema."""
        # Validate annotation
        is_valid, error_msg = validate_annotation(annotation_data, self.all_paths)
        if not is_valid:
            self.notify(f"Validation error: {error_msg}", severity="error")
            return
        
        # Apply annotation
        success, updated_schema, error_msg = apply_annotation(
            self.current_schema, annotation_data
        )
        
        if success:
            self.current_schema = updated_schema
            # Update paths with new schema values
            self.all_paths = update_paths_with_schema(self.all_paths, updated_schema)
            # Reapply current filters
            await self.apply_filters(self.current_filter_level, self.current_filter_prefix)
            self.notify("Annotation added successfully", severity="success")
        else:
            self.notify(f"Failed to add annotation: {error_msg}", severity="error")
    
    async def apply_filters(self, level: int, prefix: str) -> None:
        """Apply filtering to the current paths."""
        self.current_filter_level = level
        self.current_filter_prefix = prefix
        
        # Start with all paths
        filtered_paths = self.all_paths.copy()
        
        # Apply level filter
        if level > 0:
            filtered_paths = filter_paths_by_level(filtered_paths, level)
        
        # Apply prefix filter
        if prefix:
            filtered_paths = filter_paths_by_prefix(filtered_paths, prefix)
        
        self.current_paths = filtered_paths
        await self.update_table()
        await self.update_info_panel()
    
    async def save_schema_file(self) -> None:
        """Save the current schema to file."""
        if export_schema(self.current_schema, self.output_file):
            self.notify(f"Schema saved to {self.output_file}", severity="success")
            self.query_one("#status-bar", Static).update(f"Saved to {self.output_file}")
        else:
            self.notify("Failed to save schema", severity="error")
    
    @on(DataTable.RowSelected)
    async def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the table."""
        if event.row_key:
            # Find the path info for this row
            path_info = next((p for p in self.current_paths if p["path"] == event.row_key), None)
            if path_info:
                # Could show details in info panel or open edit modal
                details = (
                    f"Path: {path_info['path']}\n"
                    f"Type: {path_info['type']}\n"
                    f"Required: {'Yes' if path_info['required'] else 'No'}\n"
                    f"Description: {path_info['description'] or 'None'}"
                )
                # For now, just show a toast
                self.notify(f"Selected: {path_info['path']}", severity="info")
    
    # Action methods for keyboard shortcuts
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    async def action_add_annotation(self) -> None:
        """Add annotation via keyboard shortcut."""
        await self.query_one("#add-annotation", Button).press()
    
    async def action_filter_properties(self) -> None:
        """Filter properties via keyboard shortcut."""
        await self.query_one("#filter", Button).press()
    
    async def action_save_schema(self) -> None:
        """Save schema via keyboard shortcut."""
        await self.query_one("#save", Button).press()
    
    async def action_refresh(self) -> None:
        """Refresh the display."""
        await self.update_table()
        await self.update_info_panel()
        self.notify("Display refreshed", severity="info")
    
    def action_help(self) -> None:
        """Show help information."""
        self.notify(
            "Keyboard shortcuts: Ctrl+A (annotate), Ctrl+F (filter), Ctrl+S (save), Ctrl+Q (quit)",
            severity="info",
            timeout=5
        )


def run_tui_app(input_file: str, output_file: str = "updated_schema.json") -> None:
    """Run the Textual TUI application."""
    app = SchemaBuilderTUI(input_file, output_file)
    app.run()
