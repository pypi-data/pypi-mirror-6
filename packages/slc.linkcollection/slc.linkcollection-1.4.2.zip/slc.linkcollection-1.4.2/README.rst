Project Description
*******************

.. contents::

.. Note!
   -----

   - code repository
   - bug tracker
   - questions/comments feedback mail


- Code repository: https://github.com/collective/slc.linkcollection
- Questions and comments to info (at) syslab (dot) com
- Report bugs at http://plone.org/products/slc.linkcollection


Overview
========

This is a simple add-on that provides a tabbed-style display for the content of documents.
You only need to add class "linkcollection" to a h2 heading. This heading will be
turned into the title of the tab, and the following content, until the next such heading
or the end of the page, will become the tab content. There can only be one tab open at a
time - clicking on one tab closes the others.

At the bottom of each tab's content, an anchor link to the top is inserted. Clicking on it will
cause a smooth scroll to the top.

WYSIWYG editor integration
--------------------------

You can add a style to the editor of your choice, so that a heading can be added to a link collection
without the need for manually adding a class.

For TinyMCE, go to portal_tinymce/@@tinymce-controlpanel and add the following line under Styles::

  Linkcollection|h2|linkcollection

For CKEditor, go to @@ckeditor-controlpanel and add the following line under Menu Styles,
in the section Block Styles::

  { name : 'Linkcollection', element: 'h2', attributes: {'class': 'linkcollection' } },

Legacy implementation
---------------------

The first version of the link collection worked by selecting references to documents to be displayed.
Hence the name "link collection". The tabbed collection itself was displayed in a viewlet. The code
for this version is still present, but not recommended to use for SEO reasons (content duplication
is considered bad).

Credits
=======

Copyright European Agency for Health and Safety at Work and Syslab.com
GmbH.

slc.linkcollection development was funded by the European Agency for
Health and Safety at Work.


License
=======

slc.linkcollection is licensed under the GNU Lesser Generic Public
License, version 2 or later and EUPL version 1.1 only. The complete
license texts can be found in docs/LICENSE.GPL and docs/LICENSE.EUPL.
