from Products.CMFCore.utils import getToolByName

from seantis.dir.events.interfaces import IExternalEvent


def upgrade_1_to_2(context):

    # Delete all imported event
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(object_provides=IExternalEvent.__identifier__)
    for brain in brains:
        try:
            event = brain.getObject()
            event.aq_parent.manage_delObjects([event.getId()])
        except:
            pass

    # reindex everything
    catalog = getToolByName(context, 'portal_catalog')
    catalog.clearFindAndRebuild()
