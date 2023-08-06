*********************************
Configs: Configuration for Humans
*********************************

.. image:: http://img.shields.io/pypi/v/configs.svg
    :target: http://pypi.python.org/pypi/configs/
    :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/configs.svg
    :target: http://pypi.python.org/pypi/configs/
    :alt: Number of PyPI downloads

Parsing INI configs must be easy, as are the INI files.

**Configs** provides a simple API for getting data from INI config files.

Loading data from a config is as easy as ``configs.load('my.conf')``.

``Configs`` work with Python 2.7+.

The repo is at `bitbucket.org/moigagoo/configs <https://bitbucket.org/moigagoo/configs>`_.

Read the full documentation at `configs.rtfd.org <http://configs.rtfd.org>`_.

Features
========

*   Root-level params support
*   Numeric and boolean values are converted automatically
*   Sections with only key-value items are parsed as dicts
*   Sections with only flag items (keys with no value) are parsed as lists
*   Mixed content sections are parsed as tuples of a dict and a list, which can be accessed individually
*   Sections are iterable (even the mixed ones; list first, dict second)
*   Comments support

Installation
============

Install configs with pip:

.. code-block:: bash

    $ pip install configs

Basic usage
===========
Load a config file::

    >>> import configs
    >>> c = configs.load('sample.conf')
    >>> c['general']
    {'foo': 'baz'}

Load a config file with a fallback config file (with default values)::

    >>> fc = configs.load('sample.conf', fallback_file='default.conf')
    >>> fc['general']['spam']
    eggs

Tests
=====

Run the tests with:

.. code-block:: bash

    $ python test_configs.py
