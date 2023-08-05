# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from zope.interface import implements

from AccessControl import ClassSecurityInfo, Permissions
from Acquisition import aq_base
from App.class_init import InitializeClass
from OFS import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# SilvaViews
from Products.SilvaViews.interfaces import IViewRegistry
from Products.SilvaViews.helpers import add_and_edit
from silva.core.conf.utils import getFiveViewNameFor

ViewManagementScreens = Permissions.view_management_screens

class MultiViewRegistry(SimpleItem.SimpleItem):
    """Silva Multi View Registry.
    """
    meta_type = "Silva Multi View Registry"

    implements(IViewRegistry)

    security = ClassSecurityInfo()

    manage_options = (
        {'label':'Contents', 'action':'manage_main'},
        {'label':'Security', 'action':'manage_access'},
        {'label':'Undo', 'action':'manage_UndoForm'}
      )

    security.declareProtected('View management screens', 'manage_main')
    manage_main = PageTemplateFile(
        'www/viewRegistryAssociations',
        globals(),  __name__='manage_main')

    def __init__(self, id):
        self.id = id
        self.view_types = {}
        self.trees = []

    # MANIPULATORS

    security.declareProtected(ViewManagementScreens, 'register')
    def register(self, view_type, meta_type, view_path):
        """Register a view path with the registry. Can also be used
        to change what view path is registered.
        """
        self.view_types.setdefault(view_type, {})[meta_type] = view_path
        self.view_types = self.view_types

    security.declareProtected(ViewManagementScreens, 'unregister')
    def unregister(self, view_type, meta_type):
        """Unregister view_type, meta_type
        """
        try:
            del self.view_types[view_type][meta_type]
            self.view_types = self.view_types
        except KeyError:
            # is not registered: ignore
            pass

    security.declareProtected(ViewManagementScreens, 'set_trees')
    def set_trees(self, trees):
        """Set which trees to search and in which order.
        """
        self.trees = trees

    security.declareProtected(ViewManagementScreens, 'clear')
    def clear(self):
        """Clear all view_types associations.
        """
        self.view_types = {}
        self.trees = []

    # ACCESSORS

    def get_view_types(self):
        """Get all view types, sorted.
        """
        result = self.view_types.keys()
        result.sort()
        return result

    def get_meta_types(self, view_type):
        """Get meta_types registered for view_type, sorted.
        """
        meta_types = self.view_types.get(view_type, {})
        result = meta_types.keys()
        result.sort()
        return result

    def has_view(self, view_type, meta_type, content=None):
        """Return true if system has a view of this type.
        """
        steps = self.get_view_path(view_type, meta_type, content)
        return steps is not None

    def get_view_path(self, view_type, meta_type, content=None):
        """Get view path used for view_type/meta_type combination.
        """
        settings = self.view_types.get(view_type)
        if settings is None:
            return None
        steps = settings.get(meta_type)
        if steps is None:
            if content is not None:
                alternate_meta_type = getFiveViewNameFor(content)
                steps = settings.get(alternate_meta_type)
        return steps

    def get_view(self, view_type, meta_type, content=None):
        """Get view for meta_type.
        """
        # root of all the view trees
        view_root = self.service_views
        # steps we need to take
        steps = self.get_view_path(view_type, meta_type, content)
        if steps is None:
            return None
        # start at the view root
        object = view_root
        # now search through the trees
        # FIXME: breadth first search instead?
        for tree in self.trees:
            # get the tree in the acquisition context of whatever object
            # we are in (either the views_root or in fact somewhere in
            # previous view tree)
            if not hasattr(object, tree):
                continue
            object = getattr(object, tree)
            # now try to get the view from this tree
            for step in steps:
                # we break so we move on to the next tree and start stepping
                # again
                if not hasattr(aq_base(object), step):
                    break
                # we find it so we take the next step
                object = getattr(object, step)
            else:
                # we didn't break so we found it
                return object
        # we didn't find the view in the end, so return None
        return None

    def render_preview(self, view_type, obj):
        """Render preview of object using view_registry. This calls
        the render_preview() method defined on the view in the registry.
        """
        self.REQUEST['model'] = obj
        return self.get_view(view_type,
                              obj.meta_type).render_preview()

    def render_view(self, view_type, obj):
        """Render view of object using view_registry. This calls
        the render_view() method defined on the view in the registry.
        """
        self.REQUEST['model'] = obj
        return self.get_view(view_type,
                              obj.meta_type).render_view()

    def get_method_on_view(self, view_type, obj, name):
        """Get a method on the view for the object.
        """
        return getattr(self.get_view(view_type, obj.meta_type, obj), name, None)

InitializeClass(MultiViewRegistry)


manage_addMultiViewRegistryForm = PageTemplateFile(
    "www/multiViewRegistryAdd", globals(),
    __name__='manage_addMultiViewRegistryForm')


def manage_addMultiViewRegistry(self, id, REQUEST=None):
    """Add a MultiViewRegistry."""
    object = MultiViewRegistry(id)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''

