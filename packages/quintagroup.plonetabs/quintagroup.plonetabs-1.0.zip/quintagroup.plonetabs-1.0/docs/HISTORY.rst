Changelog
=========

1.0 - (25-02-2014)
------------------

* Added French translations from transifex, thanks Marc Sokolovitch
  [kroman0, msoko]

* Updated code according with pep8, pylint, pyflakes
  [kroman0, potar]

* Fixed tests and compatibility with Plone 3  (added plone detecting)
  [potar]

* Added plone.browserlayer to install_requires (setup.py)
  [potar]

* Added more tests, cleanup code
  [kroman0]

* Added description field
  [kroman0]

0.7 - (12-03-2012)
------------------
* Updated permissions. Starting from Plone 4.1 it is necessary
  to import permissions.zcml from Products.CMFCore.
  [potar]

0.6 - (21-06-2011)
------------------
* Merged plone4 branch [chervol]

* Confirmed plone4 compatibility [gotcha]

* Take care of the case when there are no tabs [gotcha]

0.5b1 - Unreleased
------------------

* Updated documentation appropriately to changes and made it a valid reST text.
  [piv]

* Added tests, including tests for javascript code (using ecmaunit.js and
  Selenium tests (be means of kss.demo package)).
  [piv]

* Added Ukrainian translation.
  [piv]

* Made package fully translatable.
  [piv]

* Added possibility to explicitly change configlet edit mode, between
  rich (Ajax based) and plain (basic HTML) modes.
  [piv]

* Added uninstall procedure.
  [piv]

* Got rid of TODO.txt file.
  [piv]

* Added browser layer for installed product. Used it for browser views.
  [piv]

* Now portal status messages are hidden after 10 seconds (of course this
  concerns only Ajax based mode ;-).
  [piv]

* Formatted python code to make it shorter or equal to 80 characters per line.
  [piv]

* Refactored presentation layer (html/css things).
  [serg]

* Made Ajax configlet fully compatible with IE7.
  [piv]

* Fixed switching between categories for IE7.
  [piv]

* Switched off browser's autocomplete feature for name field in add form.
  [piv]

* Refactored messaging strategy, made it a little bit friendlier and
  more consistent.
  [piv]

* Fixed js id generation after cancel button.
  [piv]


0.5a - January 29, 2009
-----------------------

* Improved actions reordering mechanism.
  [piv]

* Added possibility to edit actions of any categories located in
  portal_actions tool.
  [piv]

* All templates are now zope 3 views.
  [piv]

* All Ajax functionality is based now on kss javascript framework.
  [piv]

* Initial package structure.
  [zopeskel]
