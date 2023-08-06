Copyright (c) 2014 Janne Vanhala

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Description: Siilo
        =====
        
        .. image:: http://img.shields.io/travis/jpvanhal/siilo/master.svg
           :target: http://travis-ci.org/jpvanhal/siilo
        
        .. image:: http://img.shields.io/coveralls/jpvanhal/siilo/master.svg
          :target: https://coveralls.io/r/jpvanhal/siilo?branch=master
        
        .. image:: http://img.shields.io/pypi/dm/siilo.svg
          :target: https://pypi.python.org/pypi/siilo
        
        .. image:: http://img.shields.io/pypi/v/siilo.svg
          :target: https://pypi.python.org/pypi/siilo
        
        Siilo is a file abstraction layer for Python. It is inspired by `Django's File
        storage API`_, but is framework agnostic.
        
        .. _Django's File storage API:
           https://docs.djangoproject.com/en/dev/ref/files/storage/
        
        Siilo supports for the following file storages:
        
        - Local Filesystem
        - Apache Libcloud
        - Amazon S3
        
        Siilo has the following goals:
        
        - to be compatible with Python’s file API
        - to support both Python 2 and 3
        - to have full unit test coverage.
        
        You can install the library with pip::
        
            pip install siilo
        
        Resources
        ---------
        
        * `Documentation <http://siilo.readthedocs.org>`_
        * `Bug Tracker <http://github.com/jpvanhal/siilo/issues>`_
        * `Code <http://github.com/jpvanhal/siilo>`_
        * `Development Version <http://github.com/jpvanhal/siilo/zipball/master#egg=siilo-dev>`_
        
        Changelog
        ---------
        
        Here you can see the full list of changes between each Siilo release.
        
        0.1.0 (April 25th, 2014)
        ^^^^^^^^^^^^^^^^^^^^^^^^
        
        - Initial public release.
        
Platform: any
Classifier: Development Status :: 3 - Alpha
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: Implementation :: CPython
Classifier: Programming Language :: Python :: Implementation :: PyPy
Classifier: Topic :: Software Development :: Libraries :: Python Modules
