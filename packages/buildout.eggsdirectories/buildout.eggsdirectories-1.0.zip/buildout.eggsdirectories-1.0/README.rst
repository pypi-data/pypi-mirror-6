.. contents::

Introduction
============

``buildout.eggsdirectories`` includes all eggs found in prepopulated
directories.

This enables distribution of separate eggs sets.

Howto
=====

Tune ``buildout`` section::

  [buildout]
  extensions = buildout.eggsdirectories
  eggs-directories = ${buildout:directory}/more-eggs
                     /usr/local/plone-eggs

All eggs found in ``more-eggs`` or in ``/usr/local/plone-eggs`` will be made
available for the installation of eggs or creation of scripts.
