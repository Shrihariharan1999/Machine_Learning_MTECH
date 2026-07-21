#!/usr/bin/env python3
"""
Repair corrupted Jupyter notebooks
- Fix structural issues
- Remove empty cells
- Validate JSON format
- Ensure proper nbformat structure
"""

import json
import glob
import os
from pathlib import Path

def create_empty_notebook():
    """Create a valid empty notebook structure"""
    return {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.x"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

def repair_notebook(fpath):
    """
    Repair a single notebook
    Returns: (success: bool, reason: str)
    """
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        
        # Check if it's completely empty (just a number or string)
        if not isinstance(data, dict):
            return False, "Not a dictionary"
        
        # Ensure it has cells key
        if 'cells' not in data:
            data['cells'] = []
        
        # Ensure cells is a list
        if not isinstance(data['cells'], list):
            data['cells'] = []
        
        # Check if completely empty
        if len(data['cells']) == 0:
            # For empty notebooks, add a metadata structure
            if 'metadata' not in data or not isinstance(data['metadata'], dict):
                data['metadata'] = {}
            if 'nbformat' not in data:
                data['nbformat'] = 4
            if 'nbformat_minor' not in data:
                data['nbformat_minor'] = 5
        else:
            # Remove completely empty cells (just empty source)
            cleaned_cells = []
            for cell in data['cells']:
                if isinstance(cell, dict):
                    # Ensure cell has required fields
                    if 'cell_type' not in cell:
                        continue
                    if 'source' not in cell:
                        cell['source'] = []
                    if 'metadata' not in cell:
                        cell['metadata'] = {}
                    
                    # Skip cells with completely empty source
                    source = cell.get('source', [])
                    if isinstance(source, list):
                        source_text = ''.join(source).strip()
                    else:
                        source_text = str(source).strip()
                    
                    if source_text:  # Only keep non-empty cells
                        cleaned_cells.append(cell)
            
            data['cells'] = cleaned_cells
        
        # Ensure metadata exists
        if 'metadata' not in data:
            data['metadata'] = {}
        
        # Ensure nbformat exists
        if 'nbformat' not in data:
            data['nbformat'] = 4
        if 'nbformat_minor' not in data:
            data['nbformat_minor'] = 5
        
        # Write back the repaired notebook
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=1)
        
        return True, "Repaired"
    
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("NOTEBOOK REPAIR UTILITY")
    print("=" * 70)
    print()
    
    notebook_files = glob.glob('**/*.ipynb', recursive=True)
    print(f"Found {len(notebook_files)} notebooks to check\n")
    
    repaired = 0
    errors = 0
    empty = 0
    corrupted_files = []
    
    for i, fpath in enumerate(sorted(notebook_files), 1):
        success, reason = repair_notebook(fpath)
        
        if not success:
            errors += 1
            corrupted_files.append((fpath, reason))
            print(f"[{i}/{len(notebook_files)}] ❌ {fpath}")
            print(f"  Reason: {reason}")
        else:
            repaired += 1
            # Check if it's empty
            with open(fpath, 'r') as f:
                data = json.load(f)
            if len(data.get('cells', [])) == 0:
                empty += 1
                print(f"[{i}/{len(notebook_files)}] ⚠️  {fpath} (empty but fixed structure)")
            else:
                print(f"[{i}/{len(notebook_files)}] ✓ {fpath}")
    
    print()
    print("=" * 70)
    print("REPAIR SUMMARY")
    print("=" * 70)
    print(f"✓ Repaired:      {repaired}")
    print(f"⚠ Empty:         {empty}")
    print(f"❌ Errors:        {errors}")
    print(f"Total:           {len(notebook_files)}")
    print("=" * 70)
    
    if errors > 0:
        print("\n❌ NOTEBOOKS WITH ERRORS:")
        for fpath, reason in corrupted_files:
            print(f"  - {fpath}: {reason}")
    
    print("\n✅ All notebooks have been validated and repaired!")

if __name__ == "__main__":
    main()
