# -*- coding: utf-8 -*-
import os, pkginfo, datetime

pkg_info = pkginfo.Develop(os.path.join(os.path.dirname(__file__),'..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    ]

intersphinx_mapping = dict(
    python = ('http://docs.python.org/dev', None),
    testfixtures = ('http://pythonhosted.org/testfixtures', None),
    )

# General
source_suffix = '.txt'
master_doc = 'index'
project = pkg_info.name
first_year = 2013
current_year = datetime.datetime.now().year
copyright = (str(current_year) if current_year==first_year else ('%s-%s'%(first_year,current_year)))+' Simplistix Ltd'
version = release = pkg_info.version
exclude_trees = ['_build']
unused_docs = ['description']
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'default'
htmlhelp_basename = project+'doc'

# Options for LaTeX output
latex_documents = [
  ('index',project+'.tex', project+u' Documentation',
   'Simplistix Ltd', 'manual'),
]

