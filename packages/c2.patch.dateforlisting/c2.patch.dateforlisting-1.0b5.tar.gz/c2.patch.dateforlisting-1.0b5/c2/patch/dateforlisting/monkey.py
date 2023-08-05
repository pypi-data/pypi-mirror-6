#!/usr/bin/env python
# encoding: utf-8
"""
monkey.py

Created by Manabu TERADA on 2010-09-25.
Copyright (c) 2010 CMScom. All rights reserved.
"""
from Acquisition import aq_inner
from plone.app.content.browser.foldercontents import FolderContentsTable
# from plone.app.content.browser.foldercontents import FolderContentsView
from c2.patch.contentslist.browser.foldercontents import FolderContentsView

from Products.CMFPlone.WorkflowTool import WorkflowTool
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager


from logging import getLogger
logger = getLogger(__name__)
info = logger.info


try:
    import pkg_resources
    plone_version = pkg_resources.get_distribution('Plone').version
    major, minor, sub = plone_version.split('.', 2)
    if int(major) > 3:
        LESSPLONE33 = False
    elif int(minor) >2:
        LESSPLONE33 = False
    else:
        LESSPLONE33 = True
except:
    LESSPLONE33 = False

try:
    from Products.TinyMCE.adapters.JSONFolderListing import JSONFolderListing
    HAS_TINY_MCE = True
except ImportError:
    HAS_TINY_MCE = False



def contents_table(self):
    contentFilter={}
    if self.is_listing_reverse():
        contentFilter['sort_order'] = 'reverse'
    contentFilter['show_inactive'] = True
    table = FolderContentsTable(aq_inner(self.context), self.request,
                            contentFilter=contentFilter)
    return table.render()

FolderContentsView.contents_table = contents_table
info('patched %s', str(FolderContentsView.contents_table))


def getWorklistsResults(self):
    """Return all the objects concerned by one or more worklists

    This method replace 'getWorklists' by implementing the whole worklists
    work for the script.
    An object is returned only once, even if is return by several worklists.
    Make the whole work as expensive it is.
    """
    sm = getSecurityManager()
    # We want to know which types use the workflows with worklists
    # This for example avoids displaying 'pending' of multiple workflows in the same worklist
    types_tool = getToolByName(self, 'portal_types')
    catalog = getToolByName(self, 'portal_catalog')

    list_ptypes = types_tool.listContentTypes()
    types_by_wf = {} # wf:[list,of,types]
    for t in list_ptypes:
        for wf in self.getChainFor(t):
            types_by_wf[wf] = types_by_wf.get(wf, []) + [t]

    # PlacefulWorkflowTool will give us other results
    placeful_tool = getToolByName(self, 'portal_placeful_workflow', None)
    if placeful_tool is not None:
        for policy in placeful_tool.getWorkflowPolicies():
            for t in list_ptypes:
                chain = policy.getChainFor(t) or ()
                for wf in chain:
                    types_by_wf[wf] = types_by_wf.get(wf, []) + [t]

    objects_by_path = {}
    for id in self.getWorkflowIds():

        wf=self.getWorkflowById(id)
        if hasattr(wf, 'worklists'):
            for worklist in wf.worklists:
                wlist_def=wf.worklists[worklist]
                # Make the var_matches a dict instead of PersistentMapping to enable access from scripts
                catalog_vars = dict(portal_type=types_by_wf.get(id, []))
                for key in wlist_def.var_matches:
                    catalog_vars[key] = wlist_def.var_matches[key]
                ## patch
                catalog_vars['show_inactive'] = True
                for result in catalog.searchResults(**catalog_vars):
                    o = result.getObject()
                    if o \
                       and id in self.getChainFor(o) \
                       and wlist_def.getGuard().check(sm, wf, o):
                        absurl = o.absolute_url()
                        if absurl:
                            objects_by_path[absurl] = (o.modified(), o)

    results = objects_by_path.values()
    results.sort()
    return tuple([ obj[1] for obj in results ])

def plone32_getWorklistsResults(self):
    """Return all the objects concerned by one or more worklists

    This method replace 'getWorklists' by implementing the whole worklists
    work for the script.
    An object is returned only once, even if is return by several worklists.
    Make the whole work as expensive it is.
    """
    sm = getSecurityManager()
    # We want to know which types use the workflows with worklists
    # This for example avoids displaying 'pending' of multiple workflows in the same worklist
    types_tool = getToolByName(self, 'portal_types')
    catalog = getToolByName(self, 'portal_catalog')

    list_ptypes = types_tool.listContentTypes()
    types_by_wf = {} # wf:[list,of,types]
    for t in list_ptypes:
        for wf in self.getChainFor(t):
            types_by_wf[wf] = types_by_wf.get(wf, []) + [t]

    # PlacefulWorkflowTool will give us other results
    placeful_tool = getToolByName(self, 'portal_placeful_workflow', None)
    if placeful_tool is not None:
        for policy in placeful_tool.getWorkflowPolicies():
            for t in list_ptypes:
                chain = policy.getChainFor(t) or ()
                for wf in chain:
                    types_by_wf[wf] = types_by_wf.get(wf, []) + [t]

    objects_by_path = {}
    for id in self.getWorkflowIds():

        wf=self.getWorkflowById(id)
        if hasattr(wf, 'worklists'):
            wlists = []
            for worklist in wf.worklists._objects:
                wlist_def=wf.worklists._mapping[worklist['id']]
                # Make the var_matches a dict instead of PersistentMapping to enable access from scripts
                catalog_vars = dict(portal_type=types_by_wf.get(id, []))
                for key in wlist_def.var_matches.keys():
                    catalog_vars[key] = wlist_def.var_matches[key]
                ## patch
                catalog_vars['show_inactive'] = True
                for result in catalog.searchResults(**catalog_vars):
                    o = result.getObject()
                    if o \
                       and id in self.getChainFor(o) \
                       and wlist_def.getGuard().check(sm, wf, o):
                        absurl = o.absolute_url()
                        if absurl:
                            objects_by_path[absurl] = (o.modified(), o)

    results = objects_by_path.values()
    results.sort()
    return tuple([ obj[1] for obj in results ])



if not LESSPLONE33:
    WorkflowTool.getWorklistsResults = getWorklistsResults
    info('patched %s', str(WorkflowTool.getWorklistsResults))
else:
    WorkflowTool.getWorklistsResults = plone32_getWorklistsResults
    info('patched %s for Less than PLONE33', str(WorkflowTool.getWorklistsResults))
    

if HAS_TINY_MCE:
    _listing_base_query = {'show_inactive' : True}
    JSONFolderListing.listing_base_query = _listing_base_query
    info('patched TinyMCE %s', str(JSONFolderListing.listing_base_query))
