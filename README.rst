====================================================================================================================================
PyCUTEst: A Python interface to the CUTEst Optimization Test Environment |License| |Build Status| |PyPI Version| |Downloads| |Paper|
====================================================================================================================================

PyCUTEst is a Python interface to `CUTEst <https://github.com/ralna/CUTEst>`_, a Fortran package for testing optimization software. It is based on the `interface originally developed for CUTEr <http://fides.fe.uni-lj.si/~arpadb/software-pycuter.html>`_ by `Prof. Arpad Buermen <http://www.fe.uni-lj.si/en/the_faculty/staff/alphabetically/55/>`_.

Full details on how to use PyCUTEst are available in the `documentation <https://jfowkes.github.io/pycutest/>`_, and a brief summary of the package's goals is available in the `PyCUTEst journal article <https://doi.org/10.21105/joss.04377>`_.

Requirements
------------
PyCUTEst requires the following software to be installed:

* Python 3 (http://www.python.org/)
* Python 3 Headers (:code:`apt install python3-dev` on Ubuntu)
* CUTEst (see below)

**Please Note:** Currently PyCUTEst only supports Mac and Linux. For Windows 10 (or later), PyCUTEst can be used through the `Windows Subsystem for Linux <https://docs.microsoft.com/en-us/windows/wsl/>`_, following the Linux installation instructions.

Installing CUTEst on Linux
--------------------------
These instructions do not include installation of the MATLAB interface. You will need to install four packages: archdefs, SIFDecode, CUTEst and MASTSIF. To keep things simple, install all four packages in the same directory:

 .. code-block:: bash

    $ mkdir cutest
    $ cd cutest
    $ git clone https://github.com/ralna/ARCHDefs ./archdefs
    $ git clone https://github.com/ralna/SIFDecode ./sifdecode
    $ git clone https://github.com/ralna/CUTEst ./cutest
    $ git clone https://bitbucket.org/optrove/sif ./mastsif

Note that :code:`mastsif` contains all the test problem definitions and
is therefore quite large. If you're short on space you may want to copy
only the ``*.SIF`` files for the problems you wish to test on.

Next set the following environment variables in your :code:`~/.bashrc` to point to the installation directories used above:

 .. code-block:: bash

    # CUTEst
    export ARCHDEFS=/path/to/cutest/archdefs/
    export SIFDECODE=/path/to/cutest/sifdecode/
    export MASTSIF=/path/to/cutest/mastsif/
    export CUTEST=/path/to/cutest/cutest/
    export MYARCH="pc64.lnx.gfo"

Now we are ready to install CUTEst in double precision (requires :code:`gfortran` and :code:`gcc`):

 .. code-block:: bash

    $ source ~/.bashrc # load above environment variables
    $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/jfowkes/pycutest/master/.install_cutest.sh)"

And CUTEst should run from here. To test that the installation works, issue the commands:

 .. code-block:: bash

    $ cd $SIFDECODE/src ; make -f $SIFDECODE/makefiles/$MYARCH test
    $ cd $CUTEST/src ; make -f $CUTEST/makefiles/$MYARCH test

**Please Note:** *currently PyCUTEst only supports gfortran and uses the default version on your path (as returned by* :code:`gfortran -v` *). Please ensure this is the same version that you install CUTEst with above otherwise you may experience segmentation faults.*

Installing CUTEst on Mac
------------------------
Install CUTEst using Homebrew as detailed below (installing CUTEst manually on Mac is not supported). First it is important to ensure that you have the latest version of Xcode Command Line Tools installed (or the latest version of Xcode), please ensure this is the case by following `this guide <https://mac.install.guide/commandlinetools/index.html>`_. Now install the Homebrew package manager:

 .. code-block:: bash

    $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Then you can easily install CUTEst:

 .. code-block:: bash

    $ brew tap optimizers/cutest
    $ brew install cutest --without-single --with-matlab # if using Matlab interface
    $ brew install mastsif  # if you want all the test problems
    $ for f in "archdefs" "mastsif" "sifdecode" "cutest"; do \
    $   echo ". $(brew --prefix $f)/$f.bashrc" >> ~/.bashrc; \
    $ done

**Anaconda Users:** *please ensure that* :code:`~/.bashrc` *is sourced in your conda environment (you can do this with the command* :code:`source ~/.bashrc` *) otherwise you may encounter errors using PyCUTEst.*

**Please Note:** *you may see warnings such as* :code:`ld: warning: object file (RANGE.o) was built for newer macOS version (11.5) than being linked (10.15)` *. To suppress these warnings please set the environment variable* :code:`MACOSX_DEPLOYMENT_TARGET` *to your current macOS version (e.g.* :code:`export MACOSX_DEPLOYMENT_TARGET=11.5` *in this example, you can make this permanent by adding it to your* :code:`~/.bashrc` *file).*

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
.. |Build Status| image::  https://img.shields.io/github/actions/workflow/status/jfowkes/pycutest/test.yml?branch=master
                  :target: https://github.com/jfowkes/pycutest/actions/workflows/test.yml
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
