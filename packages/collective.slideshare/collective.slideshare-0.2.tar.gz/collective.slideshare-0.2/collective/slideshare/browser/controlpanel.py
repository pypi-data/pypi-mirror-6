from plone.app.registry.browser import controlpanel

from collective.slideshare.interfaces import ISlideshareSettings, _


class SlideShareEditForm(controlpanel.RegistryEditForm):

    schema = ISlideshareSettings
    label = _(u"Slideshare settings")
    description = _(u"Slideshare settings")

    def updateFields(self):
        super(SlideShareEditForm, self).updateFields()


    def updateWidgets(self):
        super(SlideShareEditForm, self).updateWidgets()

class SlideshareControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SlideShareEditForm
