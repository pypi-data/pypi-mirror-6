# -*- coding: utf-8 -*-

from zope import schema
from zope.component.hooks import getSite
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import IContainerModifiedEvent, IObjectRemovedEvent
from zope.interface import Interface, Invalid, invariant
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zExceptions import Redirect
from z3c.form import form
from five import grok
from plone import api
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.uuid.utils import uuidToObject
from plone.autoform.directives import widget
from plone.memoize import ram
from plone.memoize.interfaces import ICacheChooser
from plone.registry.interfaces import IRecordModifiedEvent, IRegistry
from plone.z3cform import layout
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.registry import DictRow
from Products.statusmessages.interfaces import IStatusMessage
from .. import _
from ..config import ORGANIZATIONS_REGISTRY, FUNCTIONS_REGISTRY, PLONEGROUP_ORG


class IOrganizationSchema(Interface):
    """
        Organization identification schema
    """
    org_id = schema.TextLine(title=_("Organization id"), required=True)
    org_title = schema.TextLine(title=_("Organization title"), required=True)


class IFunctionSchema(Interface):
    """
        Function identification schema
    """
    fct_id = schema.TextLine(title=_("Plone group suffix id"), required=True)
    fct_title = schema.TextLine(title=_("Plone group suffix title"), required=True)


class OwnOrganizationServicesVocabulary(grok.GlobalUtility):
    """
        Vocabulary of own organizations services. Needed to be used with plone.app.registry list field
    """
    grok.name('collective.contact.plonegroup.organization_services')
    grok.implements(IVocabularyFactory)

    def listSubOrganizations(self, terms, folder, parent_label='', parent_id=''):
        for orga in folder.listFolderContents(contentFilter={'portal_type': 'organization'}):
            term_title = orga.Title()
            if parent_label:
                term_title = "%s - %s" % (parent_label, term_title)
            term_token = orga.getId()
            if parent_id:
                term_token = "%s|%s" % (parent_id, term_token)
            terms.append(SimpleTerm(orga.UID(), term_token, term_title))
            self.listSubOrganizations(terms, orga, term_title, term_token)

    def __call__(self, context):
        portal = getSite()
        terms = []
        pcat = portal.portal_catalog
        brains = pcat(portal_type='organization', id=PLONEGROUP_ORG)
        if not brains:
            terms.append(SimpleTerm(None, token="unfound",
                                    title=_(u"You must define an organization with id '${pgo}' !",
                                            mapping={'pgo': PLONEGROUP_ORG})))
            return SimpleVocabulary(terms)
        elif len(brains) > 1:
            terms.append(SimpleTerm(None, token="multifound", title=_(u"You must have only one organization "
                                                                      "with id '${pgo}' !",
                                                                      mapping={'pgo': PLONEGROUP_ORG})))
            return SimpleVocabulary(terms)

        own_orga = brains[0].getObject()
        self.listSubOrganizations(terms, own_orga)

        return SimpleVocabulary(terms)


class IContactPlonegroupConfig(Interface):
    """
        Configuration schema
    """

    # plone.registry cannot store schema.Choice different from named vocabularies !
    organizations = schema.List(
        title=_(u'Selected organizations'),
        description=_(u"Choose multiple organization levels for which you want to create a plone group."),
        required=True,
        value_type=schema.Choice(vocabulary=u'collective.contact.plonegroup.organization_services',))

    functions = schema.List(
        title=_(u'Function list'),
        description=_(u'Each defined function will suffix each organization plone group.'),
        required=True,
        value_type=DictRow(title=_("Function"),
                           schema=IFunctionSchema)
    )
    widget(functions=DataGridFieldFactory)

    @invariant
    def validateSettings(data):
        if not data.organizations:
            raise Invalid(_(u"You must choose at least one organization !"))
        if len(data.organizations) == 1 and data.organizations[0] is None:
            raise Invalid(_(u"You must correct the organization error first !"))
        if not data.functions:
            raise Invalid(_(u"You must define at least one function !"))


def addOrModifyGroup(group_name, organization_title, function_title):
    """
        create a plone group
    """
    if isinstance(organization_title, unicode):
        organization_title = organization_title.encode('utf8')
    if isinstance(function_title, unicode):
        function_title = function_title.encode('utf8')
    group = api.group.get(groupname=group_name)
    group_title = '%s (%s)' % (organization_title, function_title)
    if group is None:
        group = api.group.create(
            groupname=group_name,
            title=group_title,
        )
        return True
    else:
        #group_title is maybe modified
        if group.getProperty('title') != group_title:
            group.setProperties(title=group_title)
            return True
    return False


def invalidate_sopgv_cache():
    """
        invalidate cache of selectedOrganizationsPloneGroupsVocabulary
    """
    cache_chooser = getUtility(ICacheChooser)
    thecache = cache_chooser('collective.contact.plonegroup.browser.settings.selectedOrganizationsPloneGroupsVocabulary')
    thecache.ramcache.invalidate('collective.contact.plonegroup.browser.settings.selectedOrganizationsPloneGroupsVocabulary')


def invalidate_sov_cache():
    """
        invalidate cache of selectedOrganizationsVocabulary
    """
    cache_chooser = getUtility(ICacheChooser)
    thecache = cache_chooser('collective.contact.plonegroup.browser.settings.selectedOrganizationsVocabulary')
    thecache.ramcache.invalidate('collective.contact.plonegroup.browser.settings.selectedOrganizationsVocabulary')


def detectContactPlonegroupChange(event):
    """
        Manage our record changes
    """
    if IRecordModifiedEvent.providedBy(event): # and event.record.interface == IContactPlonegroupConfig:
        registry = getUtility(IRegistry)
        changes = False
        if event.record.fieldName == 'organizations' and registry[FUNCTIONS_REGISTRY]:
            old_set = set(event.oldValue)
            new_set = set(event.newValue)
            # we detect a new organization
            add_set = new_set.difference(old_set)
            for uid in add_set:
                obj = uuidToObject(uid)
                full_title = obj.get_full_title(separator=' - ', first_index=1)
                for fct_dic in registry[FUNCTIONS_REGISTRY]:
                    group_name = "%s_%s" % (uid, fct_dic['fct_id'])
                    if addOrModifyGroup(group_name, full_title, fct_dic['fct_title']):
                        changes = True
            # we detect a removed organization. We dont do anything on exsiting groups
            if old_set.difference(new_set):
                changes = True
        elif event.record.fieldName == 'functions' and registry[ORGANIZATIONS_REGISTRY]:
            old_set = new_set = set()
            if event.oldValue:
                old_set = set([(dic['fct_id'], dic['fct_title']) for dic in event.oldValue])
            if event.newValue:
                new_set = set([(dic['fct_id'], dic['fct_title']) for dic in event.newValue])
            # we detect a new function
            add_set = new_set.difference(old_set)
            registry = getUtility(IRegistry)
            for (new_id, new_title) in add_set:
                for uid in registry[ORGANIZATIONS_REGISTRY]:
                    obj = uuidToObject(uid)
                    full_title = obj.get_full_title(separator=' - ', first_index=1)
                    group_name = "%s_%s" % (uid, new_id)
                    if addOrModifyGroup(group_name, full_title, new_title):
                        changes = True
            # we detect a removed function. We dont do anything on exsiting groups
            if old_set.difference(new_set):
                changes = True
        if changes:
            invalidate_sopgv_cache()
            invalidate_sov_cache()


class SettingsEditForm(RegistryEditForm):
    """
    Define form logic
    """
    form.extends(RegistryEditForm)
    schema = IContactPlonegroupConfig

SettingsView = layout.wrap_form(SettingsEditForm, ControlPanelFormWrapper)


def addOrModifyOrganizationGroups(organization, uid):
    """
        Modify groups linked to an organization
    """
    registry = getUtility(IRegistry)
    changes = False
    for dic in registry[FUNCTIONS_REGISTRY]:
        full_title = organization.get_full_title(separator=' - ', first_index=1)
        group_name = "%s_%s" % (uid, dic['fct_id'])
        if addOrModifyGroup(group_name, full_title, dic['fct_title']):
            changes = True
    return changes


def getOwnOrganizationPath():
    """
        get plonegroup-organization path
    """
    portal = getSite()
    pcat = portal.portal_catalog
    brains = pcat(portal_type='organization', id=PLONEGROUP_ORG)
    if brains:
        return '/'.join(brains[0].getObject().getPhysicalPath())
    return 'unfound'


def adaptPloneGroupDefinition(organization, event):
    """
        Manage an organization change
    """
    # zope.lifecycleevent.ObjectRemovedEvent : delete
    # zope.lifecycleevent.ObjectModifiedEvent : edit, rename
    # is the container who's modified at creation ?
    # bypass if we are removing the Plone Site
    if IContainerModifiedEvent.providedBy(event) or \
       event.object.portal_type == 'Plone Site':
        return
    # is the current organization a part of own organization
    organization_path = '/'.join(organization.getPhysicalPath())
    if not organization_path.startswith(getOwnOrganizationPath()):
        return
    portal = getSite()
    registry = getUtility(IRegistry)
    # when an organization is removed (and its content), we check if it is used in plonegroup configuration
    if IObjectRemovedEvent.providedBy(event) and organization.UID() in registry[ORGANIZATIONS_REGISTRY]:
        smi = IStatusMessage(organization.REQUEST)
        smi.addStatusMessage(_('You cannot delete this item !'), type='error')
        smi.addStatusMessage(_("This organization or a contained organization is used in plonegroup "
                               "configuration ! Remove it first from the configuration !"), type='error')
        view_url = getMultiAdapter((organization, organization.REQUEST), name=u'plone_context_state').view_url()
        organization.REQUEST['RESPONSE'].redirect(view_url)
        raise Redirect, _("This organization or a contained organization is used in plonegroup "
                          "configuration ! Remove it first from the configuration !")
        return
    pcat = portal.portal_catalog
    brains = pcat(portal_type='organization', path=organization_path)
    changes = False
    for brain in brains:
        orga = brain.getObject()
        orga_uid = orga.UID()
        if orga_uid in registry[ORGANIZATIONS_REGISTRY]:
            if addOrModifyOrganizationGroups(orga, orga_uid):
                changes = True
    if changes:
        invalidate_sopgv_cache()


def sopgv_cache_key(function, functions=[], group_title=True):
    """
        calculate the cache key
    """
    return (set(functions), group_title)


@ram.cache(sopgv_cache_key)
def selectedOrganizationsPloneGroupsVocabulary(functions=[], group_title=True):
    """
        Returns a vocabulary of selected organizations corresponding plone groups
    """
    registry = getUtility(IRegistry)
    terms = []
    # if no function given, use all functions
    if not functions:
        functions = [fct_dic['fct_id'] for fct_dic in registry[FUNCTIONS_REGISTRY]]
    for uid in registry[ORGANIZATIONS_REGISTRY]:
        for fct_id in functions:
            group_id = "%s_%s" % (uid, fct_id)
            group = api.group.get(groupname=group_id)
            if group is not None:
                if group_title:
                    title = group.getProperty('title')
                else:
                    title = uuidToObject(uid).get_full_title(separator=' - ', first_index=1)
                terms.append(SimpleTerm(group_id, token=group_id, title=title))
    return SimpleVocabulary(terms)


@ram.cache(lambda *args: True)
def selectedOrganizationsVocabulary():
    """
        Returns a vocabulary of selected organizations
    """
    registry = getUtility(IRegistry)
    terms = []
    for uid in registry[ORGANIZATIONS_REGISTRY]:
        title = uuidToObject(uid).get_full_title(separator=' - ', first_index=1)
        terms.append(SimpleTerm(uid, token=uid, title=title))
    return SimpleVocabulary(terms)
