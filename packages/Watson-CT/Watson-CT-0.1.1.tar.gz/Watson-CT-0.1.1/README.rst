Watson
======

Watson is a continuous unit test runner for django. As long as the script is running, it will monitor for changes in your code and re-run your test suite when needed.

Features
--------

* Monitor source code and run tests on change
* OSX notifications
* Colored test output

Installation
------------

Watson can be installed from PyPI using easy_install::
    
    $ easy_install Watson-CT
    
or pip::
    
    $ pip install Watson-CT

Setup
-----

To setup Watson under Django add ``watson`` to your ``INSTALLED_APPS`` setting.
The run ``manage.py drwatson`` to start the tester process. You can give an
application label or test name using the same format as the built-in ``test``
command.

Options
~~~~~~~

``--nocolor`` : *flag, default: False*
    Disable colored output.

``-u``, ``--ui`` : *default: autodetect*
    Force the use of a specific UI module. Available options are ``growl2`` and ``none``.


UIs
---

Watson provides a UI to indicate the current test status after each run, even
if the console is in the background.

Growl 2
~~~~~~~

The default UI on OS X uses Growl 2 via AppleScript. A Growl 2 notification is
posted after each test run. https://itunes.apple.com/us/app/growl/id467939042