Comparable
==========

[![Build Status](https://travis-ci.org/jacebrowning/comparable.png?branch=master)](https://travis-ci.org/jacebrowning/comparable)
[![Coverage Status](https://coveralls.io/repos/jacebrowning/comparable/badge.png?branch=master)](https://coveralls.io/r/jacebrowning/comparable?branch=master)
[![PyPI Version](https://badge.fury.io/py/Comparable.png)](http://badge.fury.io/py/Comparable)

Comparable is a library providing abstract base classes that enable
subclasses to be compared for "equality" and "similarity" based on their
attributes.



Getting Started
===============

Requirements
------------

* Python 3.3: http://www.python.org/download/releases/3.3.4/#download


Installation
------------

Comparable can be installed with 'pip':

    pip install Comparable

Or directly from the source code:

    git clone https://github.com/jacebrowning/comparable.git
    cd comparable
    python setup.py install



Basic Usage
===========

After installation, abstract base classes can be imported from the
package:

    python
    >>> import comparable
    comparable.__version__
    >>> from comparable import SimpleComparable, CompoundComparable

Comparable classes use `==` as the operation for "equality" and `%`
as the operation for "similarity". They may also override a `threshold`
attribute to set the "similarity" ratio.


Simple Comparables
------------------

Simple comparable types must override the `equality` and `similarity`
methods to return bool and Similarity objects, respectively. See
`comparable.simple` for examples.


Compound Comparables
--------------------

Compound comparable types contain multiple simple comparable types. They
must override the `attributes` property to define which attributes
should be used for comparison. See `comparable.compund` for examples.



Examples
========

Comparable includes many generic comparable types:

    python
    >>> from comparable.simple import Number, Text, TextEnum, TextTitle
    >>> from comparable.compound import Group

A basic script may look similar to the following:

    from comparable.simple import TextTitle
    from comparable import tools

    base = TextTitle("The Cat and the Hat")
    items = [TextTitle("cat & hat"), TextTitle("cat & the hat")]

    print("Equality: {}".format(base == items[0]))
    print("Similarity: {}".format(base % items[0]))

    print("Duplicates: {}".format(tools.duplicates(base, items)))



For Contributors
================

Requirements
------------

* GNU Make:
    * Windows: http://cygwin.com/install.html
    * Mac: https://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make (likely already installed)
* virtualenv: https://pypi.python.org/pypi/virtualenv#installation
* Pandoc: http://johnmacfarlane.net/pandoc/installing.html


Installation
------------

Create a virtualenv:

    make env

Run the tests:

    make test
    make tests  # includes integration tests

Build the documentation:

    make doc

Run static analysis:

    make pep8
    make pylint
    make check  # pep8 and pylint

Prepare a release:

    make dist  # dry run
    make upload
