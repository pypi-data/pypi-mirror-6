from bise.catalogueindexer.interfaces import ICatalogueBase
from zope.component import queryAdapter


import transaction


def create_item(obj, event):
    adapter = queryAdapter(obj, ICatalogueBase)
    if adapter is not None:
        adapter.index_creation()


def update_item(obj, event):
    adapter = queryAdapter(obj, ICatalogueBase)
    if adapter is not None:
        adapter.index_update()


def adapter_delete(trans, adap):
    if trans:
        obj = adap.context
        # Delete only if it has been deleted from the parent
        if obj.id not in obj.__parent__.keys():
            adap.index_delete()


def delete_item(obj, event):
    adapter = queryAdapter(obj, ICatalogueBase)
    if adapter is not None:
        kwargs = dict(adap=adapter)
        transaction.get().addAfterCommitHook(adapter_delete, kws=kwargs)

