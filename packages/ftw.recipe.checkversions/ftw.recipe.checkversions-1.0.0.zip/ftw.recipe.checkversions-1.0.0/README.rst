==========================
 ftw.recipe.checkversions
==========================

The ``ftw.recipe.checkversions`` buildout recipe helps you finding newer versions
of your dependency packages.
It does this based on your version pinnings (buildout config file) by checking the
current releases of each package on pypi.


Installation
============

Buildout example:

.. code:: ini

    [buildout]
    parts = checkversions

    [checkversions]
    recipe = ftw.recipe.checkversions
    versions = versions.cfg
    blacklists =
        http://dist.plone.org/release/4-latest/versions.cfg
        https://raw.github.com/4teamwork/ftw-buildouts/master/test-versions.cfg
    backlist-packages =
        zope.interface


**versions**
  A file path or URL to a buildout config file containing version pinnings.
  The list of packages and the current pinnings are retreived from this file
  from the ``[versions]`` section.

**blacklists**
  A list of file paths and / or URLs of buildout configuration files containing
  version pinnings of packages to be ignored.
  All packages in the ``[versions]`` section are ignored, regardless of their pinning.

**blacklist-packages**
  List package names to be blacklisted.


Usage
=====

After installing the recipe using buildout simply run the ``bin/checkversions`` script.
The script prints out new versions of packages which are not listed in a blacklist.
Packages which are already up to date are not listed at all.


Links
=====

- github project: https://github.com/4teamwork/ftw.recipe.checkversions
- Issue tracker: https://github.com/4teamwork/ftw.recipe.checkversions/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.recipe.checkversions
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.recipe.checkversions


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.recipe.checkversions`` is licensed under GNU General Public License, version 2.
