# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

import fluenttest


sys.path.insert(0, os.path.abspath('.'))

needs_sphinx = '1.0'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]
source_suffix = '.rst'
master_doc = 'index'
project = 'Fluent Test'
copyright = '2013, 2014, Dave Shawley'

# The short X.Y version.
version = fluenttest.__version__
# The full version, including alpha/beta/rc tags.
release = fluenttest.__version__

exclude_patterns = []
pygments_style = 'sphinx'

html_theme = 'nature'
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True

htmlhelp_basename = 'FluentTestdoc'

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
}

latex_documents = [
    ('index', 'FluentTest.tex', 'Fluent Test Documentation',
     'Dave Shawley', 'manual'),
]

texinfo_documents = [
    ('index', 'FluentTest', 'Fluent Test Documentation',
     'Dave Shawley', 'FluentTest', 'One line description of project.',
     'Miscellaneous'),
]

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'mock': ('http://mock.readthedocs.org/en/latest/', None),
}
