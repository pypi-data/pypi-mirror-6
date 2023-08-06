import json

from zope.component import getMultiAdapter
from collective.documentviewer.views import DocumentViewerView
from plone.dexterity.browser.view import DefaultView


class VersionViewerView(DocumentViewerView):
    pass


class JSONVersionViewerView(DocumentViewerView):
    def index(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(self.dv_data())


class DmsDocumentView(DefaultView):
    def update(self):
        super(DmsDocumentView, self).update()
        self.portal_url = getMultiAdapter((self.context, self.request),
            name="plone_portal_state").portal_url()
        self.dvstatic = "%s/++resource++dv.resources" % (
            self.portal_url)
