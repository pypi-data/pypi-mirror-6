from tomcom.browser.public import *
from AccessControl import Unauthorized

from Products.GenericSetup.context import TarballExportContext
from export import TCJsRegistryNodeAdapter

class IJsSort(Interface):

    def export(self):
        """ """

class Browser(BrowserView):

    implements(IJsSort)

    def export(self):
        """ """
        context=self.context
        portal=context.getAdapter('portal')()
        portal_setup=context.portal_setup
        portal_javascripts=context.portal_javascripts
        tec=TarballExportContext(portal_setup)

        string_=TCJsRegistryNodeAdapter(portal_javascripts,tec)._exportBody()

        REQUEST  = context.REQUEST
        RESPONSE = REQUEST.RESPONSE
        RESPONSE.setHeader('Content-Disposition','filename="jsregistry.xml"')
        RESPONSE.setHeader('Content-Type', 'text/plain; charset=utf-8')
        RESPONSE.setHeader('Content-Length', len(string_))
        RESPONSE.write(string_)