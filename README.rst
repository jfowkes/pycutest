================================================================================================================
PyCUTEst: A Python interface to the CUTEst Optimization Test Environment |License| |Build Status| |PyPI Version|
================================================================================================================

PyCUTEst is a Python interface to `CUTEst <https://github.com/ralna/CUTEst>`_, a Fortran package for testing optimization software. It is based on the `interface originally developed for CUTEr <http://fides.fe.uni-lj.si/~arpadb/software-pycuter.html>`_ by `Prof. Arpad Buermen <http://www.fe.uni-lj.si/en/the_faculty/staff/alphabetically/55/>`_.

Full details on how to use PyCUTEst are available in the `documentation <https://jfowkes.github.io/pycutest/>`_.

Requirements
------------
PyCUTEst requires the following software to be installed:

* Python 2.7 or Python 3 (http://www.python.org/)
* CUTEst (see below)

Additionally, the following python packages should be installed (these will be installed automatically if using *pip*, see `Installation using pip`_):

* NumPy 1.11 or higher (http://www.numpy.org/)
* SciPy 0.18 or higher (http://www.scipy.org/)

**Please Note: ** Currently PyCUTEst only supports Mac and Linux. For Windows 10 users, PyCUTEst can be used through the `Windows Subsystem for Linux <https://docs.microsoft.com/en-us/windows/wsl/faq>`_, following the Linux installation instructions.

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

    $ cd ./cutest
    $ ${ARCHDEFS}/install_optrove
    Do you wish to install GALAHAD (Y/n)? N
    Do you wish to install CUTEst (Y/n)? Y
    Do you require the CUTEst-Matlab interface (y/N)? N
    Select platform: 6 # PC with generic 64-bit processor
    Select operating system: 3 # Linux
    Would you like to review and modify the system commands (y/N)? N
    Select fortran compiler: 5 # GNU gfortran compiler
    Would you like to review and modify the fortran compiler settings (y/N)? N
    Select C compiler: 2 # generic GCC
    Would you like to review and modify the C compiler settings (y/N)? N
    Would you like to compile SIFDecode (Y/n)? Y
    Would you like to compile CUTEst (Y/n)? Y
    CUTEst may be compiled in (S)ingle or (D)ouble precision or (B)oth.
    Which precision do you require for the installed subset (D/s/b) ? D

And CUTEst should run from here. To test that the installation works, issue the commands:

 .. code-block:: bash

    $ cd $SIFDECODE/src ; make -f $SIFDECODE/makefiles/$MYARCH test
    $ cd $CUTEST/src ; make -f $CUTEST/makefiles/$MYARCH test

**Please Note:** *currently PyCUTEst only supports gfortran and uses the default version on your path (as returned by* :code:`gfortran -v` *). Please ensure this is the same version that you install CUTEst with above, this should be the case if you select the generic* :code:`GNU gfortran compiler` *as the fortran compiler in the installer above.*

Installing CUTEst on Mac
------------------------
For simplicity, we recommend installing CUTEst using Homebrew as detailed below (but you can also install CUTEst manually by following the Linux installation instructions above). First it is important to ensure that you have the latest version of Xcode Command Line Tools installed (or the latest version of Xcode), please ensure this is the case by following `this guide <http://railsapps.github.io/xcode-command-line-tools.html>`__. Now install the Homebrew package manager:

 .. code-block:: bash

    $ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

Then you can easily install CUTEst:

 .. code-block:: bash

    $ brew tap optimizers/cutest
    $ brew install cutest --without-single --with-matlab # if using Matlab interface
    $ brew install mastsif  # if you want all the test problems
    $ for f in "archdefs" "mastsif" "sifdecode" "cutest"; do \
    $   echo ". $(brew --prefix $f)/$f.bashrc" >> ~/.bashrc; \
    $ done

Installation using pip
----------------------
For easy installation, use `pip <http://www.pip-installer.org/>`_ as root:

 .. code-block:: bash
 
    $ [sudo] pip install pycutest

or alternatively *easy_install*:

 .. code-block:: bash
 
    $ [sudo] easy_install pycutest

If you do not have root privileges or you want to install PyCUTEst for your private use, you can use:

 .. code-block:: bash
 
    $ pip install --user pycutest

which will install PyCUTEst in your home directory.

Note that if an older install of PyCUTEst is present on your system you can use:

 .. code-block:: bash

    $ [sudo] pip install --upgrade pycutest

to upgrade PyCUTEst to the latest version.

You will then need to create a folder which will store all your compiled problems:

 .. code-block:: bash

    $ mkdir pycutest_cache

And set an environment variable to tell PyCUTEst about this directory, by adding to your :code:`~/.bashrc` file:

 .. code-block:: bash

    export PYCUTEST_CACHE="/path/to/pycutest_cache"
    export PYTHONPATH="${PYCUTEST_CACHE}:${PYTHONPATH}"
    

Manual installation
-------------------
Alternatively, you can download the source code from `Github <https://github.com/jfowkes/pycutest>`_ and unpack as follows:

 .. code-block:: bash

    $ git clone https://github.com/jfowkes/pycutest
    $ cd pycutest

PyCUTEst is written in pure Python and requires no compilation. It can be installed using:

 .. code-block:: bash

    $ [sudo] pip install .

If you do not have root privileges or you want to install PyCUTEst for your private use, you can use:

 .. code-block:: bash

    $ pip install --user .

which will install PyCUTEst in your home directory.

Don't forget to set up your cache and associated environment variable (see above).

To upgrade PyCUTEst to the latest version, navigate to the top-level directory (i.e. the one containing :code:`setup.py`) and rerun the installation using :code:`pip`, as above:

 .. code-block:: bash

    $ git pull
    $ [sudo] pip install .  # with root privileges

Testing
-------
If you installed PyCUTEst manually, you can test your installation by running:

 .. code-block:: bash

    $ python setup.py test

Uninstallation
--------------
If PyCUTEst was installed using *pip* you can uninstall as follows:

 .. code-block:: bash

    $ [sudo] pip uninstall pycutest

otherwise you have to remove the installed files by hand (located in your python site-packages directory).

Bugs
----
Please report any bugs using GitHub's issue tracker.

License
-------
This algorithm is released under the GNU GPL license.

.. |License| image::  https://img.shields.io/badge/License-GPL%20v3-blue.svg
             :target: https://www.gnu.org/licenses/gpl-3.0
             :alt: GNU GPL v3 License
.. |Build Status| image::  https://travis-ci.org/jfowkes/pycutest.svg?branch=master
                  :target: https://travis-ci.org/jfowkes/pycutest
.. |PyPI Version| image:: https://img.shields.io/pypi/v/pycutest.svg
                  :target: https://pypi.python.org/pypi/pycutest
