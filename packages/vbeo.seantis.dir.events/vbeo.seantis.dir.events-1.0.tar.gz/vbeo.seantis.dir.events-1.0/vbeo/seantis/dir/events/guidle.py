from five import grok
from zope.interface import Interface

from seantis.dir.events.interfaces import IEventsDirectory
from seantis.dir.events.sources.guidle import IGuidleConfig

from seantis.dir.base.utils import cached_property
from seantis.dir.events.utils import translate
from vbeo.seantis.dir.events import _


class GuidleConfig(grok.MultiAdapter):
    grok.adapts(IEventsDirectory, Interface)
    grok.implements(IGuidleConfig)

    url = "http://www.guidle.com/m_QpCBiK/Berner-Oberland/Veranstaltungen"

    classification = "Veranstaltungskalender MySwitzerland"

    @cached_property
    def tagmap(self):

        tagmap = {
            'A': _(u"Concerts"),
            'B': _(u"Theatres"),
            'C': _(u"Art"),
            'D': _(u"Fair"),
            'E': _(u"Customs, Market"),
            'F': _(u"Festival, Festivities"),
            'G': _(u"Congress, Course"),
            'H': _(u"Sports"),
            'I': _(u"Excursions for Guests"),
            'J': _(u"Meetings, Animation"),
            'K': _(u"Gastronomy")
        }

        i18ndomain = 'vbeo.seantis.dir.events'

        for tag in tagmap:
            tagmap[tag] = translate(
                self.request, tagmap[tag], domain=i18ndomain
            )

        return tagmap

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def on_event(self, root, offer, event):
        pass
