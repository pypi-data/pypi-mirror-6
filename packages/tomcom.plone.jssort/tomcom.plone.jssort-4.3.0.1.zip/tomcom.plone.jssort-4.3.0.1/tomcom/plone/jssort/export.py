from Products.ResourceRegistries.exportimport.resourceregistry import ResourceRegistryNodeAdapter
from Products.ResourceRegistries.interfaces import IJSRegistry
from Products.CMFCore.utils import getToolByName

class TCJsRegistryNodeAdapter(ResourceRegistryNodeAdapter):
    """
    Node im- and exporter for CSSRegistry.
    """

    __used_for__ = IJSRegistry
    registry_id = 'portal_javascripts'
    resource_type = 'javascript'
    register_method = 'registerScript'
    update_method = 'updateScript'

    def _extractResourceInfo(self):
        """
        Extract the information for each of the registered resources.
        """
        fragment = self._doc.createDocumentFragment()
        registry = getToolByName(self.context, self.registry_id)
        resources = registry.getResources()
        counter=0
        for resource in resources:
            data = resource._data.copy()

            if 'cooked_expression' in data:
                del data['cooked_expression']
            if counter!=0:
                data['insert-after']=resources[counter-1]._data['id']
            child = self._doc.createElement(self.resource_type)
            for key, value in data.items():
                if type(value) == type(True) or type(value) == type(0):
                    value = str(value)
                child.setAttribute(key, value)
            fragment.appendChild(child)
            counter+=1
        return fragment