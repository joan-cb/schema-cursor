"""Table display functionality for JSON schema properties."""

from tabulate import tabulate


def format_table_data(paths):
    """Format extracted schema paths for table display."""
    table_data = []
    
    for path_info in paths:
        row = [
            path_info["path"],
            path_info["type"],
            path_info["description"],
            str(path_info["default"]) if path_info["default"] else "",
            "Yes" if path_info["required"] else "No",
            str(path_info["example"]) if path_info["example"] else "",
            str(path_info["enum"]) if path_info["enum"] else "",
            path_info["format"],
            str(path_info["minItems"]) if path_info["minItems"] else "",
            str(path_info["maxItems"]) if path_info["maxItems"] else "",
        ]
        table_data.append(row)
    
    return table_data


def render_schema_table(paths):
    """Render schema properties as a formatted table."""
    headers = [
        "AbsolutePath",
        "Type", 
        "Description",
        "Default Value",
        "Required",
        "Example",
        "Enum",
        "Format",
        "MinItems",
        "MaxItems"
    ]
    
    table_data = format_table_data(paths)
    
    return tabulate(table_data, headers=headers, tablefmt="grid")


def display_schema_table(paths):
    """Display the schema table with proper formatting."""
    table = render_schema_table(paths)
    print("\n" + "="*50)
    print("JSON SCHEMA PROPERTIES")
    print("="*50)
    print(table)
    print("="*50 + "\n")


def filter_paths_by_level(paths, level=0):
    """Filter paths by nesting level for navigation."""
    if level == 0:
        return paths
    
    filtered_paths = []
    for path_info in paths:
        path = path_info["path"]
        # Count dots and array notation to determine level
        dot_count = path.count(".")
        array_count = path.count("[*]")
        total_level = dot_count + array_count
        
        if total_level <= level:
            filtered_paths.append(path_info)
    
    return filtered_paths


def get_top_level_paths(paths):
    """Get only top-level paths (no nesting)."""
    top_level = []
    for path_info in paths:
        path = path_info["path"]
        if "." not in path and "[*]" not in path:
            top_level.append(path_info)
    
    return top_level


def get_paths_by_prefix(paths, prefix):
    """Get all paths that start with a given prefix."""
    matching_paths = []
    for path_info in paths:
        if path_info["path"].startswith(prefix):
            matching_paths.append(path_info)
    
    return matching_paths
