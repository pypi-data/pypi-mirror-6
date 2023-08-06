purely.js
=========

.. image:: https://badge.fury.io/py/purelyjs.png
        :target: https://badge.fury.io/py/purelyjs

.. image:: https://travis-ci.org/numerodix/purelyjs.png?branch=master
        :target: https://travis-ci.org/numerodix/purelyjs

.. image:: https://pypip.in/license/purelyjs/badge.png
        :target: https://pypi.python.org/pypi/purelyjs/

* Command line test runner with minimal hassle (only needs a javascript shell
  like node.js/rhino/spidermonkey - no browser).
* Small library of JUnit-style testing primitives.


Quickstart
----------

.. code:: bash

    $ pip install purelyjs
    $ purelyjs


Theory
------

The composition of a typical Javascript application tends to be a mix of
library/framework code (jQuery, Backbone, Angular.js etc) and application
specific code. Frameworks provide many hooks that allow the programmer to
customize their behavior, which is accomplished through callbacks.

This tight coupling between the application and the framework makes it hard to
unit test the application logic (the framework is generally known to work well
already, that's typically why it was chosen). Worse still, the effects of the
application are manifest through side effects: network calls are made, ui
components are updated etc. Many heavy weight testing frameworks have sprung up
to address this need, and they are centered around driving a browser and
observing the effects (Selenium, phantomjs, etc).

.. code::

     Application
     --------------------------------------------
     |                                          |
     |            Callback spaghetti            |
     |         Land of the side effect          |
     |                                          |
     --------------------------------------------
     |                                          |
     |               Pure code                  |
     |                                          |
     --------------------------------------------

Still, almost every application needs to perform some tasks that have no
dependencies on network or browsers. Things like manipulating strings, numbers,
dates, arrays, custom data structures, parsing text streams etc. This code is
very amenable to unit testing, because it tends to be side effect free (ie.
pure).


Testing purely
--------------

The basic idea behind purely is that you split out your pure code from
your side-effectful code and write tests against it using the primitives
purely provides. Your stack will look like this:

.. code::

     Stack
     --------------------------------------------
     |                                          |
     |                  Tests                   |
     |                                          |
     --------------------------------------------      -----
     |                                          |        |
     |                purely.js                 |        |
     |    assertEqual, assertNotEqual etc...    |        |
     |                                          |       test
     --------------------------------------------   dependencies
     |                                          |        |
     |                Pure code                 |        |
     |                                          |        |
     --------------------------------------------      -----

Since none of this code needs a browser to run, purely can run it on a
javascript engine on the command line. First it will scan your test code to
find all the tests. For each test it will assemble a test module as shown below
(a single file containing all the code, plus the invocation of that one test)
and execute it.

.. code::

     Test module
     --------------------------------------------      -----
     |                                          |        |
     |                Pure code                 |        |
     |                                          |       test
     --------------------------------------------      module
     |                                          |        |
     |                purely.js                 |        |
     |    assertEqual, assertNotEqual etc...    |        V
     |                                          |
     --------------------------------------------
     |                                          |
     |                  Tests                   |
     |        function testThis() {...}         |
     |        function testThat() {...}         |
     |                                          |
     --------------------------------------------
     |                                          |
     |               testThis();                |
     |                                          |
     --------------------------------------------


Usage
-----

Run ``purelyjs`` with command line arguments:

.. code:: bash

    $ purelyjs --test test/test_asserts.js
    Running 10 tests on /usr/bin/js
    ..........

    ----------------------------------------------------------------------
    Ran 10 tests in 0.568s


You can also set up a ``purelyjs.ini`` file:

.. code::

    [purelyjs]

    # will be tried in order, first to succeed will be used
    interpreters = 
        js
        rhino

    libs = 
        static/js/code.js

    tests = 
        static/js/test/tests.js
