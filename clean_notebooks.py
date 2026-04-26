#!/usr/bin/env python3
"""
Jupyter Notebook Cleaner
Removes corrupted widget metadata and repairs notebook formatting issues.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List


def clean_notebook(notebook_path: str) -> bool:
    """
    Clean a single Jupyter notebook by removing/fixing widget metadata.
    
    Args:
        notebook_path: Path to the .ipynb file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        original_size = os.path.getsize(notebook_path)
        
        # Remove problematic widget state if present
        if 'metadata' in notebook:
            if 'widgets' in notebook['metadata']:
                del notebook['metadata']['widgets']
                print(f"  ✓ Removed widget metadata")
            
            # Ensure metadata structure is valid
            if not isinstance(notebook['metadata'], dict):
                notebook['metadata'] = {}
        
        # Clean cell metadata
        if 'cells' in notebook:
            for cell in notebook['cells']:
                if 'metadata' in cell and isinstance(cell['metadata'], dict):
                    # Remove widget-related metadata from cells
                    if 'widgets' in cell['metadata']:
                        del cell['metadata']['widgets']
        
        # Write the cleaned notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        
        new_size = os.path.getsize(notebook_path)
        size_reduction = original_size - new_size
        
        print(f"✓ Cleaned: {notebook_path}")
        print(f"  Size reduced: {original_size:,} → {new_size:,} bytes ({size_reduction:,} bytes removed)")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"✗ JSON decode error in {notebook_path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error cleaning {notebook_path}: {e}")
        return False


def find_notebooks(directory: str = '.') -> List[str]:
    """
    Recursively find all .ipynb files in a directory.
    
    Args:
        directory: Root directory to search
        
    Returns:
        List of notebook file paths
    """
    notebook_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.ipynb'):
                notebook_files.append(os.path.join(root, file))
    return sorted(notebook_files)


def main():
    """Main function to clean all notebooks in the repository."""
    
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = '.'
    
    if not os.path.exists(target_dir):
        print(f"Error: Directory '{target_dir}' not found")
        sys.exit(1)
    
    print("=" * 70)
    print("Jupyter Notebook Cleaner")
    print("=" * 70)
    print(f"\nSearching for notebooks in: {os.path.abspath(target_dir)}\n")
    
    notebooks = find_notebooks(target_dir)
    
    if not notebooks:
        print("No .ipynb files found.")
        sys.exit(0)
    
    print(f"Found {len(notebooks)} notebook(s):\n")
    
    successful = 0
    failed = 0
    
    for notebook in notebooks:
        if clean_notebook(notebook):
            successful += 1
        else:
            failed += 1
        print()    
    
    print("=" * 70)
    print(f"Summary: {successful} cleaned, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())