Can I Use Python 3?
===================

This script takes in a set of dependencies and then figures out which
of them are holding you up from porting to Python 3.

You can specify your dependencies in multiple ways::

    caniusepython3 -r requirements.txt,test-requirement.txt
    caniusepython3 -m PKG-INFO
    caniusepython3 -p numpy,scipy,ipython
    # If your project's setup.py uses setuptools ...
    python setup.py caniusepython3

The output of the script will tell you how many (implicit) dependencies you need
to transition to Python 3 in order to allow you to make the same transition. It
will also list what projects have no explicit dependency blocking their
transition so you can ask them consider starting a port to Python 3.
<!-- END long_description -->

[![Build Status](https://travis-ci.org/brettcannon/caniusepython3.png?branch=master)](http://img.shields.io/travis/brettcannon/caniusepython3.svg)


How do you tell if a project has been ported to Python 3?
---------------------------------------------------------
On [PyPI](https://pypi.python.org/) each project specifies various
[trove classifiers](https://pypi.python.org/pypi?%3Aaction=list_classifiers).
There are various classifiers related to what version of Python a project can
run on. E.g.:

    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.0
    Programming Language :: Python :: 3.1
    Programming Language :: Python :: 3.2
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: 3.4

As long as a trove classifier for some version of Python 3 is specified then the
project is considered to support Python 3 (project owners: it is preferred you
**at least** specify `Programming Language :: Python :: 3` as that is how you
end up listed on the [Python3 Packages list on PyPI](https://pypi.python.org/pypi?%3Aaction=packages_rss)).

The other way is through a manual override in `caniusepython3` itself. This
project maintains a hard-coded list of projects which are considered ported
because:

* They are now part of [Python's standard library](http://docs.python.org/3/py-modindex.html) in some release of Python 3
* Their Python 3 port is under a different name
* They are missing a Python 3 trove classifier but have actually been ported

If any of these various requirements are met, then a project is considered to
support Python 3.


How can I get a project ported to Python 3?
-------------------------------------------
Typically projects which have not switched to Python 3 yet are waiting for:

* A dependency to be ported to Python 3
* Someone to volunteer to put in the time and effort to do the port

Since `caniusepython3` will tell you what dependencies are blocking a project
that you depend on from being ported, you can try to port a project farther
down your dependency graph to help a more direct dependency make the transition.

Which brings up the second point: volunteering to do a port. Most projects
happily accept help, they just have not done the port yet because they have
not had the time. Some projects are simply waiting for people to ask for it, so
even speaking up politely and requesting a port can get the process started.

If you are looking for help to port a project, you can always search online for
various sources of help. If you want a specific starting point there are
[HOWTOs](http://docs.python.org/3/howto/index.html) in the Python documentation
on [porting pure Python modules](http://docs.python.org/3/howto/pyporting.html)
and [extension modules](http://docs.python.org/3/howto/cporting.html).

Secret bonus feature
---------------------
If you would like to use a different name for the either the script or
setuptools command, then change the `command_name` line in `setup.py`. Reddit
suggests `icanhazpython3`.
