import logging
import transaction
from Products.CMFCore.utils import getToolByName


INDEXES = {
    'FieldIndex' : [
        'dcterm_issue',
    ],
    'KeywordIndex' : [
    ],
}

METADATAS = [
    'dcterm_issue',
    'pages_count',
]

# Define custom indexes
class ZCTextIndex_extra:
    lexicon_id = 'plone_lexicon'
    index_type = 'Okapi BM25 Rank'

ZCTextIndex_extra = ZCTextIndex_extra()
SelectedTextIndex_type = 'ZCTextIndex'
SelectedTextIndex_extra = ZCTextIndex_extra

def setup_catalog(portal):
    log = logging.getLogger('collective.publications.catalog')
    portal_catalog = getToolByName(portal, 'portal_catalog')
    for typ in INDEXES:
        for idx in INDEXES[typ]:
            e = None
            if typ == 'ZCTextIndex':
                e= SelectedTextIndex_extra
            if not idx in portal_catalog.indexes():
                log.info('Adding index: %s' % idx)
                portal_catalog.manage_addIndex(idx, typ, e)

    for column in METADATAS:
        if not column in portal_catalog.schema():
            log.info('Adding metadata: %s' % column)
            portal_catalog.manage_addColumn(column)

def setupVarious(context):
    """Miscellanous steps import handle.
    """
    logger = logging.getLogger('collective.publications / setuphandler')

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('collective.publications_various.txt') is None:
        return

    portal = context.getSite()
    setup_catalog(portal)
