====================================================================================================================================
PyCUTEst: A Python interface to the CUTEst Optimization Test Environment |License| |Build Status| |PyPI Version| |Downloads| |Paper|
====================================================================================================================================

PyCUTEst is a Python interface to `CUTEst <https://github.com/ralna/CUTEst>`_, a Fortran package for testing optimization software. It is based on the `interface originally developed for CUTEr <http://fides.fe.uni-lj.si/~arpadb/software-pycuter.html>`_ by `Prof. Arpad Buermen <http://www.fe.uni-lj.si/en/the_faculty/staff/alphabetically/55/>`_.

Full details on how to use PyCUTEst are available in the `documentation <https://jfowkes.github.io/pycutest/>`_, and a brief summary of the package's goals is available in the `PyCUTEst journal article <https://doi.org/10.21105/joss.04377>`_.

Requirements
------------
PyCUTEst requires the following software to be installed:

* Python 3 (http://www.python.org/)
* Python 3 Headers (:code:`apt install python3-dev` on Ubuntu, already included on macOS)
* CUTEst (see below)

**Please Note:** Currently PyCUTEst only supports Mac and Linux. For Windows, PyCUTEst can be used through the `Windows Subsystem for Linux <https://docs.microsoft.com/en-us/windows/wsl/>`_, following the Linux installation instructions.

Installing CUTEst on Linux
--------------------------
Here we detail the new installation approach using the `meson build system <https://mesonbuild.com/>`_, alternative installation approaches (including the traditional installation approach) are described in the `install docs <https://jfowkes.github.io/pycutest/_build/html/install.html#installing-cutest-on-linux>`_.

You will need to install meson (:code:`apt install meson` on Ubuntu) and three packages: `SIFDecode <https://github.com/ralna/SIFDecode>`_, `CUTEst <https://github.com/ralna/CUTEst>`_ and `MASTSIF <https://bitbucket.org/optrove/sif>`_. To keep things simple, clone all three packages into the same directory:

.. code-block:: bash

    $ mkdir cutest
    $ cd cutest
    $ git clone https://github.com/ralna/SIFDecode ./sifdecode
    $ git clone https://github.com/ralna/CUTEst ./cutest
    $ git clone https://bitbucket.org/optrove/sif ./mastsif

Note that :code:`mastsif` contains all the test problem definitions and
is therefore quite large. If you're short on space you may want to copy
only the ``*.SIF`` files for the problems you wish to test on.

First we need to compile and install SIFDecode (requires :code:`gfortran` and :code:`gcc`):

.. code-block:: bash

    $ cd sifdecode
    $ meson setup builddir
    $ meson compile -C builddir
    $ sudo meson install -C builddir

And SIFDecode should run from here. To test that the installation works, issue the command:

.. code-block:: bash

    $ meson test -C builddir

Now we are ready to install CUTEst in double precision (requires :code:`gfortran` and :code:`gcc`):

.. code-block:: bash

    $ cd ../cutest
    $ meson setup builddir -Dmodules=false
    $ meson compile -C builddir
    $ sudo meson install -C builddir

And CUTEst should run from here. To test that the installation works, issue the command:

.. code-block:: bash

    $ meson test -C builddir

Finally set the following environment variable in your :code:`~/.bashrc` to point to the MASTSIF installation directory used above:

.. code-block:: bash

    # CUTEst
    export MASTSIF=/path/to/cutest/mastsif/

It is also possible to install SIFDecode and CUTEst to custom locations using the :code:`--prefix` argument to :code:`meson setup`.
In this case you will also need to set the :code:`SIFDECODE` and :code:`CUTEST` environment variables to the install prefix.

Installing CUTEst on Mac
------------------------
Here we detail the new installation approach using the `meson build system <https://mesonbuild.com/>`_, alternative installation approaches (including the traditional installation approach) are described in the `install docs <https://jfowkes.github.io/pycutest/_build/html/install.html#installing-cutest-on-mac>`_.

First it is important to ensure that you have the latest version of Xcode Command Line Tools installed (or the latest version of Xcode), please ensure this is the case by following `this guide <https://mac.install.guide/commandlinetools/4>`_. Now install the Homebrew package manager:

.. code-block:: bash

    $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Then you can easily install `GCC <https://gcc.gnu.org/>`_ and the `meson build system <https://mesonbuild.com/>`_:

.. code-block:: bash

    $ brew install gcc meson

CUTEst can now be installed using the `meson build system <https://mesonbuild.com/>`_. You will need to install three packages: `SIFDecode <https://github.com/ralna/SIFDecode>`_, `CUTEst <https://github.com/ralna/CUTEst>`_ and `MASTSIF <https://bitbucket.org/optrove/sif>`_. To keep things simple, clone all three packages into the same directory:

.. code-block:: bash

    $ mkdir cutest
    $ cd cutest
    $ git clone https://github.com/ralna/SIFDecode ./sifdecode
    $ git clone https://github.com/ralna/CUTEst ./cutest
    $ git clone https://bitbucket.org/optrove/sif ./mastsif

Note that :code:`mastsif` contains all the test problem definitions and
is therefore quite large. If you're short on space you may want to copy
only the ``*.SIF`` files for the problems you wish to test on.

First we need to compile and install SIFDecode (requires Homebrew :code:`gcc`):

.. code-block:: bash

    $ cd sifdecode
    $ meson setup builddir
    $ meson compile -C builddir
    $ sudo meson install -C builddir

And SIFDecode should run from here. To test that the installation works, issue the command:

.. code-block:: bash

    $ meson test -C builddir

Now we are ready to install CUTEst in double precision (requires Homebrew :code:`gcc`):

.. code-block:: bash

    $ cd ../cutest
    $ meson setup builddir -Dmodules=false
    $ meson compile -C builddir
    $ sudo meson install -C builddir

And CUTEst should run from here. To test that the installation works, issue the command:

.. code-block:: bash

    $ meson test -C builddir

Finally set the following environment variable in your :code:`~/.zshrc` or :code:`~/.bashrc` to point to the MASTSIF installation directory used above:

.. code-block:: bash

    # CUTEst
    export MASTSIF=/path/to/cutest/mastsif/

It is also possible to install SIFDecode and CUTEst to custom locations using the :code:`--prefix` argument to :code:`meson setup`.
In this case you will also need to set the :code:`SIFDECODE` and :code:`CUTEST` environment variables to the install prefix.

**Anaconda Users:** *please ensure that* :code:`~/.zshrc` or :code:`~/.bashrc` *is sourced in your conda environment (you can do this with the command* :code:`source ~/.zshrc` or :code:`source ~/.bashrc` *) otherwise you may encounter errors using PyCUTEst.*

**Please Note:** *you may see warnings such as* :code:`ld: warning: object file (RANGE.o) was built for newer macOS version (15.0) than being linked (14.0)` *. To suppress these warnings please set the environment variable* :code:`MACOSX_DEPLOYMENT_TARGET` *to your current macOS version (e.g.* :code:`export MACOSX_DEPLOYMENT_TARGET=15.0` *in this example, you can make this permanent by adding it to your* :code:`~/.zshrc` or :code:`~/.bashrc` *file).*

Installing PyCUTEst
-------------------
For easy installation, use `pip <http://www.pip-installer.org/>`_:

.. code-block:: bash

    $ pip install pycutest

Note that if an older install of PyCUTEst is present on your system you can use:

.. code-block:: bash

    $ pip install --upgrade pycutest

to upgrade PyCUTEst to the latest version.

You will then need to create a folder which will store all your compiled problems:

.. code-block:: bash

    $ mkdir pycutest_cache

And set an environment variable to tell PyCUTEst about this directory, by adding to your :code:`~/.bashrc` file:

.. code-block:: bash

    export PYCUTEST_CACHE="/path/to/pycutest_cache"

If you do not set this environment variable, then PyCUTEst will create a cache folder of compiled problems inside your current working directory.

Note that you can uninstall PyCUTEst as follows:

.. code-block:: bash

    $ pip uninstall pycutest

Support
-------
Please ask any questions or report problems using GitHub's issue tracker.

Bugs
----
Please report any bugs using GitHub's issue tracker.

Citing
------
To cite PyCUTEst, please use the following reference:

`J. Fowkes, L. Roberts, and Á. Bűrmen, (2022). PyCUTEst: an open source Python package of optimization test problems. Journal of Open Source Software, 7(78), 4377, https://doi.org/10.21105/joss.04377`

In BibTeX, the citation is:

.. code-block::

    @article{PyCUTEst2022,
        doi = {10.21105/joss.04377},
        url = {https://doi.org/10.21105/joss.04377},
        year = {2022},
        publisher = {The Open Journal},
        volume = {7},
        number = {78},
        pages = {4377},
        author = {Jaroslav Fowkes and Lindon Roberts and Árpád Bűrmen},
        title = {PyCUTEst: an open source Python package of optimization test problems},
        journal = {Journal of Open Source Software}
    }

Contributing
------------
We welcome contributions to PyCUTEst, please see :code:`CONTRIBUTING.md`.

License
-------
This package is released under the GNU GPL license.

.. |License| image::  https://img.shields.io/badge/License-GPL%20v3-blue.svg
             :target: https://www.gnu.org/licenses/gpl-3.0
             :alt: GNU GPL v3 License
.. |Build Status| image::  https://img.shields.io/github/actions/workflow/status/jfowkes/pycutest/test_linux.yml?branch=master
                  :target: https://github.com/jfowkes/pycutest/actions/workflows/test_linux.yml
                  :alt: Build status
.. |PyPI Version| image:: https://img.shields.io/pypi/v/pycutest.svg
                  :target: https://pypi.python.org/pypi/pycutest
                  :alt: PyPI version
.. |Downloads| image:: https://static.pepy.tech/personalized-badge/pycutest?period=total&units=international_system&left_color=black&right_color=green&left_text=Downloads
               :target: https://pepy.tech/project/pycutest
               :alt: Total downloads
.. |Paper| image:: https://joss.theoj.org/papers/10.21105/joss.04377/status.svg
           :target: https://doi.org/10.21105/joss.04377
           :alt: JOSS Paper
