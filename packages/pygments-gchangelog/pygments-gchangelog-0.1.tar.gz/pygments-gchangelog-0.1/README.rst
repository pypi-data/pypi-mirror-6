pygments-gchangelog
===================

.. image:: https://travis-ci.org/bacher09/pygments-gchangelog.png?branch=master
    :target: https://travis-ci.org/bacher09/pygments-gchangelog

Pygments lexer and style for Gentoo Portage's `changelog files`__.

Installation
------------
 * run ``pip install pygments-gchangelog``
 * download source and execute ``python setup.py install``

Requirements
------------

 * pygments

Usage
-----

You may use lexer and/or style with pygments console program or with it's api
like any other lexer or style.
::

  $ pygmentize -l changelog ChangeLog
  $ pygmentize -l changelog -O style=changelog ChangeLog
  $ pygmentize -l changelog -f html -O full,style=changelog ChangeLog > changelog.html

LICENSE
-------
MIT


.. _Changelog: http://devmanual.gentoo.org/ebuild-writing/misc-files/changelog/
__ Changelog_
