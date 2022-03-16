Installing PyCUTEst
===================

Requirements
------------
PyCUTEst requires the following software to be installed:

* Python 2.7 or Python 3 (http://www.python.org/)
* CUTEst (see below)

Additionally, the following python packages should be installed (these will be installed automatically if using *pip*, see `Installing PyCUTEst using pip`_):

* NumPy 1.11 or higher (http://www.numpy.org/)
* SciPy 0.18 or higher (http://www.scipy.org/)

**Please Note:** Currently PyCUTEst only supports Mac and Linux. For Windows 10 (or later), PyCUTEst can be used through the `Windows Subsystem for Linux <https://docs.microsoft.com/en-us/windows/wsl/>`_, following the Linux installation instructions.

Installing CUTEst on Linux
--------------------------
These instructions do not include installation of the MATLAB interface. You will need to install four packages: `archdefs <https://github.com/ralna/ARCHDefs>`_, `SIFDecode <https://github.com/ralna/SIFDecode>`_, `CUTEst <https://github.com/ralna/CUTEst>`_ and `MASTSIF <https://bitbucket.org/optrove/sif>`_. To keep things simple, install all four packages in the same directory:

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

    $ cd /path/to/cutest/cutest/
    $ ${ARCHDEFS}/install_optrove
    Do you wish to install CUTEst (Y/n)? Y
    Do you require the CUTEst-Matlab interface (y/N)? N
    Select platform: 6 # PC with generic 64-bit processor
    Select operating system: 3 # Linux
    Would you like to review and modify the system commands (y/N)? N
    Select fortran compiler: 6 # GNU gfortran compiler
    Would you like to review and modify the fortran compiler settings (y/N)? N
    Select C compiler: 8 # GCC
    Would you like to review and modify the C compiler settings (y/N)? N
    Would you like to compile SIFDecode (Y/n)? Y
    Would you like to compile CUTEst (Y/n)? Y
    CUTEst may be compiled in (S)ingle or (D)ouble precision or (B)oth.
    Which precision do you require for the installed subset (D/s/b) ? D

And CUTEst should run from here. To test that the installation works, issue the commands:

 .. code-block:: bash

    $ cd $SIFDECODE/src ; make -f $SIFDECODE/makefiles/$MYARCH test
    $ cd $CUTEST/src ; make -f $CUTEST/makefiles/$MYARCH test

**Please Note:** *currently PyCUTEst only supports gfortran and uses the default version on your path (as returned by* :code:`gfortran -v` *). Please ensure this is the same version that you install CUTEst with above otherwise you may experience segmentation faults, this should be the case if you select the generic* :code:`GNU gfortran compiler` *as the fortran compiler in the installer above.*

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

**Please Note:** *you may see warnings such as* :code:`ld: warning: object file (RANGE.o) was built for newer macOS version (11.5) than being linked (10.15)` *when using PyCUTEst on Mac, to suppress these warnings please set the environment variable* :code:`MACOSX_DEPLOYMENT_TARGET` *to your current macOS version (e.g.* :code:`export MACOSX_DEPLOYMENT_TARGET=11.5` *in this example, you can make this permanent by adding it your* :code:`~/.bashrc` *file).*

Installing PyCUTEst using pip
-----------------------------
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

Manual installation of PyCUTEst
-------------------------------
Alternatively, you can download the source code from `Github <https://github.com/jfowkes/pycutest>`_ and unpack as follows:

 .. code-block:: bash

    $ git clone https://github.com/jfowkes/pycutest
    $ cd pycutest

PyCUTEst is written in pure Python and requires no compilation. It can be installed using:

 .. code-block:: bash

    $ pip install .

**Please Note:** *don't forget to set up your cache and associated environment variable (see above).*

To upgrade PyCUTEst to the latest version, navigate to the top-level directory (i.e. the one containing :code:`setup.py`) and re-run the installation using :code:`pip`, as above:

 .. code-block:: bash

    $ git pull
    $ pip install .

Testing
-------
This documentation provides some simple examples of how to run PyCUTEst.

Uninstallation
--------------
You can uninstall PyCUTEst as follows:

 .. code-block:: bash

    $ pip uninstall pycutest
