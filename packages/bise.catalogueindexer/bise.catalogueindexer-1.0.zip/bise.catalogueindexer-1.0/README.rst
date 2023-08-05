Introduction
============

Event handlers to index BISE site content in BISE Catalogue.

Install
------------

Go to the Plone Control Panel, install this add-on, and a new control panel
entry will be created, where the info for the webservice should be entered:
the API endpoint and the site id value.

Contact the Catalogue adminsitrator to get this information.


How this works
-----------------

This package provides 3 event listeners for basic plone content-types (based on
plone.app.contenttypes). These event listeners adapt the context object
to Catalogue resource types (Article, Document or Link), get the relevant information
and then index in the catalogue.

This package provides basic adapters for plone.app.contenttypes provided content-types,
if you need more specific adapters for your content-types, just create an adapter
for it.

You can inherit the base adapter which provides basic web-service connection methods.
Then just implement the method `get_values_to_index` method, returning a dict with
the parameters which will be passed to the webservice. The basic adapter is at
`bise.catalogueindexer.adapters.basic.BaseObjectCataloguer`
