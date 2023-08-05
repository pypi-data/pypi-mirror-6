====================================
Downloading and Installation
====================================

Prerequisites
~~~~~~~~~~~~~~~

The wxmplot package requires Python, wxPython, numpy, and matplotlib.  Some
of the example applications rely on the Image module as well.

As of this writing (November, 2013), wxPython has been demonstrated to run on
Python 3, but support for wxPhoenix and matplotlib WX backend seems poor, and
no testing of wxmplot has been done with wPhoenix or Python 3.

Downloads
~~~~~~~~~~~~~

The latest version is available from PyPI or CARS (Univ of Chicago):

.. _wxmplot-0.9.14.tar.gz:  http://pypi.python.org/packages/source/w/wxmplot/wxmplot-0.9.14.tar.gz
.. _wxmplot-0.9.14.win32-py2.7.exe:  http://pypi.python.org/packages/source/w/wxmplot/wxmplot-0.9.14.win32-py2.7.exe

.. _wxmplot github repository:   http://github.com/newville/wxmplot
.. _Python Setup Tools:          http://pypi.python.org/pypi/setuptools

+---------------------+------------------+---------------------------------------+
|  Download Option    | Python Versions  |  Location                             |
+=====================+==================+=======================================+
| Source Kit          | 2.6, 2.7         | - `wxmplot-0.9.14.tar.gz`_            |
+---------------------+------------------+---------------------------------------+
| Windows Installers  | 2.7              | - `wxmplot-0.9.14.win32-py2.7.exe`_   |
+---------------------+------------------+---------------------------------------+
| Development Version | all              | use `wxmplot github repository`_      |
+---------------------+------------------+---------------------------------------+

if you have `Python Setup Tools`_  installed, you can download and install
the package simply with::

   easy_install -U wxmplot

Development Version
~~~~~~~~~~~~~~~~~~~~~~~~

To get the latest development version, use::

   git clone http://github.com/newville/wxmplot.git

Installation
~~~~~~~~~~~~~~~~~

wxmplot is a pure python module, so installation on all platforms can use the source kit::

   tar xvzf wxmplot-0.9.14.tar.gz  
   cd wxmplot-0.9.14/
   python setup.py install

or, again using ``easy_install -U wxmplot``.

License
~~~~~~~~~~~~~

The wxmplot code is distribution under the following license:

  Copyright (c) 2013 Matthew Newville, The University of Chicago

  Permission to use and redistribute the source code or binary forms of this
  software and its documentation, with or without modification is hereby
  granted provided that the above notice of copyright, these terms of use,
  and the disclaimer of warranty below appear in the source code and
  documentation, and that none of the names of The University of Chicago or
  the authors appear in advertising or endorsement of works derived from this
  software without specific prior written permission from all parties.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
  DEALINGS IN THIS SOFTWARE.


