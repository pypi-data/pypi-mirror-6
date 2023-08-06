from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.layout.viewlets.common import ViewletBase
from zopyx.together.interfaces import ITogetherSettings

class Viewlet(ViewletBase):

    def hub_url(self):
        """ Return the configured TogetherJS hub URL """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITogetherSettings)
        return settings.hub_url
