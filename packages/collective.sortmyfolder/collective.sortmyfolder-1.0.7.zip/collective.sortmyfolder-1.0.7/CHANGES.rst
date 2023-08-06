Changelog
=========

1.0.7 (2014-04-08)
------------------

- Change capitalisation of ID sort field name from ``Id``.
  [davidjb]
- Change action to be displayed if a default view is configured for a folder.
  [davidjb]


1.0.6 (2013-09-05)
------------------

- Add option to sort by id.
  [maurits]

- Hide the custom field by default.  Show it with Javascript.
  [maurits]

- Fix javascript for newer jquery versions in newer Plones, not using
  the ``jq`` alias.
  [maurits]


1.0.5 (2012-11-13)
------------------

- Fixed manifest for rst files [micecchi]


1.0.4 (2012-11-13)
------------------

- Fixed uninstall step for skin layer [micecchi]


1.0.3 (2012-10-14)
------------------

- Moved to https://github.com/collective/collective.sortmyfolder
  [maurits]


1.0.2 (2011-11-14)
------------------

* Set the icon_expr in actions.xml so we register the action icon in
  the preferred way in Plone 4.  We keep actionicons.xml for backwards
  compatibility with Plone 3.
  [maurits]

* No longer use the plone domain for our action as portal_actions
  accepts other domains too.  This means we no longer need the i18n
  directory.  Added an upgrade step to switch our action to use
  collective.sortmyfolder as domain.
  [maurits]

* Added MANIFEST.in so .mo files can be included in the release
  (automatically when using zest.releaser+zest.pocompile).
  [maurits]

* Made compatible with Plone 4.1.
  [maurits]


1.0.1 (2011-04-20)
------------------

* Updated Dutch translations [fvandijk]
* Corrected english spelling in README.txt [fvandijk]

1.0.0 (2011-04-06)
------------------

* added new dates sorting criteria [keul]
* added the field for a custom way to sort [keul] 
* do not show the menu entry if you can't sort the current object [keul]
* added some javascript for the new custom field.
  Not enabled js browser will no be able to use the new feature [keul]
* tested also on Plone 4

0.2.0 (2011-01-07)
------------------

* fixed typo syntax error in english text [markvl]
* added dutch translation [markvl]

0.1.0 (2010-12-02)
------------------

* initial release

