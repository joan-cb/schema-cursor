#!/usr/bin/env python3
"""
Main orchestrator for the JSON Schema Builder and Annotation Tool - TUI Only.
"""

import sys
from startup import run_startup_sequence

# Import TUI app
try:
    from tui_app import run_tui_app
    TUI_AVAILABLE = True
except ImportError:
    TUI_AVAILABLE = False


def main():
    """Main entry point for the application."""

    # Check if TUI is available
    if not TUI_AVAILABLE:
        print("❌ Textual library not available.")
        print("Install with: pip install textual")
        return 1
    
    # Run startup sequence to get user choices
    startup_result = run_startup_sequence()
    if not startup_result:
        print("Exiting...")
        return 0
    
    input_file, output_file = startup_result
    
    # Run TUI mode only
    try:
        print("🚀 Starting TUI mode...")
        run_tui_app(input_file, output_file)
        return 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())