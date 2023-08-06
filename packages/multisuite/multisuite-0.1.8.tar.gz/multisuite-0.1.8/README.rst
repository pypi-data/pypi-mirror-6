multisuite
==========

Run independent nose test suites together as one. This is particulary useful,
if you are having suites with different package requirements.

Install
-------

In contrast to other Python tools it is not reasonable to put multisuite in
virtualenvs, because its task is to manage virtualenvs for your tests. You can
still install it into your system with pip, though::

    $ sudo pip install multisuite

If that is not what you want, you can simply download the ``multisuite.py``
file from `the repository <https://github.com/DFE/multisuite>`_. It is one file
and currently contains everything that is needed to run multisuite.

Tutorial
--------

Let's say you have two test suites with a set of requirements each. One
contains `MONK <https://github.com/DFE/MONK>`_ in version 0.1.1 and the other
in version 0.1.2. Therefore it is not possible to run both test suites in the
same virtualenv. Manually creating different virtualenvs for different test
suites can become quite complex if you have more than two suites like these.
Therefore you decide to use multisuite.

Your suites look like this::

    root/
      suite_1/
        __init__.py
        requirements.txt # contains monk_tf==0.1.1
        suite.py
      suite_2/
        __init__.py
        requirements.txt # contains monk_tf==0.1.2
        suite.py

The order is important here. Each suite can contain as many files as you want,
but it needs to contain at least these three files. The ``requirements.txt``
file contains the requirements that this suite needs and the ``suite.py`` file
contains the test case (or the reference to them). And it needs to contain an
``__init__.py`` file because that's how ``nosetests`` will recognize them.

If you want to make sure, that you have a correct suite, you can create them
with multisuite as well::

    $ multisuite makesuite suite_1 suite_2

You can check if your test suites can be found by multisuite::

    $ multisuite list
    suite_1
    suite_2

If a suite is not listed here it was not detected correctly. Please check again
if all requirements are met. Now you can run a test suite by itself::

    $ multisuite test suite_1 suite_2
    ...
    suite suite_1 ok
    suite suite_2 ok

And you can simply run all tests together::

    $ multisuite
    ...
    suite suite_1 ok
    suite suite_2 ok

Tipps
-----

 * You do not need to spell the prefix ``suite_`` explicitly. Both the
   following commands are equal::

       $ multisuite makesuite suite_bugfixes suite_unittests
       $ multisuite makesuite bugfixes unittests
