Oct2Py: Python to GNU Octave Bridge
===================================

.. image:: https://badge.fury.io/py/oct2py.png/
    :target: http://badge.fury.io/py/oct2py

.. image:: https://pypip.in/d/oct2py/badge.png
        :target: https://crate.io/packages/oct2py/

.. image:: https://coveralls.io/repos/blink1073/oct2py/badge.png?branch=master
  :target: https://coveralls.io/r/blink1073/oct2py


Oct2Py is a means to seamlessly call M-files and Octave functions from Python.
It manages the Octave session for you, sharing data behind the scenes using
MAT files.  Usage is as simple as:

.. code-block:: python

    >>> oc = oct2py.Oct2Py() 
    >>> x = oc.zeros(3,3)
    >>> print x, x.dtype
    [[ 0.  0.  0.]
     [ 0.  0.  0.]
     [ 0.  0.  0.]] float64
    ...

If you want to run legacy m-files, do not have MATLAB(TM), and do not fully
trust a code translator, this is your library.  


Features
--------

- Supports all Octave datatypes and most Python datatypes and Numpy dtypes.
- Provides OctaveMagic_ for IPython, including inline plotting in notebooks.
- Supports cell arrays and structs with arbitrary nesting.
- Supports sparse matrices.
- Builds methods on the fly linked to Octave commands (e.g. `zeros` above).
- Nargout is automatically inferred by the number of return variables.
- Thread-safety: each Oct2Py object uses an independent Octave session.
- Can be used as a context manager.
- Supports Unicode characters.

.. _OctaveMagic: http://nbviewer.ipython.org/github/blink1073/oct2py/blob/master/example/octavemagic_extension.ipynb?create=1

Installation
------------
You must have GNU Octave installed and in your PATH. On Windows, the easiest
way to get Octave is to use an installer from `Sourceforge <http://sourceforge.net/projects/octave/files/Octave%20Windows%20binaries/>`_.
On Linux, it should be available from your package manager.
Additionally, you must have the Numpy and Scipy libraries installed.

To install Oct2Py, simply:

.. code-block:: bash

    $ pip install oct2py

Or, if you absolutely must:

.. code-block:: bash

    $ easy_install oct2py


Documentation
-------------

Documentation is available online_.

For version information, see `the Revision History <https://github.com/blink1073/oct2py/blob/master/history.rst>`_.

.. _online: http://blink1073.github.io/oct2py/docs/


.. :changelog:

Release History
---------------

1.2.0
++++++++++++++++++
- OctaveMagic is now part of Oct2Py: ``%load_ext oct2py.ipython``
- Enhanced Struct behavior - supports REPL completion and pickling
- Fixed: Oct2Py will install on Python3 when using setup.py

1.1.1 (2013-11-14)
++++++++++++++++++
- Added support for wheels.
- Fixed: Put docs back in the manifest.
- Fixed: Oct2py will install when there is no Octave available.

1.1.0 (2013-10-27)
++++++++++++++++++

- Full support for plotting with no changes to user code
- Support for Nargout = 0
- Overhaul of front end documentation
- Improved test coverage and added badge.
- Supports Python 2 and 3 from a single code base.
- Fixed: Allow help(Oct2Py()) and tab completion on REPL
- Fixed: Allow tab completion for Oct2Py().<TAB> in REPL


1.0.0 (2013-10-4)
+++++++++++++++++

- Support for Python 3.3
- Added logging to Oct2Py class with optional logger keyword
- Added context manager
- Added support for unicode characters
- Improved support for cell array and sparse matrices
- Fixed: Changes to user .m files are now refreshed during a session
- Fixed: Remove popup console window on Windows


0.4.0 (2013-01-05)
++++++++++++++++++

- Singleton elements within a cell array treated as a singleton list
- Added testing on 64 bit architecture
- Fixed:  Incorrect Octave commands give a more sensible error message


0.3.6 (2012-10-08)
++++++++++++++++++

- Default Octave working directory set to same as OS working dir
- Fixed: Plot rending on older Octave versions


0.3.4 (2012-08-17)
++++++++++++++++++

- Improved speed for larger matrices, better handling of singleton dimensions


0.3.0 (2012-06-16)
++++++++++++++++++

- Added Python 3 support
- Added support for numpy object type


0.2.1 (2011-11-25)
++++++++++++++++++

- Added Sphinx documentation


0.1.4 (2011-11-15)
++++++++++++++++++

- Added support for pip


0.1.0 (2011-11-11)
++++++++++++++++++

- Initial Release


