
from zope.interface import Interface

class IViewRegistry(Interface):
    """View registries allow associating views with meta_types.
    """

    def get_view_types():
        """Get all view types known to this registry.
        """

    def get_meta_types(view_type):
        """Get all meta_types registered for a view type.
        """

    def has_view(view_type, meta_type):
        """Return true if the registry has a view of this type for meta_type.
        """

    def get_view(view_type, meta_type):
        """Get a view for meta_type and view_type.
        """

    def render_preview(view_type, obj):
        """Render preview of object using this registry.

        This calls the render_preview method defined on the view found.
        """

    def render_view(view_type, obj):
        """Render view of the object using this registry.

        This calls the view method defined on the view found
        """

    def get_method_on_view(view_type, obj, name):
        """Return method defined on the view for the object.
        """

