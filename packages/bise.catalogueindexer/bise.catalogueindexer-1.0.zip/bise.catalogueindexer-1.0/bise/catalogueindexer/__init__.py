from zope.i18nmessageid import MessageFactory
from plone import api

import logging

CatalogueIndexerMessageFactory = MessageFactory('bise.catalogueindexer')


if api.env.debug_mode():
    import httplib
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
