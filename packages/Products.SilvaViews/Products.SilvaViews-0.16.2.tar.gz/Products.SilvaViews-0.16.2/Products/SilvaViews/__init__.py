# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision$

import ViewRegistry, MultiViewRegistry

hasMakeContainerFilter = True
try:
    from silva.core.conf.utils import makeZMIFilter
except:
    hasMakeContainerFilter = False
    
def initialize(context):
    if hasMakeContainerFilter:
        context.registerClass(
            ViewRegistry.ViewRegistry,
            constructors = (ViewRegistry.manage_addViewRegistryForm,
                            ViewRegistry.manage_addViewRegistry),
            icon = "www/silva_view_registry.gif",
            container_filter = makeZMIFilter(ViewRegistry.ViewRegistry)
            )

        context.registerClass(
            MultiViewRegistry.MultiViewRegistry,
            constructors = (MultiViewRegistry.manage_addMultiViewRegistryForm,
                            MultiViewRegistry.manage_addMultiViewRegistry),
            icon = "www/silva_multi_view_registry.gif",
            container_filter = makeZMIFilter(MultiViewRegistry.MultiViewRegistry)
            )
    else:
        context.registerClass(
            ViewRegistry.ViewRegistry,
            constructors = (ViewRegistry.manage_addViewRegistryForm,
                            ViewRegistry.manage_addViewRegistry),
            icon = "www/silva_view_registry.gif"
            )

        context.registerClass(
            MultiViewRegistry.MultiViewRegistry,
            constructors = (MultiViewRegistry.manage_addMultiViewRegistryForm,
                            MultiViewRegistry.manage_addMultiViewRegistry),
            icon = "www/silva_multi_view_registry.gif"
            )



