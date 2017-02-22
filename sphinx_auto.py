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

#---variable paths
#---! get these exactly from modules
rst_prolog = '\\n'.join([
	'.. |path_runner| replace:: ../../../runner/',
	])

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

.. title:: amx
.. sectnum::
	:depth: 3



**"Automatic GROMACS"** (a.k.a. AUTOMACS or just **amx** for short) is a biophysics simulation pipeline designed to help you run scalable, reproducible, and extensible simulations using the popular `GROMACS <www.gromacs.org>`_ integrator. The documentation :ref:`walkthrough <contents>` below describes how the codes work (and how you should use them). The :ref:`components <components>` section describes the codes available in **this particular** copy of automacs, including any extensions you may have downloaded.

Everything but the kitchen sink can be found by :ref:`searching <search>` the :ref:`index <genindex>`. Before starting the walkthrough, you must collect additional automacs modules by running the following :any:`setup <cli.setup>` command with the ``all`` recipe. If this is your first time running automacs on a particular computer, you should also :ref:`configure the gromacs paths <gmx_config>` by running :any:`make gromacs_config <cli.gromacs_config>`.

.. code-block :: bash
  
  make gromacs_config local
  make setup all

.. _contents:

The following sections explain how you can interact with the codes and outline the relatively minimal set of design constraints required for extending the codes to new use cases. The :ref:`components <components>` section at the end includes the "live" documentation for your extension modules.

.. include:: concept.rst
.. include:: configuration.rst
.. include:: interface.rst
.. include:: framework.rst

.. try: toctree:: :glob: :maxdepth: 1 ... and a list of the top-level rst files if you want them on separate pages

.. _components:

Components
==========

This section catalogs the codes loaded into the current copy of automacs. It parses the codes according to the local copy of :doc:`config.py <config>`, which configures the connections to external codes.

%(components)s

"""