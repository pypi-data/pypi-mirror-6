Changelog
=========

0.6 (unreleased)
----------------

- No changes yet.


0.5.1 (2014-02-25)
------------------

- Fixed batching provider for Plone < 4.2.


0.5 (2014-02-24)
----------------

- Added local MLS configuration.
- Added compatibility with deprecated batching used prior Plone 4.2.
- I18N updates.


0.4.2 (2013-06-27)
------------------

- CI with travis-ci.


0.4.1 (2013-06-26)
------------------

- Fixed Batching for Plone >= 4.2.
- I18N updates.


0.4 (2012-02-11)
----------------

- Registered I18N locales folder.


0.3 (2012-02-11)
----------------

- I18N updates merged.


0.2 (2012-02-05)
----------------

- Replaced old PloneTestCase based tests with plone.app.testing.
- Added custom permission for controlpanel view.
- Added custom listing result batch provider based on plone's batching.
- Added i18n support.


0.1.1 (2011-10-26)
------------------

- Added error handling if connection to the MLS can't be established.


0.1 (2011-09-07)
----------------

- Use httplib2 instead of urllib2 to get json data.
- Use the new MLS listing api. Added language support.


0.1b2 (2011-05-24)
------------------

- Fixed manage portlets fallback link (Plone 4 only).


0.1b1 (2011-05-23)
------------------

- Now raises MLSConnectionErrors if no MLS connection or bad requests.
- Added manage portlets fallback link for dexterity types.


0.1dev (2011-05-18)
-------------------

- First Beta Release.
