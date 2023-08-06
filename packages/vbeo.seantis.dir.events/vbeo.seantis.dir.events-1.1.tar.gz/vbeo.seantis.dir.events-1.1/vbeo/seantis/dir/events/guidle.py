from five import grok

from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from zope import i18n

from seantis.dir.events.interfaces import IGuidleClassifier
from seantis.dir.events.sources.guidle import EventsSourceGuidle

from seantis.dir.base.utils import cached_property
from vbeo.seantis.dir.events import _


class VbeoGuidleClassfier(grok.Adapter):
    grok.context(EventsSourceGuidle)
    grok.provides(IGuidleClassifier)

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
        site = getSite()
        lang = getToolByName(site, 'portal_languages').getDefaultLanguage()

        for tag in tagmap:
            tagmap[tag] = i18n.translate(
                tagmap[tag], target_language=lang, domain=i18ndomain
            )

        return tagmap

    def categories_by_tags(self, classification):
        categories = set()

        for tag in (c.attrib['name'] for c in classification.iterchildren()):
            for key in self.tagmap:
                if tag.startswith(key):
                    categories.add(self.tagmap[key])

        return categories

    def classify(self, classifications):
        categories = set()
        for classification in classifications.iterchildren():
            if classification.attrib['name'] != self.classification:
                continue
            categories = self.categories_by_tags(classification)

        return categories
