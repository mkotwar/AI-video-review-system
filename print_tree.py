import os

def generate_tree(dir_path, exclude_dirs, prefix=""):
    items = sorted(os.listdir(dir_path))
    items = [item for item in items if item not in exclude_dirs and not item.endswith('.pyc') and not item.startswith('.')]
    
    tree_str = ""
    for index, item in enumerate(items):
        path = os.path.join(dir_path, item)
        is_last = index == (len(items) - 1)
        connector = "└── " if is_last else "├── "
        
        tree_str += f"{prefix}{connector}{item}\n"
        
        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            tree_str += generate_tree(path, exclude_dirs, prefix + extension)
            
    return tree_str

if __name__ == "__main__":
    project_root = r"c:\Mukul K\vinfo1\video-search-engine"
    exclude = {"__pycache__", ".venv", "data", "logs", "node_modules", ".pytest_cache", ".git"}
    
    tree = f"video-search-engine\n{generate_tree(project_root, exclude)}"
    
    output_path = r"C:\Users\Vinfocom\.gemini\antigravity-ide\brain\3fa92d3a-c7d0-4df4-bc3c-6f04d87d134c\file_structure.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Project File Structure\n\n```text\n")
        f.write(tree)
        f.write("```\n")
