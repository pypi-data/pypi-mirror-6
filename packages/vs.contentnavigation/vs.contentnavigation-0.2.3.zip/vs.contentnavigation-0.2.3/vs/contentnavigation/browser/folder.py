#####################################################################
# vs.contentnavigation
# (C) 2012, Veit Schiele communications GmbH
#####################################################################

from Products.Five.browser import BrowserView
from plone.app.layout.viewlets.common import ViewletBase
from Products.ATContentTypes.interfaces import IATFolder
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

from plone.registry.interfaces import IRegistry
from plone.app.layout.navigation.defaultpage import isDefaultPage

class Base(object):
    """ Shared between browser view and viewlet class """

    def getSubnavigationRoot(self):
        """ Walk up a folder hierarchy and figure out the 
            first folder having set the 'contentNavigation' flag.
            Returns None otherwise.
        """
        current = self.context
        latest_found = None
        while current.portal_type != 'Plone Site':
            field = current.getField('contentNavigation')
            if field is not None:
                if field.get(current):
                    latest_found = current
            current = current.aq_inner.aq_parent
        return latest_found

    def haveSubnavigationRoot(self):
        """ Check if there is a subnavigation root somewhere 
            in the parent hierarchy.
        """
        root = self.getSubnavigationRoot()
        return int(root is not None and not root == self.context)

class ViewletSitemap(ViewletBase, Base):
    pass


class SitemapView(BrowserView, Base):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        metaTypesNotToList = getToolByName(self.context, 'portal_properties').navtree_properties.metaTypesNotToList
        self.metaTypesNotToList = dict([(key, 1) for key in metaTypesNotToList])

    # --- public API -----------------------------------------------------------

    def getSitemapForContext(self, current_context=None):
        registry = getUtility(IRegistry)
        render_root = registry['vs.contentnavigation.render_root_node']  
        return self._renderSitemap(self.getNavigationTree(current_context), render_root)
    
    # --- non-public implementation --------------------------------------------
    
    def _node_to_dict(self, node, current_context):
        brains = []
        pc = self.context.portal_catalog 
        
        children = pc(path={ "query": node.getPath(), 'depth':1 })
        children = [ c for c in children if not c.is_default_page ] 
        children = [ c for c in children if not c.exclude_from_nav ]
        children = [ c for c in children if not c.portal_type in self.metaTypesNotToList ]
        is_node_for_current_page = '/'.join(current_context.getPhysicalPath()).startswith(node.getPath())
        return {'path': node.getPath(),
                'url': node.getURL(),
                'title': node.Title,
                'portal_type': node.portal_type,
                'excludeFromNav': node.getExcludeFromNav(), 
                'is_node_for_current_page': is_node_for_current_page,
                'children': self._nodes_to_dict(children, current_context)} 
 
    def _nodes_to_dict(self, nodes, current_context):
        return map(lambda node: self._node_to_dict(node, current_context), nodes)
    
    def getNavigationTree(self, current_context):
        if not IATFolder.providedBy(current_context):
            # if the requested folder has a default page, the current_context
            # is the default page, not the folder. For correct rendering we
            # actually need the folder.
            current_context = current_context.aq_inner.aq_parent
        root = self.getSubnavigationRoot()
        root = self.context.portal_catalog(UID=root.UID())[0]
        return self._node_to_dict(root, current_context)
 
    def _render_children(self, children, depth):
        children_html = map(lambda node: self._node_to_html(node, depth), children)
        return self._flatten_list(children_html)

    def _flatten_list(self, lists):
        final_list = list()
        for item in lists:
            final_list.extend(item)
        return final_list
    
    def _node_to_html(self, node, depth=0):
        url = node['url']
        title = node['title']
        
        node_has_children = (len(node['children']) > 0)
        is_collapsible = node['portal_type'] not in self.metaTypesNotToList and not node['excludeFromNav']
        if is_collapsible:
            additional_css_class = node['is_node_for_current_page'] and 'initiallyOpen' or ''
            selected_css = self.request.ACTUAL_URL == url and 'current-node' or ''
            html = [
                '<div class="collapsible-item %s">' % additional_css_class,
                    '<h3 class="navTreeLevel%d %s">' % (depth, selected_css),
                        '<a href="%s">%s</a> <span class="%s"/>' % (url, title, node_has_children and 'has-children' or 'no-children'),
                    '</h3>',
            ]
        else:
            html = []
        
        if node_has_children:
            html.extend(
                ['<div class="collapsible-children">'] + \
                    self._render_children(node['children'], depth+1) + \
                ['</div>']
            )
        
        if is_collapsible:
            html.append('</div>')
        return html

    def _renderSitemap(self, tree, render_root_node):
        """ HTML sitemap renderer """
        html = list()
        if render_root_node:
            html_lines = map(self._node_to_html, [tree,])
        else:
            html_lines = map(self._node_to_html, tree['children'])
        html = self._flatten_list(html_lines)

        return '\n'.join(html)
 
