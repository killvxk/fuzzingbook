#!/usr/bin/env python

import io, os, sys, types, re

from IPython import get_ipython
from IPython.core.interactiveshell import InteractiveShell

import nbformat
from import_notebooks import RE_CODE

# Things to ignore in exported Python code
RE_IGNORE = re.compile(r'^import fuzzingbook_utils$|^get_ipython().*')

# Common header for all code
HEADER = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This code is part of "Generating Software Tests"
# (https://www.fuzzingbook.org/)
# It is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 4.0 International License,
# (https://creativecommons.org/licenses/by-nc-sa/4.0/)

"""

def prefix_code(code, prefix):
    return prefix + code.replace('\n', '\n' + prefix)
    
def print_utf8(s):
    sys.stdout.buffer.write(s.encode('utf-8'))

def export_notebook_code(notebook_name, path=None):
    # notebook_path = import_notebooks.find_notebook(notebook_name, path)
    notebook_path = notebook_name

    # load the notebook
    with io.open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, 4)

    shell = InteractiveShell.instance()

    print_utf8(HEADER)

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            # transform the input to executable Python
            code = shell.input_transformer_manager.transform_cell(cell.source)
            if RE_IGNORE.match(code):
                # Code to ignore - comment out
                print_utf8(prefix_code(code, "# ") + "\n")
            elif RE_CODE.match(code):
                # Export the code as is
                print_utf8(code + "\n")
            else:
                # Run code only if run as main file
                print_utf8('if __name__ == "__main__":\n')
                print_utf8(prefix_code(code, "    ") + "\n")
        else:
            # Anything else
            code = shell.input_transformer_manager.transform_cell(cell.source)
            print_utf8(prefix_code(code, "# ") + "\n")

if __name__ == "__main__":
    for notebook in sys.argv[1:]:
        export_notebook_code(notebook)
