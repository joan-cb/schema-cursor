# JSON Schema Builder & Annotator

A command-line tool that generates JSON schemas from sample JSON files and allows interactive annotation of schema properties.

## Features

- **Generate JSON schemas** from sample JSON data using the `genson` library
- **Interactive annotation** of schema properties with descriptions, examples, constraints, etc.
- **Table visualization** of schema properties with all metadata
- **Navigation system** for exploring nested schemas at different levels
- **Filtering capabilities** by path prefix or nesting level
- **Comprehensive testing** with pytest

## Installation

1. Ensure you have Python 3.6+ installed
2. Install dependencies:
   ```bash
   pip install genson tabulate pytest
   ```

## Usage

### Basic Usage

Generate and display a schema:
```bash
python main.py example.json
```

### Interactive Mode

Run in interactive mode for schema annotation:
```bash
python main.py example.json --interactive
```

### Textual TUI Mode

Run with modern Terminal User Interface (recommended):
```bash
python main.py example.json --tui
```

The TUI mode provides:
- Interactive data tables with real-time updates
- Modal forms for easy annotation input
- Keyboard shortcuts and mouse support
- Professional visual layout
- Better navigation and filtering

### Filtering

Filter by path prefix:
```bash
python main.py example.json --prefix address
```

Filter by nesting level:
```bash
python main.py example.json --level 1
```

### Custom Output

Specify output file:
```bash
python main.py example.json --output my_schema.json
```

### All Options

```bash
python main.py --help
```

## Interactive Mode Features

When running in interactive mode (`--interactive`), you can:

1. **View schema table** - Display all properties in a formatted table
2. **Add annotations** - Add descriptions, examples, constraints to properties
3. **Navigate levels** - Filter by nesting depth
4. **Filter by prefix** - Show only properties matching a path prefix
5. **Save schema** - Export the annotated schema to a JSON file

### Available Annotations

- **Description**: Human-readable description of the property
- **Default**: Default value for the property
- **Example**: Example value
- **Enum**: List of allowed values
- **Format**: String format constraint (e.g., "email", "date")
- **MinItems/MaxItems**: Constraints for array properties

## Project Structure

```
schema-cursor/
├── main.py                    # Main application entry point
├── cli.py                     # Command-line interface
├── schema_builder.py          # Schema generation and path extraction
├── table_display.py           # Table rendering and basic filtering
├── user_interaction.py        # Interactive prompting system
├── schema_modification.py     # Schema updating functionality
├── navigation.py              # Advanced navigation and filtering
├── test_*.py                  # Unit tests
├── example.json              # Sample JSON file for testing
└── README.md                 # This file
```

## Testing

Run all tests:
```bash
python -m pytest -v
```

Run specific test file:
```bash
python -m pytest test_schema_builder.py -v
```

## Example Workflow

1. **Generate initial schema**:
   ```bash
   python main.py example.json --interactive
   ```

2. **View the generated table** with all properties and their paths

3. **Add annotations** interactively:
   - Select "Add annotation to property"
   - Enter the absolute path (e.g., `address.street`)
   - Choose annotation type (e.g., description)
   - Enter the value (e.g., "Street address")

4. **Navigate and filter** as needed:
   - Filter by prefix to focus on specific parts
   - Adjust nesting level to manage complexity

5. **Save the annotated schema** to a JSON file

## Sample JSON

The included `example.json` demonstrates various JSON structures:

```json
{
    "name": "John",
    "age": 30,
    "city": "New York", 
    "isStudent": true,
    "grades": [85, 90, 95],
    "address": {
        "street": "123 Main St",
        "zip": "10001"
    },
    "phoneNumbers": [
        {
            "type": "home",
            "number": "123-456-7890"
        }
    ]
}
```

This generates paths like:
- `name` (string)
- `address.street` (nested object property)
- `phoneNumbers[*].type` (array item property)

## Design Principles

The implementation follows these principles:

- **Single Responsibility**: Each function does one thing well
- **Simplicity**: Choose the simplest approach that works
- **Testability**: Every function is unit tested
- **Incremental Development**: Build and test features step by step
- **Clean Code**: Readable, well-documented code

## Contributing

1. Ensure all tests pass: `python -m pytest`
2. Follow the existing code style and conventions
3. Add tests for new functionality
4. Keep functions simple and focused
