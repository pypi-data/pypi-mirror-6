.. Note::
    **Alternative product**
    
    This product is mainly deprecated. Think about switching to `wildcard.foldercontents`__, that is part on Plone 5.
    
    __ http://pypi.python.org/pypi/wildcard.foldercontents

.. contents::

Introduction
============

There's a piece of software that make possible sorting items in Plone, and it contains hidden additional features.
Normally, when you call a sort action in Plone, you call a URL like this::

    http://myhost/myfolder/folder_position?position=up&id=content_id

... of course, KSS/jQuery stuff in recent Plone versions will hide this feature, but is still available when you disable
Javascript.

The Plone UI has no way at the moment for performing actions like this::

    http://myhost/myfolder/folder_position?position=ordered&id=fieldname

But this feature is inside Plone: in this way you will sort a folder automatically, using a field value for comparison
(like ``title``, or ``created``).

What this product does
======================

This product adds to Plone some of the features that follow.

Can now sort a folder in reverse order
--------------------------------------

You can call an URL like this::

    http://myhost/myfolder/folder_position?position=ordered&id=created&reverse=1

and this will sort the folder using reverse criteria.


Add "delta" criteria to the sorting mechanism
---------------------------------------------

You can call::

    http://myhost/myfolder/folder_position?position=up&id=content_id&delta=4

and this will move the content down by 4 slots instead of the default 1 (this feature is not so useful if you use Plone KSS/jQuery/Javascript
sorting).


Add a nice Plone interface for global folder sorting
----------------------------------------------------

Your "*Action*" menu will be populated with a new entry: "*Sort folder*". This will present the user a Plone form where
he can perform common sorting operations.

.. image:: http://keul.it/images/plone/collective.sortmyfolder-1.0.0.png
   :alt: Sort my folder form

The last option makes it possible for users to specify a custom
attribute that's not in the list.  It is hidden by default and is
shown by Javascript as it needs some Javascript to work anyway.  If
you don't like this option, just add a CSS rules which hides the
``choice_custom_field`` element.


What this product isn't
=======================

This product only reveals features that are already in Plone (inside the *orderObjects* method).
It will not add new sorting behaviour.

Dependencies
============

Testing for collective.sortmyfolder has been done on:

* Plone 3.3
* Plone 4.2
* Plone 4.3

Note that on Plone 4, reverse sorting on the position does not work.
Work is under way to fix this.  It needs changes in both
``collective.sortmyfolder`` and the core ``plone.folder`` package.

Credits
=======

Developed with the support of `S. Anna Hospital, Ferrara`__

.. image:: http://www.ospfe.it/ospfe-logo.jpg 
   :alt: S. Anna Hospital - logo
     
S. Anna Hospital supports the
`PloneGov initiative`__.

__ http://www.ospfe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

 
