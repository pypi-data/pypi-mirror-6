curmit
======

| |Build Status|
| |Coverage Status|
| |PyPI Version|

Grabs text from a URL and commits it.

Getting Started
===============

Requirements
------------

-  Python 3.3: http://www.python.org/download/releases/3.3.3/#download
-  git: http://git-scm.com/downloads

Installation
------------

curmit can be installed with ``pip``:

::

    pip install curmit

Or directly from the source code:

::

    python setup.py install

Setup
-----

#. Create a new text file
#. Add the following somewhere in the first few lines:

   ::

       curmit: https://docs.google.com/document/d/<DocumentID>/pub?embedded=true

   (with a URL of your chosing)

Usage
=====

To update every flagged file with the current URL text, commit, and
push:

::

    curmit

That's it!

.. |Build Status| image:: https://travis-ci.org/jacebrowning/curmit.png?branch=master
   :target: https://travis-ci.org/jacebrowning/curmit
.. |Coverage Status| image:: https://coveralls.io/repos/jacebrowning/curmit/badge.png?branch=master
   :target: https://coveralls.io/r/jacebrowning/curmit?branch=master
.. |PyPI Version| image:: https://badge.fury.io/py/curmit.png
   :target: http://badge.fury.io/py/curmit

Changelog
=========

0.0.1 (2014/02/10)
-------------------

 - Initial development release.


