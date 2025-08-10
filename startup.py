"""
Startup functionality for JSON Schema Builder & Annotator.
Handles initial user interaction for mode and file selection.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def discover_json_files() -> List[Path]:
    """
    Discover JSON files in the specified directory.

    Returns:
        List of Path objects for JSON files found
    """
    json_path = Path("json")
    
    if not json_path.exists():
        return []
    
    if not json_path.is_dir():
        return []
    
    # Find all .json files
    json_files = list(json_path.glob("*.json"))
    
    # Sort by name for consistent ordering
    return sorted(json_files)


def display_welcome_banner():
    """Display the welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        JSON Schema Builder & Annotator                       ║
║                                                                              ║
║  Build JSON schemas from sample data and annotate them interactively        ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)



def choose_json_file(json_files: List[Path]) -> Optional[Path]:
    """Prompt user to choose a JSON file from the list."""
    if not json_files:
        print("❌ No JSON files found in the 'json' directory.\nPlease add some and try again.")
        sys.exit(1)
        return None

    print(f"\nFound {len(json_files)} JSON file(s):\n")
    for i, f in enumerate(json_files, 1):
        print(f"{i}. {f.name}")

    while True:
        try:
            choice = input(f"\nSelect JSON file (1-{len(json_files)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(json_files):
                return json_files[int(choice) - 1]
            print(f"Invalid choice. Enter a number between 1 and {len(json_files)}.")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled by user.")
            return None



def get_output_filename() -> str:
    """
    Ask user for output filename for the schema.
    
    Returns:
        Output filename with default if empty
    """
    print()
    default_name = "updated_schema.json"
    filename = input(f"Output filename (default: {default_name}): ").strip()
    
    if not filename:
        return default_name
    
    # Ensure .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    return filename


def run_startup_sequence() -> Optional[Tuple[str, str]]:
    """
    Run the complete startup sequence for TUI mode only.
    
    Returns:
        Tuple of (mode='tui', input_file, output_file) or None if cancelled
    """
    display_welcome_banner()
    
    # Discover JSON files
    json_files = discover_json_files()
    
    # Let user choose file
    selected_file = choose_json_file(json_files)
    if not selected_file:
        return None
    

    # Get output filename
    output_file = get_output_filename()
    
    print()
    print(f"Selected:")
    print(f"  📁 Input file: {selected_file}")
    print(f"  🖥️  Interface: TUI (Terminal User Interface)")
    print(f"  💾 Output: {output_file}")
    print()
    
    return str(selected_file), output_file


if __name__ == "__main__":
    # Test the startup sequence
    result = run_startup_sequence()
    if result:
        mode, input_file, output_file = result
        print(f"Ready to run {mode.upper()} mode with {input_file} -> {output_file}")
    else:
        print("Startup cancelled")
