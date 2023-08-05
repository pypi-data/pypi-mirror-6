This documentation is intended for use by pystan developers.

Release checklist
=================

- Update doc/whats_new.rst
- Set ISRELEASED = True in setup.py
- ``git tag``
- Push tag to github ``git push --tags``
- Git branch ``master`` should be fast-forwarded to ``develop``
- Git branch ``readthedocs`` force pushed after rebasing on new ``master``
- Assemble source distribution, sign it, upload to PyPI:

::

    python setup.py sdist
    gpg --detach-sign -a dist/pystan-x.x.x.x.tar.gz
    twine upload dist/*

After release
=============

- Add placeholder for changes in doc/whats_new.rst
- Set ISRELEASED = False in setup.py
- Bump version in setup.py
- Bump version in pystan/__init__.py
- Bump version in snippet in doc/getting_started.rst, i.e., "wget https://github.com/stan-dev/pystan/archive/0.2.0.zip"

See also
========
- http://docs.astropy.org/en/v0.2/development/building_packaging.html
