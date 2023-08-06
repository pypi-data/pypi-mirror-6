2. Installation and Setup
=========================

We make available pre-built Windows binaries. On other platforms you can
build it from source using distutils. pyRXP is a single extension module
with no other dependencies outside Python itself.

2.1 Installing from PyPI
----------------------------

The easiest way to install pyRXP is by using the package on PyPI:

::

    pip install pyRXP


2.2 Source Code installation
----------------------------

If you'd rather install from source code (available under the GPL), you can
find it as a Mercurial repository on BitBucket:

::

    hg clone https://bitbucket.org/rptlab/pyrxp
    cd pyrxp
    python setup.py install


2.2.1 Post installation tests
-----------------------------

Whichever method you used to get pyRXP installed, you should run the
short test suite to make sure there haven't been any problems.

Cd to the ``test`` directory and run the file ``testRXPbasic.py``.

Running the test program should result in a message like this:

::

    > python testRXPbasic.py
    ........................................
    ............
    52 tests, no failures!


These are basic health checks, which are the minimum required to make
sure that nothing drastic is wrong. This is the very least that you
should do - you should not skip this step!

If you want to be more thorough, there is a much more comprehensive test
suite which tests XML compliance. This is run by a file called
test_xmltestsuite.py, also in the test directory. This depends on a set
of more than 300 tests written by James Clark which you can download in
the form of a zip file from

::

    http://www.reportlab.com/ftp/xmltest.zip

or

::

    ftp://ftp.jclark.com/pub/xml/xmltest.zip

You can simply drop this in the test directory and run the
test_xmltestsuite file which will automatically unpack and use it.


2.3 Windows binary - pyRXP.pyd
------------------------------

ReportLab's FTP server has win32-dlls and amd64-dlls directories,
both of which are sub-divided into Python versions, where you'll find the
suitable pyd file.
So, assuming you use Python 2.7 on a 64-bit Windows machine, the file you
need to download is:

::

    http://www.reportlab.com/ftp/amd64-dlls/2.7/pyRXP.pyd

Download the pyRXP DLL from the ReportLab FTP site. Save the pyRXP.pyd
in the DLLs directory under your Python installation (eg this is the
C:\\Python27\\DLLs directory for a standard Windows installation of
Python 2.7).


2.4 Examples
------------

If you installed pyRXP from source you'll find an ``examples`` directory,
which includes a couple of substantial XML files with
DTDs, a wrapper module called *xmlutils* which provides easy access to
the tuple tree, and a simple benchmarking script, both documented in section 4.

*Note for Windows users:*

If you only installed the DLL, you can download the examples from
::

    http://www.reportlab.com/ftp/pyrxp_examples.zip

