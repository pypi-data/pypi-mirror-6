**************************
collective.customoverrides
**************************

.. contents:: Table of Contents

CSS and JS overrides for Plone
------------------------------

This product allows content managers to inject custom stylesheets and
Javascript by adding a file to a folder. On that folder and its descendants,
these will be added to the existing CSS/JS.

If you want to style a section of the site, Plone already provides ways to do
that. Please read
http://plone.org/documentation/kb/create-a-different-look-and-feel-for-different-sections-of-your-web-site-without-creating-new-skins
for more info on that, and decide if you have a use for this product.

How to use
^^^^^^^^^^

The main thing is to place a file called `custom.css` or `custom.js` ("custom
files") in a folder. These files will then be inserted in a special viewlet in
the HTML HEAD section.

There are two ways to manage custom files:

Add a custom file using Plone
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add a Plone File (ATFile). 

 * Prepare a `custom.css` or `custom.js` file
 * In Plone, go to the desired folder
 * Click the "Add item" menu
 * Select "File"
 * Upload the prepared file

The advantage of this method is that the familiar Plone interface can be used
to upload the file. Its disadvantage is that the file can't be modified: You'd
prepare a new file locally and replace the existing one instead.

Also be aware that:

* Plone files may be workflowed, depending on your site. If a custom file is
  private, it won't be visible to visitors who aren't logged in.
* Plone files may show up in your navigation, depending on your site's
  navigation settings.

Add a custom file using the ZMI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add a Zope File.

* Either:

  - In Plone, go to the desired folder and append `manage_main` to the URL, or
  - Go to the ZMI straight away, and go to the desired folder

* Add a File, name it either `custom.css` or `custom.js`

  - You may choose to upload a locally prepared file.

* Edit the file.

This method is more flexible: it is possible to edit the file through the web.
However, the ZMI is more complex to use, and requires higher permissions, so
this method is for power users.

Tested on
---------

Plone 3, Plone 4

Warning
-------

* Incorrect CSS/JS may mess up your site.
