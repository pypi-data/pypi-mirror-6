pytest_pyramid
==============

.. image:: https://travis-ci.org/fizyk/pytest_pyramid.png?branch=master
    :target: https://travis-ci.org/fizyk/pytest_pyramid
    :alt: Tests for RandomWords

.. image:: https://coveralls.io/repos/fizyk/pytest_pyramid/badge.png?branch=master
    :target: https://coveralls.io/r/fizyk/pytest_pyramid?branch=master
    :alt: Coverage Status

.. image:: https://requires.io/github/fizyk/pytest_pyramid/requirements.png?branch=master
   :target: https://requires.io/github/fizyk/pytest_pyramid/requirements/?branch=master
   :alt: Requirements Status

pytest_pyramid provides basic fixtures for testing pyramid applications with pytest test suite.

By default, pytest_pyramid will create two fixtures: pyramid_config, which creates configurator based on config.ini file, and pyramid_app, which creates TestApp based on Configurator returned by pyramid_config.

Command line options
--------------------

* **--pc** - pyramid configuration file based on which pytest_pyramid will create test app

Documentation
-------------

http://pytest-pyramid.readthedocs.org/en/latest/

TODO
----

This goal should make it in to 1.0 major release.

#. provide a pyramid_proc fixture that will start pyramid app process using summon_process


Tests
-----

To run tests run this command:

`py.test --pc tests/pyramid.test.ini`


=======
CHANGES
=======

0.1.1
-----
- make factories condition to check parameters against None

0.1.0
-----
- initial release
- pyramid_config fixture factory and default fixture
- pyramid_app fixture factory and default fixture
- documentation


