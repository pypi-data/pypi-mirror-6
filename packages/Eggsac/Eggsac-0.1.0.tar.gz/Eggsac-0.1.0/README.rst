Eggsac: Package Python applications in a virtualenv for deployment.

Eggsac takes a Python application,
installs it and all of its dependencies into a *relocatable* virtualenv_,
and wraps it all up in a ready-to-run tarball, zipfile, or Debian package,
which can be deployed on other machines.

Motivation
----------

Installing Python applications can be slow.
Compiling Python modules into bytecode,
compiling C extensions into shared libraries,
building eggs,
downloading a cascade of dependencies from the `Python Package Index`_
(assuming PyPI is available)—\
all of this can take several minutes for a large application.
Even if you have an internal PyPI mirror and use binary eggs for the dependencies,
it can still take a long time to roll the application out to a server farm.

Eggsac does all of this effort as part of your build process,
leaving you with a single ready-to-run file to deploy to your servers.

Caveat: your build machine has to be running the same operating system
as your application servers, but this is a common requirement.



.. _virtualenv:
    https://pypi.python.org/pypi/virtualenv
.. _PyPI:
.. _Python Package Index:
    https://pypi.python.org/pypi
