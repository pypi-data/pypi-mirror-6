Introduction
==============

This patch product can change view of review list and contents tab.
After install this product, non admin user can see and manage the
content that has future effective date. It can help editors and
reviewers to manage the content which will be published in future
date.

requirement
-------------
Plone 3.x (Tested by Plone 3.3.1 on MaxOS X 10.5)
Plone 4.0

note for Plone 3.2.x
-----------------------
You need to add on buildout.cfg

buildout.cfg

::

   [buildout]
   eggs =
      ...
      z3c.autoinclude
      c2.patch.dateforlisting

   zcml =
      ...
      z3c.autoinclude-meta
      c2.patch.dateforlisting
