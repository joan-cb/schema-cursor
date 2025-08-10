"""User interaction functionality for schema annotation."""

import json


def prompt_user_for_annotation():
    """Prompt user for key path, annotation type, and value."""
    print("\n" + "-" * 50)
    print("ANNOTATE SCHEMA PROPERTY")
    print("-" * 50)
    
    key_path = input("Enter the absolute path (e.g., 'name', 'address.street'): ").strip()
    if not key_path:
        return None
    
    print("\nAvailable annotation types:")
    annotation_types = [
        "description", "default", "example", "enum", 
        "format", "minItems", "maxItems"
    ]
    
    for i, annotation_type in enumerate(annotation_types, 1):
        print(f"{i}. {annotation_type}")
    
    while True:
        try:
            choice = input(f"\nSelect annotation type (1-{len(annotation_types)}): ").strip()
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(annotation_types):
                    annotation_type = annotation_types[choice_idx]
                    break
            print("Invalid choice. Please try again.")
        except (ValueError, IndexError):
            print("Invalid choice. Please try again.")
    
    value = input(f"Enter value for {annotation_type}: ").strip()
    
    # Handle special value types
    if annotation_type == "enum":
        # Parse comma-separated values for enum
        value = [v.strip() for v in value.split(",") if v.strip()]
    elif annotation_type in ["minItems", "maxItems"]:
        # Convert to integer for numeric constraints
        try:
            value = int(value) if value else ""
        except ValueError:
            print("Warning: Invalid number provided, using empty value.")
            value = ""
    elif annotation_type == "default":
        # Try to parse as JSON for proper data types
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            # Keep as string if not valid JSON
            pass
    
    return {
        "path": key_path,
        "annotation": annotation_type,
        "value": value
    }


def display_menu():
    """Display the main menu options."""
    print("\n" + "=" * 50)
    print("JSON SCHEMA ANNOTATION TOOL")
    print("=" * 50)
    print("1. View schema table")
    print("2. Add annotation to property")
    print("3. Navigate to specific level")
    print("4. Filter by path prefix")
    print("5. Save updated schema")
    print("6. Exit")
    print("=" * 50)


def get_user_choice():
    """Get user menu choice."""
    while True:
        try:
            choice = input("Select an option (1-6): ").strip()
            if choice in ["1", "2", "3", "4", "5", "6"]:
                return int(choice)
            print("Invalid choice. Please enter a number between 1 and 6.")
        except ValueError:
            print("Invalid choice. Please enter a number between 1 and 6.")


def prompt_for_level():
    """Prompt user for nesting level."""
    while True:
        try:
            level = input("Enter maximum nesting level (0 for all levels): ").strip()
            return int(level) if level else 0
        except ValueError:
            print("Invalid input. Please enter a number.")


def prompt_for_prefix():
    """Prompt user for path prefix filter."""
    prefix = input("Enter path prefix (e.g., 'address'): ").strip()
    return prefix


def confirm_save():
    """Confirm if user wants to save the schema."""
    while True:
        choice = input("Save updated schema? (y/n): ").strip().lower()
        if choice in ["y", "yes"]:
            return True
        elif choice in ["n", "no"]:
            return False
        print("Please enter 'y' or 'n'.")


def prompt_for_output_file():
    """Prompt user for output file name."""
    filename = input("Enter output filename (default: updated_schema.json): ").strip()
    return filename if filename else "updated_schema.json"


def display_annotation_result(success, message=""):
    """Display the result of an annotation operation."""
    if success:
        print("\n✅ Annotation added successfully!")
    else:
        print(f"\n❌ Failed to add annotation: {message}")
    
    input("Press Enter to continue...")


def display_navigation_help():
    """Display help for navigation options."""
    print("\n" + "-" * 50)
    print("NAVIGATION HELP")
    print("-" * 50)
    print("• Level 0: Show all properties (default)")
    print("• Level 1: Show top-level properties only")
    print("• Level 2: Show up to 2 levels of nesting")
    print("• And so on...")
    print("-" * 50)


def display_filter_help():
    """Display help for filtering options."""
    print("\n" + "-" * 50)
    print("FILTER HELP")
    print("-" * 50)
    print("• Enter a path prefix to show only matching properties")
    print("• Examples:")
    print("  - 'address' shows 'address', 'address.street', 'address.zip'")
    print("  - 'phoneNumbers' shows all phone number properties")
    print("• Leave empty to show all properties")
    print("-" * 50)
