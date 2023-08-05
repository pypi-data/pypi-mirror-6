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
            # maincategories where the subcategories do not matter
            'D': _(u"Fair"),
            'H': _(u"Sports"),
            'I': _(u"Excursions for Guests"),
            'J': _(u"Meetings, Animation"),
            'K': _(u"Gastronomy"),

            # maincategories where some subcategories differ
            'A01': _(u"Blues, Jazz, Gospel"),
            'A02': _(u"Folk songs, Hits"),
            'A03': _(u"Folk, Country"),
            'A04': _(u"Classical Music"),
            'A05': _(u"Rock, Pop"),
            'A06': _(u"Techno, Rap, Techno Parties"),
            'A07': _(u"Swiss Folk Music"),
            'A08': _(u"Ethno Music"),
            'A09': _(u"Light Music"),
            'A10': _(u"Oopmh Music"),
            'A11': _(u"Musical"),
            'A12': _(u"Opera, Operetta"),
            'A13': _(u"Barrel Organ"),
            'A14': _(u"Concerts"),
            'B01': _(u"Authors' Reading"),
            'B02': _(u"Ballet, Dance, Mouvement"),
            'B03': _(u"Film, Video, Performance"),
            'B04': _(u"Cabaret, Satirical Revue"),
            'B07': _(u"Pantomime, Clown"),
            'B08': _(u"Puppet Theater, Figures"),
            'B09': _(u"Stage Play, Spectacle"),
            'B10': _(u"Street Theater"),
            'B11': _(u"Music-Hall"),
            'B12': _(u"Popular Theater"),
            'B13': _(u"Circus"),
            'B14': _(u"Movie Theater"),
            'B15': _(u"Theatres"),
            'C02': _(u"Cultures, History"),
            'C03': _(u"Paintings, Engravings"),
            'C04': _(u"Graphic Design, Design"),
            'C05': _(u"Arts & Crafts"),
            'C08': _(u"Photo, Video Art"),
            'C09': _(u"Plastic Art, Sculptures, Installations"),
            'C10': _(u"Jewellery, Knich-Knacks"),
            'C12': _(u"Art"),
            'F01': _(u"Open Air"),
            'F02': _(u"Street Parade"),
            'F03': _(u"Festival"),
            'F05': _(u"Lake Festival at Night"),
            'F06': _(u"Town Festival, Village Festival, Fair"),
            'F07': _(u"Children's Festival"),
            'F08': _(u"Parade"),
            'F09': _(u"Festival, Festivities"),
            'F10': _(u"Anniversary, Ceremony"),
            'G01': _(u"Forum, Symposium"),
            'G02': _(u"Congress, Course"),
            'G03': _(u"Congress, Course"),
            'G04': _(u"Lecture"),
            'G05': _(u"Congress, Course"),
            'G06': _(u"Congress, Course"),
            'G07': _(u"Congress, Course"),
            'G08': _(u"Congress, Course"),
            'G09': _(u"Congress, Course"),
            'G10': _(u"Congress, Course"),
            'G11': _(u"Congress, Course"),
            'G12': _(u"Congress, Course")
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
