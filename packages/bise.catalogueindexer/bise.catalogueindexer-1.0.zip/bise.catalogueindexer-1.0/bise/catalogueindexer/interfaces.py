from zope import schema
from zope.interface import Interface

from bise.catalogueindexer import CatalogueIndexerMessageFactory as _


class ICatalogueIndexerSettings(Interface):
    """
    Configuration values for Catalogue available through plone.app.registry
    """

    catalogue_endpoint = schema.TextLine(
        title=_(u'Catalogue API endpoint'),
        description=_(u'Enter the full URL of the catalogue API, '
                      u'where the queries will be directed to'
            )
    )

    catalogue_authtoken = schema.TextLine(
        title=_(u'Authorization token for the Catalogue'),
        description=_(u"Enter the authorization token to call the API "
                      u"of the Catalogue"
            )
    )


class ICatalogueBase(Interface):

    def get_values_to_index():
        """
        return a dict with all items which should be passed to the
        webservice
        """

    def index_creation():
        """
        A method to index this object in the catalogue
        when the object is created for the first time
        """

    def index_update():
        """
        A method to index this object in the catalogue
        when the object is modified
        """

    def index_delete():
        """
        A method to register the deletion of the object
        in the catalogue
        """
