"""Command-line interface for the JSON Schema Builder tool."""

import argparse
import sys
from pathlib import Path


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="JSON Schema Builder and Annotation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.json
  %(prog)s input.json --output my_schema.json
  %(prog)s input.json --interactive
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the JSON file to process"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="updated_schema.json",
        help="Output file for the annotated schema (default: updated_schema.json)"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode for schema annotation"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress non-essential output"
    )
    
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format for displaying schema properties (default: table)"
    )
    
    parser.add_argument(
        "--level",
        type=int,
        default=0,
        help="Maximum nesting level to display (0 for all levels)"
    )
    
    parser.add_argument(
        "--prefix",
        help="Filter properties by path prefix"
    )
    
    return parser


def validate_arguments(args):
    """
    Validate command-line arguments.
    Returns (is_valid, error_message)
    """
    # Check if input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        return False, f"Input file does not exist: {args.input_file}"
    
    if not input_path.is_file():
        return False, f"Input path is not a file: {args.input_file}"
    
    # Check if input file is JSON
    if input_path.suffix.lower() not in [".json"]:
        return False, f"Input file must be a JSON file: {args.input_file}"
    
    # Validate level
    if args.level < 0:
        return False, "Level must be 0 or greater"
    
    # Check if output directory is writable
    output_path = Path(args.output)
    output_dir = output_path.parent
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"Cannot create output directory: {e}"
    
    return True, ""


def display_banner():
    """Display the application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        JSON Schema Builder & Annotator                       ║
║                                                                              ║
║  Build JSON schemas from sample data and annotate them interactively        ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def display_help():
    """Display additional help information."""
    help_text = """
USAGE GUIDE:

1. Basic Usage:
   python cli.py sample.json
   
2. Interactive Mode:
   python cli.py sample.json --interactive
   
3. Custom Output:
   python cli.py sample.json --output my_schema.json
   
4. Filtered View:
   python cli.py sample.json --prefix address --level 2

FEATURES:
• Generate JSON schemas from sample JSON files
• Interactive annotation of schema properties
• Navigate through nested structures
• Filter by path prefix or nesting level
• Export annotated schemas

For more information, use --help
    """
    print(help_text)


def parse_arguments():
    """
    Parse and validate command-line arguments.
    Returns parsed arguments or exits on error.
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate arguments
    is_valid, error_message = validate_arguments(args)
    if not is_valid:
        print(f"Error: {error_message}", file=sys.stderr)
        sys.exit(1)
    
    return args


def handle_cli_error(error_message):
    """Handle CLI errors gracefully."""
    print(f"Error: {error_message}", file=sys.stderr)
    sys.exit(1)


def display_completion_message(output_file, interactive_mode=False):
    """Display completion message."""
    if interactive_mode:
        print(f"\n✅ Schema annotation completed!")
        print(f"📄 Updated schema saved to: {output_file}")
        print("🎉 Thank you for using JSON Schema Builder!")
    else:
        print(f"Schema generated and saved to: {output_file}")


def confirm_overwrite(output_file):
    """
    Confirm if user wants to overwrite existing output file.
    Returns True if should proceed, False otherwise.
    """
    output_path = Path(output_file)
    if output_path.exists():
        while True:
            choice = input(f"File '{output_file}' already exists. Overwrite? (y/n): ").strip().lower()
            if choice in ["y", "yes"]:
                return True
            elif choice in ["n", "no"]:
                return False
            print("Please enter 'y' or 'n'.")
    
    return True
