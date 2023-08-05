from bise.catalogueindexer.interfaces import ICatalogueIndexerSettings
from logging import getLogger
from plone import api
from plone.app.dexterity.behaviors.metadata import IDublinCore
from plone.registry.interfaces import IRegistry
from Products.CMFCore.WorkflowCore import WorkflowException
from StringIO import StringIO
from zope.component import getUtility

import DateTime
import requests


class BaseObjectCataloguer(object):
    """
    Base adapter. All other adapters should subclass
    this one, implement `get_values_to_index` method and
    be registered for the correct interface.

    Thus, the webservice interaction code is written just once.

    """

    def __init__(self, context):
        self.context = context

    def get_values_to_index(self):
        return {}

    def _get_catalog_url(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICatalogueIndexerSettings)
        return settings.catalogue_endpoint

    def _get_catalog_authtoken(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICatalogueIndexerSettings)
        return settings.catalogue_authtoken

    def index_creation(self):
        url = self._get_catalog_url()
        items = self.get_values_to_index()
        if items and url:
            files = {}
            if 'document[file]' in items:
                files['document[file]'] = items.get('document[file]')
                del items['document[file]']

            resp = requests.post(
                url,
                data=items,
                files=files,
            )
            if not resp.ok:
                log = getLogger('index_creation')
                log.info('Error indexing creation of {0}'.format(
                    '/'.join(self.context.getPhysicalPath())
                    )
                )
            import time
            time.sleep(1)

    def index_update(self):
        url = self._get_catalog_url()
        items = self.get_values_to_index()
        if items and url:
            resource_type = items.get('resource_type')
            items['{0}[source_url]'.format(resource_type)] = self.context.absolute_url()
            files = {}
            if 'document[file]' in items:
                files['document[file]'] = items.get('document[file]')
                del items['document[file]']

            resp = requests.put(
                url,
                data=items,
                files=files,
            )
            if not resp.ok:
                log = getLogger('index_update')
                log.info('Error updating {0}'.format(
                    '/'.join(self.context.getPhysicalPath())
                    )
                )

    def index_delete(self):
        url = self._get_catalog_url()
        if url:
            items = {}
            ditems = self.get_values_to_index()
            items['auth_token'] = ditems.get('auth_token', '')
            resource_type = ditems.get('resource_type', '')
            items['resource_type'] = resource_type
            items['{0}[source_url]'.format(resource_type)] = self.context.absolute_url()
            resp = requests.delete(
                url,
                data=items,
            )
            if not resp.ok:
                log = getLogger('index_delete')
                log.info('Error deleting {0}'.format(
                    '/'.join(self.context.getPhysicalPath())
                    )
                )


class PACDocumentCataloguer(BaseObjectCataloguer):

    def get_values_to_index(self):
        context = self.context
        try:
            metadata = IDublinCore(context)
            items = {}
            items['auth_token'] = self._get_catalog_authtoken()
            items['language'] = context.Language().upper()

            # XXX: should be context.creator
            user = api.user.get(context.Creator())
            if user is not None:
                fullname = user.getProperty('fullname') or user.getId()
            else:
                fullname = context.Creator()

            items['article[author]'] = fullname
            items['article[title]'] = metadata.title
            items['article[english_title]'] = metadata.title
            created = context.created().strftime('%d/%m/%Y')
            items['article[published_on]'] = created
            try:
                if api.content.get_state(obj=context) == 'published':
                    items['article[approved]'] = 'true'
                    if metadata.effective:
                        if callable(metadata.effective):
                            effective = metadata.effective().strftime('%d/%m/%Y')
                        else:
                            effective = metadata.effective.strftime('%d/%m/%Y')
                    else:
                        effective = DateTime.DateTime().strftime('%d/%m/%Y')
                    items['article[approved_at]'] = effective
                else:
                    items['article[approved]'] = '0'
                    items['article[approved_at]'] = u''
            except WorkflowException:
                items['article[approved]'] = 'true'
                items['article[approved_at]'] = created

            items['article[source_url]'] = context.absolute_url()

            if context.text:
                content = metadata.description + u' ' + context.text.output
            else:
                content = metadata.description

            items['article[content]'] = content
            items['resource_type'] = 'article'
            return items
        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)
            return {}


class PACFileCataloguer(PACDocumentCataloguer):

    def get_values_to_index(self):
        context = self.context
        items = {}
        items['auth_token'] = self._get_catalog_authtoken()
        items['language'] = context.Language().upper()

        # XXX should be context.creator
        user = api.user.get(context.Creator())
        if user is not None:
            fullname = user.getProperty('fullname') or user.getId()
        else:
            fullname = context.Creator()

        items['document[author]'] = fullname
        items['document[title]'] = context.title
        items['document[english_title]'] = context.title
        created = context.created().strftime('%d/%m/%Y')
        items['document[published_on]'] = created
        try:
            if api.content.get_state(obj=context) == 'published':
                items['document[approved]'] = 'true'
                if context.effective:
                    if callable(context.effective):
                        effective = context.effective().strftime('%d/%m/%Y')
                    else:
                        effective = context.effective.strftime('%d/%m/%Y')
                else:
                    effective = DateTime.DateTime().strftime('%d/%m/%Y')
                items['document[approved_at]'] = effective
            else:
                items['document[approved]'] = 'false'
                items['document[approved_at]'] = u''
        except WorkflowException:
            items['document[approved]'] = 'true'
            items['document[approved_at]'] = created

        items['document[source_url]'] = context.absolute_url()

        items['document[description]'] = context.description
        filedata = (context.file.filename, StringIO(context.file.data))
        items['document[file]'] = filedata
        items['resource_type'] = 'document'

        return items


class PACLinkCataloguer(PACDocumentCataloguer):

    def get_values_to_index(self):
        context = self.context
        items = {}
        items['auth_token'] = self._get_catalog_authtoken()
        items['language'] = context.Language().upper()

        # XXX should be context.creator
        user = api.user.get(context.Creator())
        if user is not None:
            fullname = user.getProperty('fullname') or user.getId()
        else:
            fullname = context.Creator()

        items['link[author]'] = fullname
        items['link[title]'] = context.title
        items['link[english_title]'] = context.title
        created = context.created().strftime('%d/%m/%Y')
        items['link[published_on]'] = created
        try:
            if api.content.get_state(obj=context) == 'published':
                items['link[approved]'] = 'true'
                if context.effective:
                    if callable(context.effective):
                        effective = context.effective().strftime('%d/%m/%Y')
                    else:
                        effective = context.effective.strftime('%d/%m/%Y')
                else:
                    effective = DateTime.DateTime().strftime('%d/%m/%Y')
                items['link[approved_at]'] = effective
            else:
                items['link[approved]'] = 'false'
                items['link[approved_at]'] = u''
        except WorkflowException:
            items['link[approved]'] = 'true'
            items['link[approved_at]'] = created

        items['link[source_url]'] = context.absolute_url()

        items['link[description]'] = context.description
        items['link[url]'] = context.remoteUrl
        items['resource_type'] = 'link'

        return items
