import os
from pathlib import Path

IGNORE = {'.venv', '__pycache__', '.git', '.ipynb_checkpoints', 'node_modules'}

def print_tree(directory, prefix="", level=0, max_level=3):
    if level > max_level:
        return
    
    contents = sorted(Path(directory).iterdir(), key=lambda x: (not x.is_dir(), x.name))
    
    for i, path in enumerate(contents):
        if path.name in IGNORE:
            continue
            
        is_last = i == len(contents) - 1
        print(f"{prefix}{'└── ' if is_last else '├── '}{path.name}")
        
        if path.is_dir():
            extension = "    " if is_last else "│   "
            print_tree(path, prefix + extension, level + 1, max_level)

print_tree(".")