# Configuration file for the Sphinx documentation builder.

# -- Path setup --------------------------------------------------------------
import os
import sys
sys.path.insert(0, os.path.abspath('../Documents'))  # Adjust the path as needed

# -- Project information -----------------------------------------------------
project = 'TFM_Sclerosis'
copyright = '2024, Marti'
author = 'Marti'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # For Google and NumPy docstring style support
    'sphinx.ext.viewcode',   # Links to source 
    'sphinx_rtd_theme'       # Add the Read the Docs theme
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

