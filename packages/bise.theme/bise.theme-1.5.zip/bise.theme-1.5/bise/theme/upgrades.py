from logging import getLogger
from Products.CMFCore.utils import getToolByName


def ploneglossary_1001(context, logger=None):
    if logger is None:
        logger = getLogger('ploneglossary_1001')

    js_registry = getToolByName(context, 'portal_javascripts')
    resource = js_registry.getResource('ploneglossary_definitions.js')
    resource.setInline(False)
    logger.info('Upgraded')


def reload_css_1001(context, logger=None):
    if logger is None:
        logger = getLogger('reload_css_1001')

    default_profile = 'profile-bise.biodiversityfactsheet:default'
    context.runImportStepFromProfile(default_profile, 'jsregistry')
    logger.info('Upgraded')
