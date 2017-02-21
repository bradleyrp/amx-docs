Configuration
=============

Automacs clearly divides experiment parameters from settings required to run the code. The scientific parameters are placed in :ref:`experiment files <customize_experiments>` and are designed to be portable. Software locations, hardware settings, and the precise configuration of your copy of automacs are set in two places: one is specific to GROMACS, and the other configures automacs.

GROMACS configuration
---------------------

Automacs needs to find GROMACS exeuctables at the terminal in order to run your simulations. If you install a single copy of GROMACS for all users, than the default configuration will suffice, but either way, automacs will look for a gromacs configuration file in one of two locations.

Running :any:`make prep <control.prep>` for the first time causes automacs to check for the configuration. If it can't find one, it throws an error and asks you to run the configure script. If you run :any:`make gromacs_config home <cli.gromacs_config>`, it will write the example configuration file to a hidden file in your home directory at ``~/.automacs.py``. 

You can override the global configuration with a local one, written to ``./gromacs_config.py``, by running :any:`make gromacs_config local <cli.gromacs_config>`, or by copying the file to the automacs root directory yourself. 

.. warning ::
	
	finish this

.. _code_config :

Code configuration
------------------

Automacs can use a number of different extension modules which can be easily shared with other users by packaging them in `git repositories <https://git-scm.com/>`_. These codes can be directly added to a copy of automacs using a simple command which manipulates the local ``config.py`` file. This file describes all of paths that automacs uses, so that you are free to store your codes wherever you like. Extensions must be added from git repositories using the :any:`make set <acme.set_config>` utility, which writes ``config.py``.

.. code-block :: bash
  
  make set module ~/path/to/extension.git local/path/to/extension
  make set module source="https://github.com/username/extension" spot="inputs/path/to/extension"

The ``spot`` argument is unconstrained; you can store the codes whereever you like. We prefer to put minor extensions in the ``inputs`` folder, and major extensions directly in the root directory.  

The ``config.py`` file will change as you add modules and interface functions. A local copy of your config.py is rendered :doc:`here <config>`, as part of the :ref:`live documentation <live_documentation>` of this copy of automacs.

.. _finding_experiments :

**Finding experiments** The ``config.py`` describes the rules for finding experiments. Since many extensions may provide many different standalone experiments and test sets, you may have a large list of experiments. Rather than requiring that each experiment has its own file, you can organize multiple experiments into one :doc:`experiment file <customize_experiments>`. Automacs finds these files according to the ``inputs`` item in ``config.py``. This can be a single string with a path to your experiments file, or a list of paths. Any path can contain wildcards. For the most flexibility, you can also set ``inputs`` to ``'@regex^.*?_expts\\.py$'``, where everything after ``@regex`` is a regular expression for matching *any file* in the automacs subtree. In this example, we require all experiment files to be named e.g. ``my_experiment_group_expts.py``.

**Running commands** Another item in the ``config.py`` dictionary is called ``commands``. It provides explicit paths to python scripts containing command-line interface functions described in the :any:`interface <interface>` section.

.. warning ::

	describe the bootstrapping here

.. simulation_source_material :

Simulation source material
--------------------------

Starting simulations often requires starting configurations such as a protein crystal structure or the initial configuration for a polymer or bilayer. These files tend to be large, and should not be packaged alongside code. You can always place them in their own extension module.

Initial setup
-------------

.. warning ::

	delete this section in favor of the bootstrap explanation above

Automacs can natively simulate proteins in water without modification. The ``make prep protein`` routine will run a simulation of any `pdb <http://www.rcsb.org/pdb/home/home.do>`_ file found directly in the ``inputs`` folder.

.. link to protein tutorial

Since automacs contains many different configuration options, a more typical use case requires that users clone automacs along with several extensions. An example script for this is printed below. Note that this script also allows users to host private git repositories with :ref:`starting materials <simulation_source_material>`.

.. literalinclude :: ../code_examples/script-acme-boot.sh
  :tab-width: 4

.. needs config.py section

This script clones a copy of automacs, and generates an initial copy of ``config.py`` with the bare minimum settings. It then uses ``make set`` to add extension modules, and to point the code to two command-line interface modules found in ``amx/cli.py`` and ``inputs/docs/docs.py`` using ``make set commands``. The latter is responsible for compiling this documentation and is written to take advantage of the :any:`makefile interface <interface>`.

Starting simulations often requires starting configurations such as a protein crystal structure or the initial configuration for a polymer or bilayer. These files tend to be large, and should not be packaged alongside code. You can always place them in their own extension module and load them. The example above uses separate repositories for the `MARTINI <http://cgmartini.nl/>`_ topologies and protein structures.

.. live_documentation

Live documentation
------------------

This documentation uses the modules list ``config.py`` to include the automatic documentation of any extension modules alongside this walkthrough. These are listed in the :ref:`components <components>` section below. Some extensions may only include starting structures or raw data, in which case they will be blank. This scheme ensures that adding codes to your copy of automacs will make it easy to read the accompanying documentation. Each copy of the documentation also serves as a "live" snapshot of the available codes.
