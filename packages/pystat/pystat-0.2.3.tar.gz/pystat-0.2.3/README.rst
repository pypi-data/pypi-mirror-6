=================================================
pystat - simple library for in-memory aggregation
=================================================

CI status: |cistatus|

.. |cistatus| image:: https://secure.travis-ci.org/blackwithwhite666/pystat.png?branch=master

This library is a thin python wrapper around counter and timer implementation in https://raw.github.com/armon/statsite

Installing
==========

pystat can be installed via pypi:

::

    pip install pystat


Building
========

Get the source:

::

    git clone https://github.com/blackwithwhite666/pystat.git


Compile extension:

::

     python setup.py build_ext --inplace



Usage
=====

Counter example:

::

    from pystat import Counter
    counter = Counter()
    counter.add()
    assert 1 == int(counter)
    counter.add()
    assert 2 == int(counter)
    counter.add(5)
    assert 7 == int(counter)
    assert 3 == len(counter)
    assert 5.0 == counter.max
    assert 1.0 == counter.min
    assert 2.333.. == counter.mean
    assert 2.309.. == counter.stddev

Timer example:

::

    from pystat import Timer
    timer = Timer()
    timer.add(1.0)
    assert 1 == int(timer)
    timer.add(1.0)
    assert 2 == int(timer)
    timer.add(5)
    assert 7 == int(timer)
    assert (0.5, 0.95, 0.99) == timer.quantiles
    assert 5.0 == timer.query(0.99)
    assert 1.0 == timer.query(0.5)


Running the test suite
======================

Use Tox to run the test suite:

::

    tox

