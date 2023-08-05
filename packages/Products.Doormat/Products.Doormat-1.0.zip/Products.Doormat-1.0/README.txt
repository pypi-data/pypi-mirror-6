.. image:: https://travis-ci.org/collective/Products.Doormat.png
  :target: https://travis-ci.org/collective/Products.Doormat

.. image:: https://coveralls.io/repos/collective/Products.Doormat/badge.png
  :target: https://coveralls.io/r/collective/Products.Doormat


Introduction
============

A doormat is a couple of links which are presented in a structured
way. One example is the current plone.org_, where the div#sitemap at the bottom
consists of some ordered bundles of internal and external links, with sections
called "Downloads", "Documentation", "Developers", "Plone foundation" and
"Support". See more examples_ of doormats.

This product adds a couple of content types (Archetypes), which are used to
create a structure which is used for generating a doormat. A viewlet on this
doormat is placed in the Plone footer. The links in the Doormat are managed as
content, making the Doormat more flexible than a sitemap.  It's also possible
to add external links. It's also possible to add bits of text, with markup.


Quick feature overview
======================

* Internal links
* External links
* Text blocks (including images)
* Links from Plone Collections
* Can have any number of columns
* Can have multiple sections per column


Similar products
================

collective.doormat
------------------

collective.doormat_ also lets you creates a doormat in your site, but takes a different approach: Instead of creating a structure of content objects, it offers a configuration panel where you can create the doormat in a single rich text field.

This approach is a lot easier for maintaining the doormat.

It doesn't take permissions into account, so links might point to internal content to which the visitor viewing the page has no access. There is also no way to add content from collections.


Getting started
===============

After installing the product in your site, you should have a "Doormat" item in
your Plone site, which should show up in the folder contents of the site.
Inside it, you can create a hierarchical structure of Columns,
Sections, links (both internal and external), Documents (Plone's Page type),
and Links to a Collection (DoormatCollection).
There should be one Column, one Section and one Document already there.

The Doormat may look like this, schematically::

    +-- Doormat ----------------------------------------------------------------------------+
    |                                                                                       |
    |  +-- Column 1 ----------+  +-- Column 2----------+  +-- Column 3 ------------------+  |
    |  |                      |  |                     |  |                              |  |
    |  |  +-- Section 1 ----+ |  | +-- Section 1 ----+ |  | +-- Section 1 -------------+ |  |
    |  |  |                 | |  | |                 | |  | |                          | |  |
    |  |  |  +-- Link 1 --+ | |  | |  +-- Link 1 --+ | |  | |  +-- Document 1 -------+ | |  |
    |  |  |  +------------+ | |  | |  +------------+ | |  | |  |                     | | |  |
    |  |  |                 | |  | |                 | |  | |  | (Contact info)      | | |  |
    |  |  |  +-- Link 2 --+ | |  | |  +-- Link 2 --+ | |  | |  |                     | | |  |
    |  |  |  +------------+ | |  | |  +------------+ | |  | |  +---------------------+ | |  |
    |  |  |                 | |  | |                 | |  | |                          | |  |
    |  |  |  +- Document -+ | |  | |                 | |  | |  +- DoormatCollection -+ | |  |
    |  |  |  |            | | |  | |                 | |  | |  |                     | | |  |
    |  |  |  |            | | |  | |                 | |  | |  | Item 1 from Collctn | | |  |
    |  |  |  +------------+ | |  | |                 | |  | |  | Item 2 from Collctn | | |  |
    |  |  |                 | |  | |                 | |  | |  | (...)               | | |  |
    |  |  |                 | |  | |                 | |  | |  | Link to Collection  | | |  |
    |  |  |                 | |  | |                 | |  | |  |                     | | |  |
    |  |  |                 | |  | |                 | |  | |  +---------------------| | |  |
    |  |  |                 | |  | |                 | |  | |                          | |  |
    |  |  +-----------------+ |  | +-----------------+ |  | +--------------------------+ |  |
    |  |                      |  |                     |  |                              |  |
    |  +----------------------+  +---------------------+  +------------------------------+  |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+

In fact, you can add more than one section, they will be displayed below each
other. In each section, you can mix internal links, external links and
Documents.

And in real life:

.. image:: http://plone.org/products/doormat/screenshot

Note that the product adds an extra hierarchical layer compared to the
plone.org_ doormat: it adds a Column, which can contain more than one Section.
An example using this structure is the Oosterpoort_, which actually is the
product's predecessor.


Adding a Document
=================

Adding and editing a Document to the Doormat is just as simple as adding it in
any other place. However, keep this in mind that only the "Body text" field
will be displayed in the Doormat. Other fields, most notably the title and
description will be omitted.

Links in a Document
-------------------

By default, relative links will be created from the place where the Document
lives. This link is then displayed in the Doormat on all pages, so it is very
likely to be broken.

The solution is to make your editor insert links by uid. With TinyMCE on Plone
4, you can enable "link by uid" by going to the "Resource types" tab on TinyMCE
Settings (via the "Site setup"), and checking the box called "Link using UIDs".

This will apply to the whole site. You may want to revert to the default
setting after you've added the link, as relative links are more desirable in
general.

Adding an Image
---------------

To add an image to the Doormat, add a Document and include an image there. It's
not possible to upload an Image to a DoormatSection, so you need to upload the
image to another place in your site first.

Make sure you enable "Link using UIDs" (see above) first, because defining the
image's location in a relative way will break in the same way as a relative
link will break.

Links to Collections
====================

It's also possible to add a "Link to Collection" item (DoormatCollection). This
allows yout to point to a Plone Collection object, and take the items from
that.


Simple configuration
====================

By default, the Doormat is excluded from navigation.

There's a field `showTitle` on the folderish types (Doormat, Column and
Section) which allows content managers to decide if the item's title should be
displayed in the doormat.


More advanced configuration and styling
=======================================

This section is intended for integrators and/or developers who would like to
customize the way the doormat is rendered in more detail.

Moving the doormat
------------------

By default, the default doormat viewlet (`doormat.footer`) is placed in the
`plone.portalfooter` viewlet manager. It's easy to modify this in an add-on
product, so the doormat will display below the global navigation (portal tabs),
or anywhere else in the site.


Displaying the doormat without the extra div elements
-----------------------------------------------------

The default viewlet renders the doormat inside Plone's default footer elements,
so it blends in with Plone 4's default Sunburst Theme::

  <div class="row">
    <div class="cell width-full position-0" >
      <div id="doormat-container" />
    </div>
  </div>

Using the `doormat.footer.bare` viewlet will omit the two outermost <div>'s.
This may be handy when using the doormat in a different theme, or in a
customized layout. You can hide the default viewlet and enable the bare version
through `@@manage-viewlets`, or by adding a customized `viewlets.xml` to the
product you're developing.


Caveats
=======

More than one Doormat
---------------------

The viewlet does a catalog lookup for the `Doormat` portal type. If you have
more than one object of this type (nothing stops you), it will use the oldest
one.

Uninstalling removes content
----------------------------

If you run the uninstall profile, like when you uninstall the product, **all
content will be deleted**. This ensures the product uninstalls cleanly, for
the convenience of migrations and of those just wanting to try it out.

If you have a Doormat in your site and you are happy with it, don't click
uninstall.


Dependencies / Requirements
===========================

The product works on:

* Plone 3
* Plone 4


Credits
=======

See Changelog.

This product was originally sponsored by GroningerForum_.


.. _examples: http://www.welie.com/patterns/showPattern.php?patternID=doormat
.. _plone.org: http://www.plone.org
.. _Oosterpoort: http://www.de-oosterpoort.nl
.. _GroningerForum: http://www.groningerforum.nl
.. _collective.doormat: http://plone.org/products/collective.doormat

