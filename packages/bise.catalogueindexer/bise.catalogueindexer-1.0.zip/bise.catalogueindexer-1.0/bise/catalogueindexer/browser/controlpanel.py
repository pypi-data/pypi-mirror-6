from bise.catalogueindexer import CatalogueIndexerMessageFactory as _
from bise.catalogueindexer.interfaces import ICatalogueIndexerSettings
from plone.app.registry.browser import controlpanel


class CatalogueIndexerSettingsEditForm(controlpanel.RegistryEditForm):

    schema = ICatalogueIndexerSettings
    label = _(u"BISE catalogue settings")
    description = _(u"""Configuration for BISE catalogue""")

    def updateFields(self):
        super(CatalogueIndexerSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(CatalogueIndexerSettingsEditForm, self).updateWidgets()


class CatalogueIndexerSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = CatalogueIndexerSettingsEditForm
