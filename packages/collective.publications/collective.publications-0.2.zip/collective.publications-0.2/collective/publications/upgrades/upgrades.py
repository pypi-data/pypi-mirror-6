# -*- coding: utf-8 -*-

import os, sys
import logging
logger = logging.getLogger("GenericSetup")

try:
    from Products.CMFPlone.migrations import migration_util
except:
    #plone4
    from plone.app.upgrade import utils as migration_util

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface.image import IATImage
from Products.ATContentTypes.content.image import ATImage
from collective.publications import setuphandlers
from collective.publications.content.publication import IPublication
from plone.dexterity.interfaces import IDexterityContent
import transaction


from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from logging import getLogger
logger = getLogger('collective.publications.migration')
#logger.info(message)

def upgrade_to_1001(context):
    """Upgrade to 1001"""
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile('profile-collective.publications:default', 'cssregistry', run_dependencies=False)
    setup.runImportStepFromProfile('profile-collective.publications:default', 'typeinfo', run_dependencies=False)
    transaction.commit()

    site = getToolByName(context, 'portal_url').getPortalObject()
    setuphandlers.setup_catalog(site)
    site.portal_catalog.reindexIndex('dcterm_issue', site.REQUEST)
    
    

