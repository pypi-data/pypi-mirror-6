slc.linkcollection Changelog
============================

1.4.2 (2013-12-18)
------------------

- Replace jQuery with jq to avoid conflicts [deroiste]


1.4.1 (2012-09-17)
------------------

- Plone 4

1.4.0 (2011-11-29)
------------------

- Minor changes for Plone4 compatibility [thomasw]

1.3.7 (2011-05-19)
------------------

- Added "slow" scrolling to anchors for jQuery based version [thomasw]

1.3.6 (2011-05-18)
------------------

- New jquery-ui based link collection: simply assign class "linkcollection" to
  a number of h2 tags. SEO improvement, refs #2830 [thomasw]

1.3.5 (2011-01-24)
------------------

- Added new styles to linkbox, provided by cornae. Reference: Syslab #1152
  [cornae, thomasw]
- Added anchor and corresponding "Go up" link. Reference: Syslab #1152
  [thomasw]

1.3.4 (2010-11-23)
------------------

- deactivated setting the div's height to maxheight #253 [thomasw]

1.3.3 (2010-10-21)
------------------

- set a class denoting the currently selected item also on the <li>, not only
  on the <a> tag [thomasw]


1.3.2 (2009-09-30)
------------------

- Nothing changed yet.

1.3.1 (2009-09-30)
------------------

- Bug fix: the parent folder could be selected as a link even though it isn't a
  document
- Feature: scroll to the top of the linkbox when a document is displayed
  without causing the page to jump up and down for longer and shorter
  documents.

1.3.0 (2009-09-29)
------------------

- linkcollection can now also be used on ATFolders. For the Annotations-factory, I had to use a somewhat
  awkward naming & inheritance construct, so as not to break existing linkcollection instances.
- added a BrowserView (linkcollection-view) for displaying contents of a Linkcollection
- enhanced search mechanism to distinguish between folder and document (thomasw)

slc.linkcollection 1.2.3 (2009-07-20)
-------------------------------------

- added an id to the linkcollection prefetched docs so that they can be fetched by the linkscanner (pilz)

slc.linkcollection 1.2.2 (2009-07-06)
-------------------------------------

- small fix for a bug with empty append

slc.linkcollection 1.2.1 (2009-07-03)
-------------------------------------

- Fixed problem where LC references a non existing doc but still appends it to the list (pilz)

slc.linkcollection 1.2 (2009-06-19)
-----------------------------------

- test fixes (gerken)

slc.linkcollection 1.1 (2009-05-12)
-----------------------------------

- Packaged egg (pilz)

slc.linkcollection 1.0 (2008-03-31)
-----------------------------------

- Initial port
