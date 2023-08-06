from decimal import Decimal
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.geo.settings.interfaces import IGeoSettings


def setup_geo(site):
    registry = getUtility(IRegistry)

    # note, the weird way lists below are used is due to the fact that
    # they break if they are replaced, so all updates must be in-place
    # it's probably due to the settings being proxied

    # setup the types
    geo_settings = registry.forInterface(IGeoSettings)

    types = ('seantis.dir.events.directory', 'seantis.dir.events.item')
    for t in types:
        if t not in geo_settings.geo_content_types:
            geo_settings.geo_content_types.append(t)

    # setup the default map layers, removing the old ones first
    # (we need a copy for that)
    to_remove = [l for l in geo_settings.default_layers]
    for layer in to_remove:
        geo_settings.default_layers.remove(layer)

    layers = ('osm', )
    for layer in layers:
        if layer not in geo_settings.default_layers:
            geo_settings.default_layers.append(layer)

    # set the location to City of Thun
    geo_settings.longitude = Decimal("7.6333")
    geo_settings.latitude = Decimal("46.7667")
    geo_settings.zoom = Decimal("11")


def custom_setup(context):

    if 'vbeo/seantis' in context._profile_path:
        setup_geo(context.getSite())
