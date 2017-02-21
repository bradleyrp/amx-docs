#!/usr/bin/env python 

makefile = """
# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: clean
clean:
	rm -rf $(BUILDDIR)/*

.PHONY: html
html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: dirhtml
dirhtml:
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

.PHONY: singlehtml
singlehtml:
	$(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."
"""

conf_base = """
import sys
import os
import shlex

sys.dont_write_bytecode = True

extensions = ['sphinx.ext.autodoc','numpydoc']

autodoc_docstring_signature = True
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

#---project information
project = u'amx'
html_show_copyright = False
html_show_sphinx = False
author = u'BioPhysCode'
version = ''
release = ''
language = 'en'
today_fmt = '%%Y.%%B.%%d'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False

#---paths for custom themes
html_theme = 'bizstyle-custom'
html_theme_path = ['_static/']
html_title = "AUTOMACS Documentation"
html_short_title = "AMX docs"
html_logo = 'logo.png'
html_static_path = ['_static']
htmlhelp_basename = 'amxdoc'

from sphinx.ext import autodoc

class SimpleDocumenter(autodoc.MethodDocumenter):
  objtype = "simple"
  #---do not add a header to the docstring
  def add_directive_header(self, sig): pass

def setup(app):
    app.add_autodocumenter(SimpleDocumenter)
"""

conf_py = conf_base + '\n'+ r"import sys;sys.path.insert(0,'%s')"
conf_master_py = conf_base + '\n'+ r"%s"

index_rst = """
.. bilayers documentation master file, created by ACME DOCS !!!
   sphinx-quickstart on Sat Jan 14 10:36:25 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

%(name)s extension
============================

The ``%(name)s`` extension is a component of automacs located at ``%(path_rel)s`` and sourced from ``%(git_source)s``.

%(index_toc)s

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

index_master_rst = """

.. title:: automacs

########
AUTOMACS
########

Automacs is a biophysics simulation pipeline designed to help you run 
scalable, reproducible, and extensible simulations using the popular 
`GROMACS <www.gromacs.org>`_ integrator. 
The docuementation :ref:`contents <contents>` below 
describes how the codes work (and how you should use them). 
The :ref:`components <components>` section describes the codes available in **this** copy
of automacs, including an extensions you may have downloaded.

.. _contents:

***********
Walkthrough
***********

The following sections describe how you can interact with the codes, outline the relatively
minimal set of design constraints required for extending the codes to new use cases.

.. include:: concept.rst
.. include:: configuration.rst
.. include:: interface.rst
.. include:: framework.rst
.. include:: equilibration.rst
.. include:: tutorials.rst

.. try: toctree:: :glob: :maxdepth: 1 ... and a list of the top-level rst files if you want them on separate pages

.. _components:

**********
Components
**********

This section catalogs the codes loaded into the current copy of automacs.
It parses the codes according to the local copy of :doc:`config.py <config>`, which configures the
connections to external codes.

%(components)s

******************
Indices and tables
******************

Everything and the kitchen sink can be found in the index. We omit the typical module index because the modules are structured in a somewhat quirky way.

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""