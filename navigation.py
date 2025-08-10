"""Navigation functionality for exploring JSON schema at different levels."""


def filter_paths_by_level(paths, level=0):
    """
    Filter paths by maximum nesting level.
    Level 0 returns all paths, level 1 returns top-level only, etc.
    """
    if level == 0:
        return paths
    
    filtered_paths = []
    for path_info in paths:
        path = path_info["path"]
        
        # Count nesting level
        dot_count = path.count(".")
        array_count = path.count("[*]")
        
        # Each dot or array notation counts as one level
        total_level = dot_count + array_count
        
        # Include paths at or below the specified level
        if total_level < level:
            filtered_paths.append(path_info)
    
    return filtered_paths


def get_top_level_paths(paths):
    """Get only top-level paths (no nesting)."""
    return filter_paths_by_level(paths, level=1)


def filter_paths_by_prefix(paths, prefix):
    """
    Filter paths that start with the given prefix.
    Returns all matching paths and their nested properties.
    """
    if not prefix:
        return paths
    
    filtered_paths = []
    for path_info in paths:
        path = path_info["path"]
        
        # Check if path starts with prefix
        if path.startswith(prefix):
            filtered_paths.append(path_info)
    
    return filtered_paths


def get_available_prefixes(paths):
    """
    Get all available path prefixes for navigation.
    Returns a list of unique prefixes.
    """
    prefixes = set()
    
    for path_info in paths:
        path = path_info["path"]
        
        # Add all possible prefixes
        parts = path.split(".")
        current_prefix = ""
        
        for i, part in enumerate(parts):
            if i == 0:
                current_prefix = part
            else:
                current_prefix += "." + part
            
            # Remove array notation for cleaner prefixes
            clean_prefix = current_prefix.replace("[*]", "")
            if clean_prefix and clean_prefix not in prefixes:
                prefixes.add(clean_prefix)
    
    return sorted(list(prefixes))


def get_nesting_levels(paths):
    """
    Get all available nesting levels in the schema.
    Returns a sorted list of levels.
    """
    levels = set()
    
    for path_info in paths:
        path = path_info["path"]
        
        # Calculate nesting level
        dot_count = path.count(".")
        array_count = path.count("[*]")
        level = dot_count + array_count
        
        levels.add(level)
    
    return sorted(list(levels))


def group_paths_by_parent(paths):
    """
    Group paths by their parent object.
    Returns a dictionary with parent paths as keys.
    """
    groups = {}
    
    for path_info in paths:
        path = path_info["path"]
        
        # Determine parent path
        if "." in path:
            parent = ".".join(path.split(".")[:-1])
        elif "[*]" in path:
            parent = path.split("[*]")[0]
        else:
            parent = "root"
        
        if parent not in groups:
            groups[parent] = []
        
        groups[parent].append(path_info)
    
    return groups


def get_children_paths(paths, parent_path):
    """
    Get direct children of a given parent path.
    """
    children = []
    
    for path_info in paths:
        path = path_info["path"]
        
        # Check if this is a direct child
        if parent_path == "root":
            # Top-level properties
            if "." not in path and "[*]" not in path:
                children.append(path_info)
        else:
            # Check if path starts with parent and has exactly one more level
            if path.startswith(parent_path + "."):
                remaining = path[len(parent_path + "."):]
                if "." not in remaining and "[*]" not in remaining:
                    children.append(path_info)
            elif path.startswith(parent_path + "[*]"):
                remaining = path[len(parent_path + "[*]"):]
                if remaining.startswith("."):
                    remaining = remaining[1:]
                    if "." not in remaining and "[*]" not in remaining:
                        children.append(path_info)
    
    return children


def navigate_to_path(paths, target_path):
    """
    Navigate to a specific path and show its context.
    Returns the target path info and its children.
    """
    target_info = None
    
    # Find the target path
    for path_info in paths:
        if path_info["path"] == target_path:
            target_info = path_info
            break
    
    if not target_info:
        return None, []
    
    # Get children of the target path
    children = get_children_paths(paths, target_path)
    
    return target_info, children


def display_navigation_summary(paths, current_filter=None):
    """Display a summary of navigation options."""
    print("\n" + "-" * 50)
    print("NAVIGATION SUMMARY")
    print("-" * 50)
    
    if current_filter:
        print(f"Current filter: {current_filter}")
    else:
        print("Showing all paths")
    
    levels = get_nesting_levels(paths)
    print(f"Available nesting levels: {levels}")
    
    prefixes = get_available_prefixes(paths)
    if len(prefixes) <= 10:
        print(f"Available prefixes: {', '.join(prefixes)}")
    else:
        print(f"Available prefixes: {', '.join(prefixes[:10])}... ({len(prefixes)} total)")
    
    print(f"Total properties: {len(paths)}")
    print("-" * 50)
