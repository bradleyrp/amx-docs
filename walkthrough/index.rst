AUTOMACS
========

Automacs is a biophysics simulation pipeline designed to help you run 
scalable, reproducible, and extensible simulations using the popular 
`GROMACS <www.gromacs.org>`_ integrator. 
The docuementation :ref:`contents <contents>` below 
describes how the codes work (and how you should use them). 
The :ref:`components <components>` section describes the codes available in **this** copy
of automacs, including an extensions you may have downloaded.

.. _contents:

Contents
--------

The following sections describe how you can interact with the codes, outline the relatively
minimal set of design constraints required for extending the codes to new use cases.

.. note that the layout prevents us from adding the following toctree to the table of contents on the left. we could make the contents into a separate rst file, however, to get around this limitation

.. include:: concept.rst

.. toctree::
	:glob:
	:maxdepth: 2

	concept
	controller
	framework
	equilibration
	configuration
	tutorials

.. _components:

Components
----------

This section catalogs the codes loaded into the current copy of automacs.
It parses the codes according to the local copy of :doc:`config.py <config>`, which configures the
connections to external codes.

bilayers
~~~~~~~~

.. toctree::
	:glob:
	:maxdepth: 4

	inputs-bilayers/scripts.rst
	inputs-bilayers/experiments.rst
	inputs-bilayers/submodules.rst


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
