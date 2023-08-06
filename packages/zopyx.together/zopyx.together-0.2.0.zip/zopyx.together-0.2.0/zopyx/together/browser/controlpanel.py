# -*- coding: utf-8 -*-

from plone.app.registry.browser import controlpanel

from zopyx.together.interfaces import ITogetherSettings
from zopyx.together import MessageFactory as _


class TogetherSettingsEditForm(controlpanel.RegistryEditForm):

    schema = ITogetherSettings
    label = _(u'zopyx.together settings')
    description = _(u'')

    def updateFields(self):
        super(TogetherSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(TogetherSettingsEditForm, self).updateWidgets()


class TogetherControlPanel(controlpanel.ControlPanelFormWrapper):
    form = TogetherSettingsEditForm
