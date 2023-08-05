============
on.zopetools
============

Stuff to work with Zope & Plone from the command line or other programs.

Unfortunately, only creating mount points works reliably, so...

Installation
------------

Add the product to your buildout.cfg

After running buildout, you should have a console script, createmountpoints,
in your buildout's bin directory. Example:


::

  [tools]
  recipe = zc.recipe.egg
  eggs = on.zopetools


Typical Usage
-------------

::

  $ ./bin/instance run ./bin/createmountpoints


When the script exits, all ZODB mount points have been created.


TODO
====

This package needs tests!



LICENSE
=======

(c) 2014 Toni Mueller <support@oeko.net>

Software licensed under the AGPLv3 or later.

