# -*- coding: utf-8 -*-


from zope import schema
from zope.interface import Interface

from zopyx.together import MessageFactory as _


class ITogetherSettings(Interface):
    """ zopyx.together settings """

    hub_url = schema.TextLine(
        title=_(u'TogetherJS hub URL'),
        required=True,
        default=u'https://hub.togetherjs.com',)
