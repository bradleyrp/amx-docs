
.. title :: Concept

Concept
=======

Automacs is a set of python codes which prepares molecular simulations using common tools, namely `GROMACS <http://www.gromacs.org/>`_ and `CHARMM <http://www.charmm.org/>`_. The purpose of this project is to ensure that simulations are prepared according to a standard method which also bundles simulation data with careful documentation. Automacs (hopefully) makes it possible to generate large simulation datasets with a minimum of description and so-called "manual" labor which invites mistakes and wastes time. Automacs codes are meant to be cloned once for each simulation rather than installed in a central location. This means that each simulation has a copy of the code used to create it.

"Overloaded Python"
-------------------

High-level programming languages often rely on functions which can accept many different kinds of input while producing a consistent result. This is called `overloading <https://en.wikipedia.org/wiki/Function_overloading>`_. The automacs codes are overloaded in two ways. First, simulation data -- files, directories, etc -- for different procedures are organized in a uniform way. These file-naming conventions are described in the :doc:`framework <framework>`. Users who follow these rules can benefit from generic functions that apply to many different simulation types. For example, performing restarts or ensemble changes in GROMACS uses a single generic procedure, regardless of whether you are doing atomistic or coarse-grained simulations. Second, the procedure codes are organized to reflect the consistent naming conventions so that they can be used in as many situations as possible. The simulation-specific settings are separated from the generic, modular steps required to build a simulation so that users can simulate a variety of different systems without rewriting any code. In the next section, we will describe how this separation happens.

.. _concept_procedures:

Procedures
----------

.. ! really only one way ...
.. ! replace all uses of "configuration" with acme.

Automacs executes code in an extremely straightforward way: users first request an experiment, and then they run it. After you clone automacs, you can run a simulation with a few simple `make <https://www.gnu.org/software/make/>`_ commands.

.. code-block :: bash
  
  make clean sure
  make prep protein
  make run

.. warning ::

  Change to "go" vs "manual" above. Point to three types of runs in the experiments section.

We always start by cleaning up the data from a previous run --- all useful data should be archived in a completed copy of automacs. The `make prep?` command lists all of the available experiments, which are detected according to instructions in the configuration. An experiment contains information on which script to run (we sometimes call them "procedures"), and how this execution should be customized. In the example above, we choose the "protein" experiment. The `make prep protein` command finds the right script and copies it to ``script.py`` in the root folder. It also collects the customizations and writes them to an experiment file called ``expt.json``, which will be discussed in the next section.

At this point, you could simply run ``python script.py`` and if everything were in order, the simulation would run to completion. In this basic use-case, automacs has simply organized some code for you. In practice, few codes, especially those under active development, run perfectly the first time. To make development easier, and to save a record of everything automacs does, we use ``make run`` to supervise the exection of ``script.py``. We will explain this in detail in the section :ref:`supervised execution <sec_supervised_execution>` below.

Procedure scripts
~~~~~~~~~~~~~~~~~

Procedure scripts are standard python scripts which must only import a single package into the global namespace.

.. code-block :: python

  from amx import *

Using ``import *`` may be somewhat un-Pythonic, however it allows our scripts to read like lab notebooks for running computational experiments, and it generally makes them much more concise. The automacs import scheme does a lot of bookkeeping work for you behind the scenes. It reads the experiment, imports required modules that are attached to your local copy of automacs, and also ensures that all of your codes (functions, classes, etc) have access to a namespace variable called ``state``. The ``state`` variable (along with its partners: ``expt`` and ``settings``, which will be discussed later), effectively solves the problem of passing information between functions. Any function can read or write to the state, which is carefully passed to new codes and written to disk when the simulation is completed.

The most typical script is called ``protein.py`` and generates an atomistic protein-in-water simulation.

.. note that the following path is relative! no @-syntax sugar!

.. literalinclude :: ../../../amx/proteins/protein.py
  :tab-width: 4

As long as your procedure script leads off with ``from amx import *`` or alternately ``import amx``, then the import magic will import the core automacs functions (which also loads GROMACS), any extension modules you request, and distribute the ``state`` to all of them. The remainder of the script is just a sequence of functions that generate new configurations, run inputs, and all the assorted paraphernalia for a typical simulation.

Functions
~~~~~~~~~

The individual functions in an automacs-style procedure typically perform a single, specific task that a user might otherwise perform at the terminal. Some functions can be used to copy files, write topologies, or execute the GROMACS integrator. 

One of the most useful functions is called :any:`minimize() <automacs.minimize>`, which automates the process of performing energy minimization in GROMACS by taking a configuration file (and its topology), generating run inputs and executing the GROMACS integrator (`mdrun <http://manual.gromacs.org/programs/gmx-mdrun.html>`_). 

.. code-block :: python

  def minimize(name,method='steep',top=None):
    """
    Energy minimization procedure.

    Minimize a structure found at `name.gro` with topology 
    specified by the keyword argument `top` (otherwise `name.top`) 
    according to inputs found in input-<method>-in.mdp and ideally 
    prepared with :meth:`write_mdp <amx.automacs.write_mdp>`. 
    Writes output files to `em-<name>-<method>` and writes a 
    final structure to `<name>-minimized.gro`
    """
    gmx('grompp',base='em-%s-%s'%(name,method),
      top=name if not top else re.sub('^(.+)\.top$',r'\1',top),
      structure=name,log='grompp-%s-%s'%(name,method),
      mdp='input-em-%s-in'%method,skip=True)
    tpr = state.here+'em-%s-%s.tpr'%(name,method)
    if not os.path.isfile(tpr):
      raise Exception('cannot find %s'%tpr)
    gmx('mdrun',
      base='em-%s-%s'%(name,method),
      log='mdrun-%s-%s'%(name,method))
    shutil.copyfile(
      state.here+'em-'+'%s-%s.gro'%(name,method),
      state.here+'%s-minimized.gro'%name)

The minimize function has straightforward inputs and outputs, but it also makes use of ``state.here``, which holds the path to the current step in your simulation (note that most simulations only require a single step, whereas multi-step procedures might use a handful of steps). It also expects to find an ``mdp`` file with the appropriate name, and hence implicitly relies on another function called :any:`write_mdp <amx.automacs.write_mdp>` to prepare these files. The docstring should tell you how these functions depend on one another.

.. _sec_supervised_execution:

Supervised execution
~~~~~~~~~~~~~~~~~~~~

Robust simulation procedures can always be run with `python script.py` once they are prepared, however automacs provides a useful "supervision" feature that provides two advantages that are particularly useful for developing code.

1. The shared namespace called `state` is saved to a file called `state.json` when the job is complete. All functions that are imported by automacs are `decorated <https://www.python.org/dev/peps/pep-0318/>`_ with a function that logs its exeuction to the `state.history` variable.
2. Errors are logged to special variables inside of the ``state`` so that user-developers can correct errors and *continue the experiment from the last successful step*. The code makes use of Python's internal syntax parser in order to find the earliest change in your code. This can be particularly useful when you are adding steps to a procedure which is under development, because it means that you don't have to repeat the earlier steps. Even if the procedure script located at `script.py` doesn't change, automacs still knows where to continue execution without repeating itself.
3. In the event that users wish to "chain" together multiple discrete simulation steps, automacs can look back to completed steps (with states saved to e.g. `state_1.json`) in order to access important details about the simulation, including its geometry and composition. Chaining multiple steps requires a "metarun" procedure and uses the alternate `make metarun` command instead of `make run`, but otherwise execution is the same. The no-repetition feature described above in item two also works when chaining steps together.

.. ! link to acme section. "acme section" throughout this document.

The exact control flow is fully specified in the acme section.

What next?
----------

.. warning :: 

  We moved the experiments to its own section BUT IT NEEDS A SEGUE

The remainder of this walkthrough describe the automacs :any:`configuration <configuration>`, the :any:`command-line interface <interface>`, and MOAR. The last part of the documentation, titled :ref:`components <components>` also provides a :ref:`"live" snapshot of the documentation <live_documentation>`.
