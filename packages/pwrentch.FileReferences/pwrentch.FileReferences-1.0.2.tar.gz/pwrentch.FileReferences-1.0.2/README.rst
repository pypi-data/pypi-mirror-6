pwrentch.FileReferences
=======================

pwrentch.FileReferences adds a browser view to your Plone site that produces a report showing all of the File and Image items in your site, or sub-folder of your site. Along with each item it also shows any content items in the site that link to that File or Image item.

This report can be useful in assessing the types of files and images your content editors have added to the site. It can also be useful if you're looking to remove or replace a certain file or image and need to know what other content links to it.

Installation
============

Dependencies
------------

Plone 4.1+

This product has been tested with Plone 4.1.4 and should work with anything newer.


Install stable version via Buildout
-----------------------------------

#. Add ``pwrentch.FileReferences`` to the eggs section of your buildout configuration
#. Run buildout
#. Restart Zope
#. Go to the Site Setup page in the Plone interface and click on the Add Ons link.
   Choose "File References" (check its checkbox) and click the Install button.


Using the latest development version
------------------------------------

#. Clone the repository from GitHub into the src folder
#. Add ``pwrentch.FileReferences`` to the eggs section of your buildout configuration
#. Add ``src/pwrentch.FileReferences`` to the develop section of your buildout configuration
#. Run buildout
#. Restart Zope
#. Go to the Site Setup page in the Plone interface and click on the Add Ons link.
   Choose "File References" (check its checkbox) and click the Install button.


Security
========

The view is hard coded to require the "Modify Portal Content" permission. Thus users must be logged in and have the Editor role in order to view the report.


Usage
=====

Add ``@@reflist`` to the end of any folder's URL to view the report of all the File and Image items in that folder and its sub-folders.

Click the "customize" link at the top of the page to choose to include/exclude File and/or Image items and to limit the type of documents displayed by their file type. File types are determined by filename extension and/or mime type.


Support
=======

*   Code repository: https://github.com/paulrentschler/pwrentch.FileReferences
*   Questions and comments: paul _ at _ rentschler _ dot _ ws
*   Report bugs: https://github.com/paulrentschler/pwrentch.FileReferences/issues


License
=======

Distributed under the GPL.

See LICENSE.txt and LICENSE.GPL for details.
